"""Backend tests for C plan: Import (JSON/YAML), DHCP relay, Export, Revisions."""
import os
import json
import requests
import pytest

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://ios-builder-30.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


def _base_project(platform="catalyst_9300", hostname="TEST-DHCP", name="TEST_DHCP_Relay"):
    return {
        "name": name,
        "device": {"role": "distribution_switch", "vendor": "cisco", "platform_family": platform,
                   "os_family": "ios_xe", "os_version": "17.9", "hostname": hostname},
        "management": {"mgmt_vlan": "10", "mgmt_ip": "10.1.1.10", "mgmt_mask": "255.255.255.0",
                       "default_gateway": "10.1.1.1", "dns_servers": ["8.8.8.8"], "domain_name": "test.local"},
        "vlans": [{"id": 10, "name": "DATA", "description": ""}],
        "interfaces": {"access_ports": [], "trunk_ports": [], "port_channels": []},
        "routing": {"svi_list": [{"vlan": 10, "ip": "10.1.1.1", "mask": "255.255.255.0", "description": ""}],
                    "static_routes": []},
        "stp": {"mode": "rapid-pvst", "priority": {}},
        "services": {"ntp_servers": ["10.1.1.5"], "syslog_servers": [], "snmp": {"version": ""},
                     "dhcp_relay": []},
        "security": {"aaa": {"enabled": True, "method": "local", "radius_servers": []},
                     "local_users": [{"username": "admin", "privilege": 15, "secret_type": "9"}],
                     "ssh": {"version": 2, "timeout": 60, "retries": 3, "rsa_bits": 2048},
                     "banner": "Authorized only", "line_vty": {"transport": "ssh", "access_class": ""}},
        "industrial": {"panel_name": "", "cabinet_name": "", "peer_role": "none"},
        "notes": ""
    }


# --- Import tests (JSON / YAML / raw dict backward compat) ---
class TestImport:
    def test_import_json_format(self, session):
        proj = _base_project(name="TEST_Import_JSON")
        payload = {"format": "json", "content": json.dumps(proj)}
        r = session.post(f"{API}/projects/import", json=payload)
        assert r.status_code == 200, r.text
        data = r.json()
        assert "id" in data
        assert data["name"] == "TEST_Import_JSON"
        assert data["device"]["platform_family"] == "catalyst_9300"
        # Verify persistence
        g = session.get(f"{API}/projects/{data['id']}")
        assert g.status_code == 200
        assert g.json()["name"] == "TEST_Import_JSON"

    def test_import_yaml_format(self, session):
        import yaml
        proj = _base_project(name="TEST_Import_YAML")
        payload = {"format": "yaml", "content": yaml.dump(proj)}
        r = session.post(f"{API}/projects/import", json=payload)
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["name"] == "TEST_Import_YAML"
        assert data["device"]["hostname"] == "TEST-DHCP"

    def test_import_raw_dict_backward_compat(self, session):
        proj = _base_project(name="TEST_Import_Raw")
        r = session.post(f"{API}/projects/import", json=proj)
        assert r.status_code == 200, r.text
        assert r.json()["name"] == "TEST_Import_Raw"

    def test_import_invalid_json_content(self, session):
        r = session.post(f"{API}/projects/import", json={"format": "json", "content": "{bad json"})
        assert r.status_code == 400


