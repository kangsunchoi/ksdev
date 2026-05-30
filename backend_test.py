"""
Comprehensive backend API testing for Cisco NetConfig Builder
Tests all CRUD operations, validation, generation, and export functionality
"""

import requests
import sys
import json
from datetime import datetime

BASE_URL = "https://ios-builder-30.preview.emergentagent.com/api"

class APITester:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.project_id = None
        self.template_id = None
        self.errors = []

    def test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{BASE_URL}{endpoint}"
        self.tests_run += 1
        
        print(f"\n{'='*60}")
        print(f"Test {self.tests_run}: {name}")
        print(f"{'='*60}")
        print(f"Method: {method} | Endpoint: {endpoint}")
        
        try:
            if method == "GET":
                response = requests.get(url, params=params, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=30)
            elif method == "PUT":
                response = requests.put(url, json=data, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, timeout=30)
            
            print(f"Status Code: {response.status_code} (Expected: {expected_status})")
            
            success = response.status_code == expected_status
            
            if success:
                self.tests_passed += 1
                print(f"✅ PASSED")
                try:
                    resp_data = response.json()
                    print(f"Response preview: {json.dumps(resp_data, indent=2)[:500]}...")
                    return True, resp_data
                except:
                    return True, {}
            else:
                self.tests_failed += 1
                print(f"❌ FAILED")
                print(f"Response: {response.text[:500]}")
                self.errors.append({
                    "test": name,
                    "expected": expected_status,
                    "got": response.status_code,
                    "response": response.text[:200]
                })
                return False, {}
                
        except Exception as e:
            self.tests_failed += 1
            print(f"❌ FAILED - Exception: {str(e)}")
            self.errors.append({
                "test": name,
                "error": str(e)
            })
            return False, {}

    def run_all_tests(self):
        """Execute all backend API tests"""
        print("\n" + "="*60)
        print("CISCO NETCONFIG BUILDER - BACKEND API TEST SUITE")
        print("="*60)
        
        # Test 1: GET /api/stats
        print("\n\n### DASHBOARD STATS TESTS ###")
        success, data = self.test(
            "Get Dashboard Stats",
            "GET",
            "/stats",
            200
        )
        if success:
            assert "total_projects" in data, "Missing total_projects in stats"
            assert "total_templates" in data, "Missing total_templates in stats"
            assert "recent_projects" in data, "Missing recent_projects in stats"
            print(f"Stats: {data['total_projects']} projects, {data['total_templates']} templates")
        
        # Test 2: GET /api/platforms
        print("\n\n### PLATFORM TESTS ###")
        success, data = self.test(
            "Get Platform List",
            "GET",
            "/platforms",
            200
        )
        if success:
            assert "platforms" in data, "Missing platforms in response"
            assert len(data["platforms"]) == 7, f"Expected 7 platforms, got {len(data['platforms'])}"
            print(f"Platforms: {len(data['platforms'])} available")
        
        # Test 3: POST /api/projects - Create project
        print("\n\n### PROJECT CRUD TESTS ###")
        project_data = {
            "name": "Test Project - API Test",
            "device": {
                "role": "access_switch",
                "vendor": "cisco",
                "platform_family": "ie3300",
                "os_family": "ios_xe",
                "os_version": "17.9",
                "hostname": "TEST-SW-01"
            },
            "management": {
                "mgmt_vlan": "100",
                "mgmt_ip": "10.0.100.50",
                "mgmt_mask": "255.255.255.0",
                "default_gateway": "10.0.100.1",
                "dns_servers": ["10.0.1.10"],
                "domain_name": "test.local"
            },
            "vlans": [
                {"id": 10, "name": "DATA", "description": "Data VLAN"},
                {"id": 20, "name": "VOICE", "description": "Voice VLAN"}
            ],
            "interfaces": {
                "access_ports": [
                    {"interface": "GigabitEthernet1/0/1", "vlan": "10", "description": "Test Port", "mode": "access"}
                ],
                "trunk_ports": [
                    {"interface": "GigabitEthernet1/0/25", "allowed_vlans": "10,20", "native_vlan": "1", "description": "Uplink"}
                ],
                "port_channels": []
            },
            "routing": {"svi_list": [], "static_routes": []},
            "stp": {"mode": "rapid-pvst", "priority": {}},
            "services": {
                "ntp_servers": ["10.0.1.10"],
                "syslog_servers": ["10.0.1.20"],
                "snmp": {"version": "v2c", "community": "public"},
                "dhcp_relay": []
            },
            "security": {
                "aaa": {"enabled": True, "method": "local", "radius_servers": []},
                "local_users": [{"username": "admin", "privilege": 15, "secret_type": "9"}],
                "ssh": {"version": 2, "timeout": 60, "retries": 3, "rsa_bits": 2048},
                "banner": "Test Banner",
                "line_vty": {"transport": "ssh", "access_class": ""}
            },
            "industrial": {
                "panel_name": "Test Panel",
                "cabinet_name": "Test Cabinet"
            },
            "notes": "Test project for API validation"
        }
        
        success, data = self.test(
            "Create Project",
            "POST",
            "/projects",
            200,
            data=project_data
        )
        if success:
            self.project_id = data.get("id")
            assert self.project_id, "No project ID returned"
            assert data.get("status") == "draft", "Project should be in draft status"
            print(f"Created project ID: {self.project_id}")
        
        # Test 4: GET /api/projects/{id}
        if self.project_id:
            success, data = self.test(
                "Get Project by ID",
                "GET",
                f"/projects/{self.project_id}",
                200
            )
            if success:
                assert data.get("id") == self.project_id, "Project ID mismatch"
                assert data.get("name") == "Test Project - API Test", "Project name mismatch"
        
        # Test 5: GET /api/projects (list)
        success, data = self.test(
            "List All Projects",
            "GET",
            "/projects",
            200
        )
        if success:
            assert isinstance(data, list), "Projects should be a list"
            print(f"Total projects in system: {len(data)}")
        
        # Test 6: POST /api/projects/{id}/validate
        print("\n\n### VALIDATION TESTS ###")
        if self.project_id:
            success, data = self.test(
                "Validate Project",
                "POST",
                f"/projects/{self.project_id}/validate",
                200
            )
            if success:
                assert "findings" in data, "Missing findings in validation response"
                assert "summary" in data, "Missing summary in validation response"
                summary = data.get("summary", {})
                print(f"Validation: {summary.get('errors', 0)} errors, {summary.get('warnings', 0)} warnings, {summary.get('infos', 0)} infos")
                print(f"Can generate: {summary.get('can_generate', False)}")
        
        # Test 7: POST /api/projects/{id}/generate
        print("\n\n### CONFIG GENERATION TESTS ###")
        if self.project_id:
            success, data = self.test(
                "Generate Config",
                "POST",
                f"/projects/{self.project_id}/generate",
                200
            )
            if success:
                assert "config" in data or "status" in data, "Missing config or status in response"
                if data.get("status") == "generated":
                    config = data.get("config", {})
                    assert "clean_config" in config, "Missing clean_config"
                    assert "annotated_config" in config, "Missing annotated_config"
                    assert "checklist" in config, "Missing checklist"
                    print(f"Config generated successfully")
                    print(f"Clean config length: {len(config.get('clean_config', ''))} chars")
                    print(f"Checklist items: {len(config.get('checklist', []))}")
                    
                    # Verify IOS-XE commands are present
                    clean = config.get("clean_config", "")
                    assert "hostname TEST-SW-01" in clean, "Hostname command missing"
                    assert "vlan 10" in clean, "VLAN 10 missing"
                    assert "vlan 20" in clean, "VLAN 20 missing"
                    assert "interface GigabitEthernet1/0/1" in clean, "Interface config missing"
                    print("✓ Config contains expected IOS-XE commands")
                else:
                    print(f"Generation status: {data.get('status')}")
                    if data.get("message"):
                        print(f"Message: {data.get('message')}")
        
        # Test 8: GET /api/projects/{id}/export/json
        print("\n\n### EXPORT TESTS ###")
        if self.project_id:
            success, data = self.test(
                "Export Project as JSON",
                "GET",
                f"/projects/{self.project_id}/export/json",
                200
            )
            if success:
                assert "content" in data, "Missing content in export"
                assert "filename" in data, "Missing filename in export"
                print(f"Export filename: {data.get('filename')}")
        
        # Test 9: GET /api/projects/{id}/export/txt
        if self.project_id:
            success, data = self.test(
                "Export Config as TXT",
                "GET",
                f"/projects/{self.project_id}/export/txt",
                200
            )
            if success:
                assert "content" in data, "Missing content in export"
                content = data.get("content", "")
                print(f"TXT export length: {len(content)} chars")
        
        # Test 10: GET /api/projects/{id}/export/yaml
        if self.project_id:
            success, data = self.test(
                "Export Project as YAML",
                "GET",
                f"/projects/{self.project_id}/export/yaml",
                200
            )
            if success:
                assert "content" in data, "Missing content in export"
        
        # Test 11: PUT /api/projects/{id} - Update project
        if self.project_id:
            update_data = {
                "name": "Test Project - UPDATED",
                "notes": "Updated via API test"
            }
            success, data = self.test(
                "Update Project",
                "PUT",
                f"/projects/{self.project_id}",
                200,
                data=update_data
            )
            if success:
                assert data.get("name") == "Test Project - UPDATED", "Name not updated"
        
        # Test 12: GET /api/templates
        print("\n\n### TEMPLATE TESTS ###")
        success, data = self.test(
            "List Templates",
            "GET",
            "/templates",
            200
        )
        if success:
            assert isinstance(data, list), "Templates should be a list"
            assert len(data) >= 3, f"Expected at least 3 seed templates, got {len(data)}"
            print(f"Templates found: {len(data)}")
            if len(data) > 0:
                self.template_id = data[0].get("id")
                print(f"Using template ID: {self.template_id} ({data[0].get('name')})")
        
        # Test 13: POST /api/templates/{id}/duplicate
        if self.template_id:
            success, data = self.test(
                "Duplicate Template",
                "POST",
                f"/templates/{self.template_id}/duplicate",
                200
            )
            if success:
                assert data.get("id") != self.template_id, "Duplicate should have different ID"
                assert "(Copy)" in data.get("name", ""), "Duplicate name should contain (Copy)"
                print(f"Duplicated template: {data.get('name')}")
        
        # Test 14: POST /api/templates/{id}/lock
        if self.template_id:
            success, data = self.test(
                "Toggle Template Lock",
                "POST",
                f"/templates/{self.template_id}/lock",
                200
            )
            if success:
                assert "locked" in data, "Missing locked status"
                print(f"Template locked: {data.get('locked')}")
        
        # Test 15: POST /api/projects/from-template/{id}
        if self.template_id:
            success, data = self.test(
                "Create Project from Template",
                "POST",
                f"/projects/from-template/{self.template_id}",
                200
            )
            if success:
                assert "id" in data, "Missing project ID"
                assert data.get("status") == "draft", "New project should be draft"
                print(f"Created project from template: {data.get('name')}")
        
        # Test 16: GET /api/projects/{id}/revisions
        if self.project_id:
            success, data = self.test(
                "Get Project Revisions",
                "GET",
                f"/projects/{self.project_id}/revisions",
                200
            )
            if success:
                assert "revisions" in data, "Missing revisions"
                print(f"Revisions: {len(data.get('revisions', []))}")
        
        # Test 17: DELETE /api/projects/{id} - Cleanup
        print("\n\n### CLEANUP TESTS ###")
        if self.project_id:
            success, data = self.test(
                "Delete Project",
                "DELETE",
                f"/projects/{self.project_id}",
                200
            )
            if success:
                assert data.get("status") == "deleted", "Delete status incorrect"
                print(f"Deleted project: {self.project_id}")
        
        # Print summary
        print("\n\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed} ✅")
        print(f"Failed: {self.tests_failed} ❌")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.errors:
            print("\n" + "="*60)
            print("FAILED TESTS DETAILS")
            print("="*60)
            for err in self.errors:
                print(f"\n❌ {err.get('test')}")
                if 'expected' in err:
                    print(f"   Expected: {err['expected']}, Got: {err['got']}")
                if 'error' in err:
                    print(f"   Error: {err['error']}")
                if 'response' in err:
                    print(f"   Response: {err['response']}")
        
        return self.tests_failed == 0


def main():
    tester = APITester()
    success = tester.run_all_tests()
    
    print("\n" + "="*60)
    if success:
        print("✅ ALL BACKEND TESTS PASSED")
        print("="*60)
        return 0
    else:
        print("❌ SOME BACKEND TESTS FAILED")
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
