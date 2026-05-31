from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import json
import yaml
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone
import uuid
import copy

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI(title="NetConfig Builder API")
api_router = APIRouter(prefix="/api")

from models import ProjectCreate, ProjectUpdate, TemplateCreate, TemplateUpdate
from validation_engine import validate_project
from config_renderer import render_config
from platform_profiles import get_platform_list, PLATFORM_FAMILIES, DEVICE_ROLES, ROLE_PLATFORM_MAP
from seed_data import get_seed_templates, get_sample_project

logger = logging.getLogger(__name__)


# --- Startup: Seed data ---
@app.on_event("startup")
async def seed_database():
    # Re-seed system templates on every startup so backend seed_data.py stays the
    # single source of truth. Only templates marked is_seed (and any legacy ones
    # matching a seed name) are replaced; user-created templates are left intact.
    templates = get_seed_templates()
    seed_names = [t["name"] for t in templates]
    await db.templates.delete_many({"$or": [{"is_seed": True}, {"name": {"$in": seed_names}}]})
    for t in templates:
        await db.templates.insert_one(t)
    logger.info(f"Seeded/updated {len(templates)} system templates")

    project_count = await db.projects.count_documents({})
    if project_count == 0:
        sample = get_sample_project()
        await db.projects.insert_one(sample)
        logger.info("Seeded sample project")


# --- Platform info ---
@api_router.get("/platforms")
async def list_platforms():
    return {
        "platforms": get_platform_list(),
        "roles": DEVICE_ROLES,
        "role_platform_map": ROLE_PLATFORM_MAP,
    }


# --- Dashboard stats ---
@api_router.get("/stats")
async def get_stats():
    project_count = await db.projects.count_documents({})
    template_count = await db.templates.count_documents({})
    draft_count = await db.projects.count_documents({"status": "draft"})
    validated_count = await db.projects.count_documents({"status": "validated"})
    generated_count = await db.projects.count_documents({"status": "generated"})

    recent_projects = await db.projects.find(
        {}, {"_id": 0, "id": 1, "name": 1, "status": 1, "device.platform_family": 1, "device.hostname": 1, "updated_at": 1}
    ).sort("updated_at", -1).limit(10).to_list(10)

    return {
        "total_projects": project_count,
        "total_templates": template_count,
        "draft_count": draft_count,
        "validated_count": validated_count,
        "generated_count": generated_count,
        "recent_projects": recent_projects,
    }


# --- Projects CRUD ---
@api_router.post("/projects")
async def create_project(data: ProjectCreate):
    project_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    doc = data.model_dump()
    doc["id"] = project_id
    doc["status"] = "draft"
    doc["created_at"] = now
    doc["updated_at"] = now
    doc["validation_results"] = []
    doc["generated_config"] = None
    doc["revisions"] = []

    await db.projects.insert_one(doc)
    doc.pop("_id", None)
    return doc


@api_router.get("/projects")
async def list_projects(status: Optional[str] = None, platform: Optional[str] = None):
    query = {}
    if status:
        query["status"] = status
    if platform:
        query["device.platform_family"] = platform

    projects = await db.projects.find(query, {"_id": 0}).sort("updated_at", -1).to_list(100)
    return projects