# --- DHCP relay tests (end-to-end + platform check + invalid input) ---
class TestDhcpRelay:
    def test_dhcp_relay_e2e_catalyst9300(self, session):
        proj = _base_project(name="TEST_DHCP_E2E")
        proj["services"]["dhcp_relay"] = [
            {"svi_vlan": "10", "helper_ip": "10.1.1.100"},
            {"svi_vlan": "10", "helper_ip": "10.1.1.101"},
        ]
        r = session.post(f"{API}/projects", json=proj)
        assert r.status_code == 200, r.text
        pid = r.json()["id"]

        v = session.post(f"{API}/projects/{pid}/validate")
        assert v.status_code == 200
        summary = v.json()["summary"]
        assert summary["errors"] == 0, f"Unexpected errors: {v.json()['findings']}"

        g = session.post(f"{API}/projects/{pid}/generate")
        assert g.status_code == 200
        clean = g.json().get("config", {}).get("clean_config", "")
        assert "interface Vlan10" in clean
        assert "ip helper-address 10.1.1.100" in clean
        assert "ip helper-address 10.1.1.101" in clean
        # Order check
        idx_intf = clean.index("interface Vlan10")
        idx_h1 = clean.index("ip helper-address 10.1.1.100", idx_intf)
        idx_h2 = clean.index("ip helper-address 10.1.1.101", idx_h1)
        assert idx_intf < idx_h1 < idx_h2

    def test_dhcp_relay_unsupported_ie3300(self, session):
        proj = _base_project(platform="ie3300", hostname="TEST-IE3300", name="TEST_DHCP_IE3300")
        # IE3300 is L2-only; remove SVI and use mgmt at L2
        proj["routing"]["svi_list"] = []
        proj["services"]["dhcp_relay"] = [{"svi_vlan": "10", "helper_ip": "10.1.1.100"}]
        r = session.post(f"{API}/projects", json=proj)
        assert r.status_code == 200
        pid = r.json()["id"]

        v = session.post(f"{API}/projects/{pid}/validate")
        assert v.status_code == 200
        findings = v.json()["findings"]
        dhcp_errors = [f for f in findings if f["severity"] == "error"
                       and f["field"].startswith("services.dhcp_relay")]
        assert dhcp_errors, f"Expected DHCP relay platform error, got: {findings}"

    def test_dhcp_relay_invalid_inputs(self, session):
        proj = _base_project(name="TEST_DHCP_Invalid")
        proj["services"]["dhcp_relay"] = [
            {"svi_vlan": "", "helper_ip": "10.1.1.1"},
            {"svi_vlan": "10", "helper_ip": "999.999.0.1"},
        ]
        r = session.post(f"{API}/projects", json=proj)
        assert r.status_code == 200
        pid = r.json()["id"]
        v = session.post(f"{API}/projects/{pid}/validate")
        findings = v.json()["findings"]
        vlan_err = [f for f in findings if f["field"] == "services.dhcp_relay[0].svi_vlan"
                    and f["severity"] == "error"]
        ip_err = [f for f in findings if f["field"] == "services.dhcp_relay[1].helper_ip"
                  and f["severity"] == "error"]
        assert vlan_err, f"Expected svi_vlan error: {findings}"
        assert ip_err, f"Expected helper_ip error: {findings}"


# --- Revisions tests ---
class TestRevisions:
    def test_revisions_after_put(self, session):
        proj = _base_project(name="TEST_Revisions")
        r = session.post(f"{API}/projects", json=proj)
        pid = r.json()["id"]

        # Update once
        upd = {"name": "TEST_Revisions_v2"}
        u1 = session.put(f"{API}/projects/{pid}", json=upd)
        assert u1.status_code == 200
        # Update twice
        u2 = session.put(f"{API}/projects/{pid}", json={"name": "TEST_Revisions_v3"})
        assert u2.status_code == 200

        rev = session.get(f"{API}/projects/{pid}/revisions")
        assert rev.status_code == 200
        body = rev.json()
        assert body["project_id"] == pid
        assert len(body["revisions"]) >= 2
        # newest first
        assert "snapshot" in body["revisions"][0]
        assert "timestamp" in body["revisions"][0]


# --- Export tests ---
class TestExport:
    def test_export_all_formats(self, session):
        proj = _base_project(name="TEST_Export")
        proj["services"]["dhcp_relay"] = [{"svi_vlan": "10", "helper_ip": "10.1.1.100"}]
        r = session.post(f"{API}/projects", json=proj)
        pid = r.json()["id"]

        ej = session.get(f"{API}/projects/{pid}/export/json")
        assert ej.status_code == 200
        assert ej.json()["format"] == "json"
        assert "TEST_Export" in ej.json()["content"]

        ey = session.get(f"{API}/projects/{pid}/export/yaml")
        assert ey.status_code == 200
        assert ey.json()["format"] == "yaml"
        assert "TEST_Export" in ey.json()["content"]

        # txt before generate -> 400
        et = session.get(f"{API}/projects/{pid}/export/txt")
        assert et.status_code == 400

        # generate, then txt
        session.post(f"{API}/projects/{pid}/generate")
        et2 = session.get(f"{API}/projects/{pid}/export/txt")
        assert et2.status_code == 200
        assert "hostname" in et2.json()["content"].lower()


# --- Smoke regression ---
class TestSmokeRegression:
    def test_ie3300_validate_generate_smoke(self, session):
        proj = _base_project(platform="ie3300", hostname="TEST-IE", name="TEST_IE3300_Smoke")
        proj["routing"]["svi_list"] = []  # L2 only
        r = session.post(f"{API}/projects", json=proj)
        pid = r.json()["id"]
        v = session.post(f"{API}/projects/{pid}/validate")
        assert v.status_code == 200
        # generate even with warnings (no errors expected for this trimmed proj)
        g = session.post(f"{API}/projects/{pid}/generate")
        assert g.status_code == 200
        assert g.json().get("status") in ("generated", "validation_failed")
