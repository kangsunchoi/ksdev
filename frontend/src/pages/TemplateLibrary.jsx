import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import {
  Copy, Lock, Unlock, Trash2, Plus, Server, RefreshCw, FilePlus2
} from "lucide-react";

const platformLabels = {
  ie3300: "IE3300", ie3400: "IE3400", ie3100: "IE3100", ie9320: "IE9320",
  catalyst_9200: "Cat9200", catalyst_9300: "Cat9300", catalyst_9500: "Cat9500",
  wlc_9800: "WLC9800", c1200: "C1200",
};

const catLabels = {
  access_switch: "Access", distribution_switch: "Distribution", core_switch: "Core",
  industrial_access: "Ind. Access", industrial_distribution: "Ind. Dist.", wlc: "WLC",
};

export default function TemplateLibrary() {
  const navigate = useNavigate();
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");

  const fetchTemplates = useCallback(async () => {
    try {
      setLoading(true);
      const params = filter !== "all" ? { platform: filter } : {};
      const res = await api.listTemplates(params);
      setTemplates(res.data);
    } catch {
      toast.error("Failed to load templates");
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => { fetchTemplates(); }, [fetchTemplates]);

  const handleDuplicate = async (id) => {
    try {
      await api.duplicateTemplate(id);
      toast.success("Template duplicated");
      fetchTemplates();
    } catch (e) {
      toast.error("Duplicate failed: " + (e.response?.data?.detail || e.message));
    }
  };

  const handleToggleLock = async (id) => {
    try {
      const res = await api.toggleTemplateLock(id);
      toast.success(res.data.locked ? "Template locked" : "Template unlocked");
      fetchTemplates();
    } catch (e) {
      toast.error("Lock toggle failed");
    }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Delete template "${name}"?`)) return;
    try {
      await api.deleteTemplate(id);
      toast.success("Template deleted");
      fetchTemplates();
    } catch (e) {
      toast.error("Delete failed: " + (e.response?.data?.detail || e.message));
    }
  };

  const handleCreateProject = async (id) => {
    try {
      const res = await api.createFromTemplate(id);
      toast.success("Project created from template");
      navigate(`/projects/${res.data.id}/edit`);
    } catch (e) {
      toast.error("Failed to create project from template");
    }
  };

  return (
    <div className="p-6 space-y-6" data-testid="template-library">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">Template Library</h1>
          <p className="text-sm text-zinc-500 mt-0.5">Reusable configuration templates by platform</p>
        </div>
        <div className="flex gap-2 items-center">
          <Select value={filter} onValueChange={setFilter}>
            <SelectTrigger className="w-40 h-8 text-xs" data-testid="filter-platform">
              <SelectValue placeholder="All Platforms" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Platforms</SelectItem>
              <SelectItem value="ie3300">IE3300</SelectItem>
              <SelectItem value="ie3400">IE3400</SelectItem>
              <SelectItem value="ie9320">IE9320</SelectItem>
              <SelectItem value="catalyst_9200">Catalyst 9200</SelectItem>
              <SelectItem value="catalyst_9300">Catalyst 9300</SelectItem>
              <SelectItem value="catalyst_9500">Catalyst 9500</SelectItem>
              <SelectItem value="wlc_9800">WLC 9800</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" size="sm" className="h-8 text-xs" onClick={fetchTemplates} data-testid="refresh-templates-btn">
            <RefreshCw className="w-3.5 h-3.5" />
          </Button>
        </div>
      </div>

      <TemplateContent
        loading={loading}
        templates={templates}
        onCreateProject={handleCreateProject}
        onDuplicate={handleDuplicate}
        onToggleLock={handleToggleLock}
        onDelete={handleDelete}
      />
    </div>
  );
}

function TemplateContent({ loading, templates, onCreateProject, onDuplicate, onToggleLock, onDelete }) {
  if (loading) {
    return <div className="text-sm text-zinc-500 py-8">Loading templates...</div>;
  }

  if (templates.length === 0) {
    return (
      <div className="text-center py-12 border border-dashed border-border rounded-sm">
        <Server className="w-8 h-8 text-zinc-600 mx-auto mb-3" />
        <div className="text-sm text-zinc-500">No templates found.</div>
        <div className="text-xs text-zinc-600 mt-1">Templates are seeded on first load. Try refreshing.</div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
      {templates.map((t) => (
        <TemplateCard
          key={t.id}
          template={t}
          onCreateProject={onCreateProject}
          onDuplicate={onDuplicate}
          onToggleLock={onToggleLock}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}

function TemplateCard({ template: t, onCreateProject, onDuplicate, onToggleLock, onDelete }) {
  return (
    <div className="border border-border rounded-sm bg-card p-4 space-y-3" data-testid={`template-card-${t.id}`}>
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-medium text-zinc-200 truncate">{t.name}</h3>
            {t.locked && <Lock className="w-3 h-3 text-amber-500 shrink-0" />}
          </div>
          <p className="text-xs text-zinc-500 mt-1 line-clamp-2">{t.description}</p>
        </div>
      </div>

      <div className="flex flex-wrap gap-1.5">
        <Badge variant="secondary" className="text-[10px] px-1.5 py-0 bg-zinc-800 text-zinc-400">
          {platformLabels[t.platform_family] || t.platform_family}
        </Badge>
        <Badge variant="secondary" className="text-[10px] px-1.5 py-0 bg-zinc-800 text-zinc-400">
          IOS-XE {t.os_version}
        </Badge>
        {t.category && (
          <Badge variant="secondary" className="text-[10px] px-1.5 py-0 bg-zinc-800 text-zinc-400">
            {catLabels[t.category] || t.category}
          </Badge>
        )}
        {(t.tags || []).slice(0, 2).map(tag => (
          <Badge key={tag} variant="outline" className="text-[10px] px-1.5 py-0 text-zinc-500">
            {tag}
          </Badge>
        ))}
      </div>

      <div className="flex gap-1.5 pt-1 border-t border-border">
        <Button variant="outline" size="sm" className="h-7 text-xs flex-1" onClick={() => onCreateProject(t.id)} data-testid={`use-template-${t.id}`}>
          <FilePlus2 className="w-3 h-3 mr-1" /> Use
        </Button>
        <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-zinc-500" onClick={() => onDuplicate(t.id)} title="Duplicate">
          <Copy className="w-3 h-3" />
        </Button>
        <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-zinc-500" onClick={() => onToggleLock(t.id)} title={t.locked ? "Unlock" : "Lock"}>
          {t.locked ? <Unlock className="w-3 h-3" /> : <Lock className="w-3 h-3" />}
        </Button>
        {!t.locked && (
          <Button variant="ghost" size="sm" className="h-7 w-7 p-0 text-zinc-500 hover:text-red-400" onClick={() => onDelete(t.id, t.name)} title="Delete">
            <Trash2 className="w-3 h-3" />
          </Button>
        )}
      </div>
    </div>
  );
}