@api_router.get("/projects/{project_id}")
async def get_project(project_id: str):
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@api_router.put("/projects/{project_id}")
async def update_project(project_id: str, data: ProjectUpdate):
    existing = await db.projects.find_one({"id": project_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = {k: v for k, v in data.model_dump(exclude_none=True).items()}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    update_data["status"] = "draft"

    # Save revision before update
    revision_id = str(uuid.uuid4())
    revision = {
        "id": revision_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "snapshot": {k: v for k, v in existing.items() if k not in ("_id", "revisions")},
    }
    await db.projects.update_one(
        {"id": project_id},
        {"$set": update_data, "$push": {"revisions": revision}}
    )

    updated = await db.projects.find_one({"id": project_id}, {"_id": 0})
    return updated


@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    result = await db.projects.delete_one({"id": project_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"status": "deleted", "id": project_id}


# --- Validation ---
@api_router.post("/projects/{project_id}/validate")
async def validate_project_endpoint(project_id: str):
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    findings = validate_project(project)
    errors = [f for f in findings if f["severity"] == "error"]
    warnings = [f for f in findings if f["severity"] == "warning"]
    infos = [f for f in findings if f["severity"] == "info"]

    status = "validated" if not errors else "draft"
    await db.projects.update_one(
        {"id": project_id},
        {"$set": {
            "validation_results": findings,
            "status": status,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }}
    )

    return {
        "project_id": project_id,
        "status": status,
        "findings": findings,
        "summary": {
            "errors": len(errors),
            "warnings": len(warnings),
            "infos": len(infos),
            "total": len(findings),
            "can_generate": len(errors) == 0,
        }
    }


@api_router.post("/validate-input")
async def validate_input_standalone(data: ProjectCreate):
    project_dict = data.model_dump()
    findings = validate_project(project_dict)
    errors = [f for f in findings if f["severity"] == "error"]
    return {
        "findings": findings,
        "summary": {
            "errors": len(errors),
            "warnings": len([f for f in findings if f["severity"] == "warning"]),
            "infos": len([f for f in findings if f["severity"] == "info"]),
            "can_generate": len(errors) == 0,
        }
    }


# --- Config Generation ---
@api_router.post("/projects/{project_id}/generate")
async def generate_config(project_id: str):
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Run validation first
    findings = validate_project(project)
    errors = [f for f in findings if f["severity"] == "error"]

    if errors:
        return {
            "project_id": project_id,
            "status": "validation_failed",
            "message": f"Cannot generate config: {len(errors)} validation error(s) must be fixed first.",
            "findings": findings,
        }

    result = render_config(project)
    generated = {
        "clean_config": result.get("clean_config", ""),
        "annotated_config": result.get("annotated_config", ""),
        "checklist": result.get("checklist", []),
        "validation_summary": result.get("validation_summary", ""),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    await db.projects.update_one(
        {"id": project_id},
        {"$set": {
            "generated_config": generated,
            "validation_results": findings,
            "status": "generated",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }}
    )

    return {
        "project_id": project_id,
        "status": "generated",
        "config": generated,
        "findings": findings,
    }


# --- Revisions ---
@api_router.get("/projects/{project_id}/revisions")
async def get_revisions(project_id: str):
    project = await db.projects.find_one({"id": project_id}, {"_id": 0, "revisions": 1, "name": 1})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    revisions = project.get("revisions", [])
    revisions.reverse()  # newest first
    return {"project_id": project_id, "revisions": revisions}


# --- Export ---
@api_router.get("/projects/{project_id}/export/{format}")
async def export_project(project_id: str, format: str):
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if format == "json":
        export_data = {k: v for k, v in project.items() if k != "revisions"}
        return {"format": "json", "content": json.dumps(export_data, indent=2), "filename": f"{project.get('name', 'project')}.json"}
    elif format == "yaml":
        export_data = {k: v for k, v in project.items() if k != "revisions"}
        return {"format": "yaml", "content": yaml.dump(export_data, default_flow_style=False, sort_keys=False), "filename": f"{project.get('name', 'project')}.yaml"}
    elif format == "txt":
        config = project.get("generated_config", {})
        if not config:
            raise HTTPException(status_code=400, detail="No generated config. Generate config first.")
        return {"format": "txt", "content": config.get("clean_config", ""), "filename": f"{project.get('name', 'config')}.txt"}
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}. Supported: json, yaml, txt")


# --- Import ---
@api_router.post("/projects/import")
async def import_project(data: dict):
    # Accept either a raw project dict OR { format: "json"|"yaml", content: "..." }
    if isinstance(data.get("content"), str) and data.get("format") in ("json", "yaml"):
        try:
            if data["format"] == "json":
                data = json.loads(data["content"])
            else:
                data = yaml.safe_load(data["content"]) or {}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse {data.get('format', '?')}: {e}")

    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="Imported content must be an object/dict.")

    project_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    data["id"] = project_id
    data["status"] = "draft"
    data["created_at"] = now
    data["updated_at"] = now
    data["validation_results"] = []
    data["generated_config"] = None
    data["revisions"] = []
    data.pop("_id", None)

    if not data.get("name"):
        data["name"] = f"Imported Project {now[:10]}"

    await db.projects.insert_one(data)
    data.pop("_id", None)
    return data


# --- Templates CRUD ---
@api_router.get("/templates")
async def list_templates(platform: Optional[str] = None, category: Optional[str] = None):
    query = {}
    if platform:
        query["platform_family"] = platform
    if category:
        query["category"] = category
    templates = await db.templates.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    return templates


@api_router.post("/templates")
async def create_template(data: TemplateCreate):
    template_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    doc = data.model_dump()
    doc["id"] = template_id
    doc["locked"] = False
    doc["created_at"] = now
    doc["updated_at"] = now

    await db.templates.insert_one(doc)
    doc.pop("_id", None)
    return doc


@api_router.get("/templates/{template_id}")
async def get_template(template_id: str):
    template = await db.templates.find_one({"id": template_id}, {"_id": 0})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@api_router.put("/templates/{template_id}")
async def update_template(template_id: str, data: TemplateUpdate):
    existing = await db.templates.find_one({"id": template_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Template not found")
    if existing.get("locked"):
        raise HTTPException(status_code=403, detail="Template is locked and cannot be modified.")

    update_data = {k: v for k, v in data.model_dump(exclude_none=True).items()}
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()

    await db.templates.update_one({"id": template_id}, {"$set": update_data})
    updated = await db.templates.find_one({"id": template_id}, {"_id": 0})
    return updated


@api_router.delete("/templates/{template_id}")
async def delete_template(template_id: str):
    existing = await db.templates.find_one({"id": template_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Template not found")
    if existing.get("locked"):
        raise HTTPException(status_code=403, detail="Template is locked and cannot be deleted.")
    await db.templates.delete_one({"id": template_id})
    return {"status": "deleted", "id": template_id}


@api_router.post("/templates/{template_id}/duplicate")
async def duplicate_template(template_id: str):
    existing = await db.templates.find_one({"id": template_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Template not found")

    new_template = copy.deepcopy(existing)
    new_template["id"] = str(uuid.uuid4())
    new_template["name"] = f"{existing['name']} (Copy)"
    new_template["locked"] = False
    new_template["created_at"] = datetime.now(timezone.utc).isoformat()
    new_template["updated_at"] = datetime.now(timezone.utc).isoformat()

    await db.templates.insert_one(new_template)
    new_template.pop("_id", None)
    return new_template


@api_router.post("/templates/{template_id}/lock")
async def toggle_template_lock(template_id: str):
    existing = await db.templates.find_one({"id": template_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Template not found")

    new_locked = not existing.get("locked", False)
    await db.templates.update_one({"id": template_id}, {"$set": {"locked": new_locked}})
    return {"id": template_id, "locked": new_locked}


# --- Create project from template ---
@api_router.post("/projects/from-template/{template_id}")
async def create_project_from_template(template_id: str):
    template = await db.templates.find_one({"id": template_id}, {"_id": 0})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    config_data = template.get("config_data", {})
    project_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    project = copy.deepcopy(config_data)
    project["id"] = project_id
    project["name"] = f"{config_data.get('name', template['name'])} - New"
    project["status"] = "draft"
    project["created_at"] = now
    project["updated_at"] = now
    project["validation_results"] = []
    project["generated_config"] = None
    project["revisions"] = []

    await db.projects.insert_one(project)
    project.pop("_id", None)
    return project


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
