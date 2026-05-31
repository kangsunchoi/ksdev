"""
Seed data: pre-loaded templates and sample projects for demo.
"""
import uuid
from datetime import datetime, timezone


def get_seed_templates():
    return [
        _ie3300_access_template(),
        _ie3400_access_template(),
        _ie3100_access_template(),
        _ie9320_distribution_template(),
        _catalyst_9300_distribution_template(),
        _c1200_access_template(),
        _wlc_9800_basic_template(),
    ]


def _ie3300_access_template():
    return {
            "id": str(uuid.uuid4()),
            "name": "IE3300 Access Switch Base Config",
            "description": "Standard base configuration for Cisco IE3300 industrial access switch. L2 only with management VLAN, standard VLANs, access/trunk ports, NTP, syslog, and security hardening.",
            "platform_family": "ie3300",
            "os_version": "17.15",
            "category": "access_switch",
            "tags": ["industrial", "ie3300", "ios-xe-17", "base-config", "l2"],
            "locked": False,
            "is_seed": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "config_data": {
                "name": "IE3300 Access Template",
                "device": {
                    "role": "industrial_access",
                    "vendor": "cisco",
                    "platform_family": "ie3300",
                    "os_family": "ios_xe",
                    "os_version": "17.15",
                    "hostname": "IE-ACCESS-01",
                },
                "management": {
                    "mgmt_vlan": "100",
                    "mgmt_ip": "10.0.100.10",
                    "mgmt_mask": "255.255.255.0",
                    "default_gateway": "10.0.100.1",
                    "dns_servers": ["10.0.1.10"],
                    "domain_name": "ot.local",
                },
                "vlans": [
                    {"id": 10, "name": "OT-DATA", "description": "OT device data traffic"},
                    {"id": 20, "name": "OT-MGMT", "description": "OT management traffic"},
                    {"id": 100, "name": "SWITCH-MGMT", "description": "Switch management"},
                ],
                "interfaces": {
                    "access_ports": [
                        {"interface": "GigabitEthernet1/0/1", "vlan": "10", "description": "PLC-01", "mode": "access"},
                        {"interface": "GigabitEthernet1/0/2", "vlan": "10", "description": "HMI-01", "mode": "access"},
                        {"interface": "GigabitEthernet1/0/3", "vlan": "20", "description": "SCADA-RTU-01", "mode": "access"},
                    ],
                    "trunk_ports": [
                        {"interface": "GigabitEthernet1/0/25", "allowed_vlans": "10,20,100", "native_vlan": "1", "description": "Uplink-to-Distribution"},
                    ],
                    "port_channels": [],
                },
                "routing": {"svi_list": [], "static_routes": []},
                "stp": {"mode": "rapid-pvst", "priority": {}},
                "services": {
                    "ntp_servers": ["10.0.1.10"],
                    "syslog_servers": ["10.0.1.20"],
                    "snmp": {"version": "v2c", "community": "OT-RO-COMM", "v3_user": "", "v3_auth_protocol": "", "v3_auth_password": "", "v3_priv_protocol": "", "v3_priv_password": ""},
                    "dhcp_relay": [],
                },
                "security": {
                    "aaa": {"enabled": True, "method": "local", "radius_servers": []},
                    "local_users": [{"username": "otadmin", "privilege": 15, "secret_type": "9"}],
                    "ssh": {"version": 2, "timeout": 60, "retries": 3, "rsa_bits": 2048},
                    "banner": "AUTHORIZED ACCESS ONLY. All access is logged and monitored.",
                    "line_vty": {"transport": "ssh", "access_class": ""},
                },
                "industrial": {
                    "panel_name": "Panel-A1",
                    "cabinet_name": "MCC-01",
                    "peer_role": "plc",
                    "uplink_role": "distribution",
                    "ring_link_role": "",
                    "multicast_relevance": "low",
                    "industrial_notes": "Floor-level access switch near MCC panel",
                },
                "notes": "",
            },
    }


def _catalyst_9300_distribution_template():
    return {
            "id": str(uuid.uuid4()),
            "name": "Catalyst 9300 L3 Distribution Switch",
            "description": "Standard L3 distribution switch template for Catalyst 9300 with inter-VLAN routing, SVIs, HSRP-ready, NTP, syslog, SNMPv3, and full security hardening.",
            "platform_family": "catalyst_9300",
            "os_version": "17.15",
            "category": "distribution_switch",
            "tags": ["campus", "catalyst-9300", "ios-xe-17", "l3", "distribution"],
            "locked": False,
            "is_seed": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "config_data": {
                "name": "Cat9300 Distribution Template",
                "device": {
                    "role": "distribution_switch",
                    "vendor": "cisco",
                    "platform_family": "catalyst_9300",
                    "os_family": "ios_xe",
                    "os_version": "17.15",
                    "hostname": "DIST-SW-01",
                },
                "management": {
                    "mgmt_vlan": "100",
                    "mgmt_ip": "10.1.100.1",
                    "mgmt_mask": "255.255.255.0",
                    "default_gateway": "10.1.100.254",
                    "dns_servers": ["10.1.1.10", "10.1.1.11"],
                    "domain_name": "corp.local",
                },
                "vlans": [
                    {"id": 10, "name": "DATA", "description": "User data VLAN"},
                    {"id": 20, "name": "VOICE", "description": "VoIP VLAN"},
                    {"id": 30, "name": "WIRELESS", "description": "Wireless client VLAN"},
                    {"id": 100, "name": "MGMT", "description": "Management VLAN"},
                    {"id": 999, "name": "NATIVE", "description": "Native VLAN for trunks"},
                ],
                "interfaces": {
                    "access_ports": [],
                    "trunk_ports": [
                        {"interface": "GigabitEthernet1/0/1", "allowed_vlans": "10,20,30,100", "native_vlan": "999", "description": "Downlink-Access-SW-01"},
                        {"interface": "GigabitEthernet1/0/2", "allowed_vlans": "10,20,30,100", "native_vlan": "999", "description": "Downlink-Access-SW-02"},
                    ],
                    "port_channels": [
                        {"id": 1, "members": ["TenGigabitEthernet1/0/1", "TenGigabitEthernet1/0/2"], "mode": "trunk", "protocol": "lacp", "allowed_vlans": "10,20,30,100,999", "description": "Uplink-to-Core"},
                    ],
                },
                "routing": {
                    "svi_list": [
                        {"vlan": 10, "ip": "10.1.10.1", "mask": "255.255.255.0", "description": "Data Gateway"},
                        {"vlan": 20, "ip": "10.1.20.1", "mask": "255.255.255.0", "description": "Voice Gateway"},
                        {"vlan": 30, "ip": "10.1.30.1", "mask": "255.255.255.0", "description": "Wireless Gateway"},
                    ],
                    "static_routes": [
                        {"network": "0.0.0.0", "mask": "0.0.0.0", "next_hop": "10.1.100.254"},
                    ],
                },
                "stp": {"mode": "rapid-pvst", "priority": {"10": "4096", "20": "4096", "30": "4096"}},
                "services": {
                    "ntp_servers": ["10.1.1.10"],
                    "syslog_servers": ["10.1.1.20"],
                    "snmp": {"version": "v3", "community": "", "v3_user": "snmpmon", "v3_auth_protocol": "sha", "v3_auth_password": "<REPLACE>", "v3_priv_protocol": "aes128", "v3_priv_password": "<REPLACE>"},
                    "dhcp_relay": [],
                },
                "security": {
                    "aaa": {"enabled": True, "method": "local", "radius_servers": []},
                    "local_users": [{"username": "netadmin", "privilege": 15, "secret_type": "9"}],
                    "ssh": {"version": 2, "timeout": 60, "retries": 3, "rsa_bits": 4096},
                    "banner": "AUTHORIZED ACCESS ONLY. Unauthorized access is prohibited and will be prosecuted.",
                    "line_vty": {"transport": "ssh", "access_class": ""},
                },
                "industrial": {},
                "notes": "Standard distribution switch template. Adjust SVI IPs and VLAN list per site.",
            },
    }


def _wlc_9800_basic_template():
    return {
            "id": str(uuid.uuid4()),
            "name": "WLC 9800 Basic SSID/VLAN Mapping",
            "description": "Basic WLC 9800 management template. WLAN/SSID configuration is not yet fully supported - this template provides management baseline only.",
            "platform_family": "wlc_9800",
            "os_version": "17.15",
            "category": "wlc",
            "tags": ["wireless", "wlc-9800", "ios-xe-17", "baseline"],
            "locked": False,
            "is_seed": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "config_data": {
                "name": "WLC 9800 Basic Template",
                "device": {
                    "role": "wlc",
                    "vendor": "cisco",
                    "platform_family": "wlc_9800",
                    "os_family": "ios_xe",
                    "os_version": "17.15",
                    "hostname": "WLC-01",
                },
                "management": {
                    "mgmt_vlan": "100",
                    "mgmt_ip": "10.1.100.50",
                    "mgmt_mask": "255.255.255.0",
                    "default_gateway": "10.1.100.1",
                    "dns_servers": ["10.1.1.10"],
                    "domain_name": "corp.local",
                },
                "vlans": [],
                "interfaces": {"access_ports": [], "trunk_ports": [], "port_channels": []},
                "routing": {"svi_list": [], "static_routes": []},
                "stp": {"mode": "rapid-pvst", "priority": {}},
                "services": {
                    "ntp_servers": ["10.1.1.10"],
                    "syslog_servers": ["10.1.1.20"],
                    "snmp": {"version": "v2c", "community": "WLC-RO", "v3_user": "", "v3_auth_protocol": "", "v3_auth_password": "", "v3_priv_protocol": "", "v3_priv_password": ""},
                    "dhcp_relay": [],
                },
                "security": {
                    "aaa": {"enabled": True, "method": "local", "radius_servers": []},
                    "local_users": [{"username": "wlcadmin", "privilege": 15, "secret_type": "9"}],
                    "ssh": {"version": 2, "timeout": 60, "retries": 3, "rsa_bits": 2048},
                    "banner": "AUTHORIZED ACCESS ONLY.",
                    "line_vty": {"transport": "ssh", "access_class": ""},
                },
                "industrial": {},
                "notes": "WLC config generation is limited. WLAN/SSID profiles must be configured manually.",
            },
    }


def get_sample_project():
    return {
        "id": str(uuid.uuid4()),
        "name": "Factory Floor IE3300 - Line A",
        "status": "draft",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "device": {
            "role": "industrial_access",
            "vendor": "cisco",
            "platform_family": "ie3300",
            "os_family": "ios_xe",
            "os_version": "17.15",
            "hostname": "IE-LINEA-01",
        },
        "management": {
            "mgmt_vlan": "100",
            "mgmt_ip": "10.100.1.10",
            "mgmt_mask": "255.255.255.0",
            "default_gateway": "10.100.1.1",
            "dns_servers": ["10.0.1.10"],
            "domain_name": "factory.local",
        },
        "vlans": [
            {"id": 10, "name": "PLC-NET", "description": "PLC communications"},
            {"id": 20, "name": "HMI-NET", "description": "HMI operator stations"},
            {"id": 100, "name": "MGMT", "description": "Switch management"},
        ],
        "interfaces": {
            "access_ports": [
                {"interface": "GigabitEthernet1/0/1", "vlan": "10", "description": "PLC-AB-01", "mode": "access"},
                {"interface": "GigabitEthernet1/0/2", "vlan": "10", "description": "PLC-AB-02", "mode": "access"},
                {"interface": "GigabitEthernet1/0/3", "vlan": "20", "description": "HMI-OP-01", "mode": "access"},
            ],
            "trunk_ports": [
                {"interface": "GigabitEthernet1/0/25", "allowed_vlans": "10,20,100", "native_vlan": "1", "description": "Uplink-to-Dist"},
            ],
            "port_channels": [],
        },
        "routing": {"svi_list": [], "static_routes": []},
        "stp": {"mode": "rapid-pvst", "priority": {}},
        "services": {
            "ntp_servers": ["10.0.1.10"],
            "syslog_servers": ["10.0.1.20"],
            "snmp": {"version": "v2c", "community": "FACTORY-RO", "v3_user": "", "v3_auth_protocol": "", "v3_auth_password": "", "v3_priv_protocol": "", "v3_priv_password": ""},
            "dhcp_relay": [],
        },
        "security": {
            "aaa": {"enabled": True, "method": "local", "radius_servers": []},
            "local_users": [{"username": "otadmin", "privilege": 15, "secret_type": "9"}],
            "ssh": {"version": 2, "timeout": 60, "retries": 3, "rsa_bits": 2048},
            "banner": "AUTHORIZED ACCESS ONLY. OT NETWORK - ALL ACTIVITY MONITORED.",
            "line_vty": {"transport": "ssh", "access_class": ""},
        },
        "industrial": {
            "panel_name": "Panel-A1",
            "cabinet_name": "MCC-LineA",
            "peer_role": "plc",
            "uplink_role": "distribution",
            "ring_link_role": "",
            "multicast_relevance": "low",
            "industrial_notes": "Production Line A access switch, near MCC panel",
        },
        "notes": "Sample project for Factory Floor Line A",
        "validation_results": [],
        "generated_config": None,
        "revisions": [],
    }


def _ie3400_access_template():
    return {
        "id": str(uuid.uuid4()),
        "name": "IE3400 Access Switch Base Config",
        "description": "Base config for Cisco IE3400 rugged industrial L2/L3 access switch. Management VLAN, OT VLANs, access/trunk ports, NTP, syslog, SNMP, security hardening. Avoid IOS-XE 17.9.4/17.9.5 (FN74245); 17.15 recommended.",
        "platform_family": "ie3400",
        "os_version": "17.15",
        "category": "industrial_access",
        "tags": ["industrial", "ie3400", "ios-xe-17", "base-config", "l2-l3"],
        "locked": False,
        "is_seed": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "config_data": {
            "name": "IE3400 Access Template",
            "device": {"role": "industrial_access", "vendor": "cisco", "platform_family": "ie3400", "os_family": "ios_xe", "os_version": "17.15", "hostname": "IE3400-ACCESS-01"},
            "management": {"mgmt_vlan": "100", "mgmt_ip": "10.0.100.11", "mgmt_mask": "255.255.255.0", "default_gateway": "10.0.100.1", "dns_servers": ["10.0.1.10"], "domain_name": "ot.local"},
            "vlans": [
                {"id": 10, "name": "OT-DATA", "description": "OT device data"},
                {"id": 20, "name": "OT-CTRL", "description": "OT control traffic"},
                {"id": 100, "name": "SWITCH-MGMT", "description": "Switch management"},
            ],
            "interfaces": {
                "access_ports": [
                    {"interface": "GigabitEthernet1/0/1", "vlan": "10", "description": "PLC-01", "mode": "access"},
                    {"interface": "GigabitEthernet1/0/2", "vlan": "10", "description": "HMI-01", "mode": "access"},
                    {"interface": "GigabitEthernet1/0/3", "vlan": "20", "description": "RTU-01", "mode": "access"},
                ],
                "trunk_ports": [
                    {"interface": "GigabitEthernet1/0/25", "allowed_vlans": "10,20,100", "native_vlan": "1", "description": "Uplink-to-Distribution"},
                ],
                "port_channels": [],
            },
            "routing": {"svi_list": [], "static_routes": []},
            "stp": {"mode": "rapid-pvst", "priority": {}},
            "services": {
                "ntp_servers": ["10.0.1.10"], "syslog_servers": ["10.0.1.20"],
                "snmp": {"version": "v2c", "community": "OT-RO-COMM", "v3_user": "", "v3_auth_protocol": "", "v3_auth_password": "", "v3_priv_protocol": "", "v3_priv_password": ""},
                "dhcp_relay": [],
            },
            "security": {
                "aaa": {"enabled": True, "method": "local", "radius_servers": []},
                "local_users": [{"username": "otadmin", "privilege": 15, "secret_type": "9"}],
                "ssh": {"version": 2, "timeout": 60, "retries": 3, "rsa_bits": 2048},
                "banner": "AUTHORIZED ACCESS ONLY. All access is logged and monitored.",
                "line_vty": {"transport": "ssh", "access_class": ""},
            },
            "industrial": {"panel_name": "Panel-B1", "cabinet_name": "MCC-02", "peer_role": "plc", "uplink_role": "distribution", "ring_link_role": "", "multicast_relevance": "low", "industrial_notes": "IE3400 access switch"},
            "notes": "",
        },
    }


def _ie3100_access_template():
    return {
        "id": str(uuid.uuid4()),
        "name": "IE3100 Access Switch Base Config",
        "description": "Base config for Cisco IE3100 compact rugged industrial L2/L3 access switch. Newer hardware (IOS-XE 17.14+). Management VLAN, OT VLANs, access/trunk ports, NTP, syslog, SNMP, security hardening.",
        "platform_family": "ie3100",
        "os_version": "17.15",
        "category": "industrial_access",
        "tags": ["industrial", "ie3100", "ios-xe-17", "base-config", "compact"],
        "locked": False,
        "is_seed": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "config_data": {
            "name": "IE3100 Access Template",
            "device": {"role": "industrial_access", "vendor": "cisco", "platform_family": "ie3100", "os_family": "ios_xe", "os_version": "17.15", "hostname": "IE3100-ACCESS-01"},
            "management": {"mgmt_vlan": "100", "mgmt_ip": "10.0.100.12", "mgmt_mask": "255.255.255.0", "default_gateway": "10.0.100.1", "dns_servers": ["10.0.1.10"], "domain_name": "ot.local"},
            "vlans": [
                {"id": 10, "name": "OT-DATA", "description": "OT device data"},
                {"id": 100, "name": "SWITCH-MGMT", "description": "Switch management"},
            ],
            "interfaces": {
                "access_ports": [
                    {"interface": "GigabitEthernet1/0/1", "vlan": "10", "description": "Sensor-01", "mode": "access"},
                    {"interface": "GigabitEthernet1/0/2", "vlan": "10", "description": "Sensor-02", "mode": "access"},
                ],
                "trunk_ports": [
                    {"interface": "GigabitEthernet1/0/9", "allowed_vlans": "10,100", "native_vlan": "1", "description": "Uplink"},
                ],
                "port_channels": [],
            },
            "routing": {"svi_list": [], "static_routes": []},
            "stp": {"mode": "rapid-pvst", "priority": {}},
            "services": {
                "ntp_servers": ["10.0.1.10"], "syslog_servers": ["10.0.1.20"],
                "snmp": {"version": "v2c", "community": "OT-RO-COMM", "v3_user": "", "v3_auth_protocol": "", "v3_auth_password": "", "v3_priv_protocol": "", "v3_priv_password": ""},
                "dhcp_relay": [],
            },
            "security": {
                "aaa": {"enabled": True, "method": "local", "radius_servers": []},
                "local_users": [{"username": "otadmin", "privilege": 15, "secret_type": "9"}],
                "ssh": {"version": 2, "timeout": 60, "retries": 3, "rsa_bits": 2048},
                "banner": "AUTHORIZED ACCESS ONLY. All access is logged and monitored.",
                "line_vty": {"transport": "ssh", "access_class": ""},
            },
            "industrial": {"panel_name": "Panel-C1", "cabinet_name": "JB-03", "peer_role": "sensor", "uplink_role": "access", "ring_link_role": "", "multicast_relevance": "low", "industrial_notes": "IE3100 compact access"},
            "notes": "",
        },
    }


def _ie9320_distribution_template():
    return {
        "id": str(uuid.uuid4()),
        "name": "IE9320 Industrial Distribution Switch",
        "description": "L3 distribution config for Cisco IE9320 rugged industrial switch with inter-VLAN routing (SVIs), default route, NTP, syslog, SNMPv3, and security hardening.",
        "platform_family": "ie9320",
        "os_version": "17.15",
        "category": "industrial_distribution",
        "tags": ["industrial", "ie9320", "ios-xe-17", "distribution", "l3"],
        "locked": False,
        "is_seed": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "config_data": {
            "name": "IE9320 Distribution Template",
            "device": {"role": "industrial_distribution", "vendor": "cisco", "platform_family": "ie9320", "os_family": "ios_xe", "os_version": "17.15", "hostname": "IE9320-DIST-01"},
            "management": {"mgmt_vlan": "100", "mgmt_ip": "10.2.100.1", "mgmt_mask": "255.255.255.0", "default_gateway": "10.2.100.254", "dns_servers": ["10.2.1.10"], "domain_name": "ot.local"},
            "vlans": [
                {"id": 10, "name": "OT-DATA", "description": "OT data segment"},
                {"id": 20, "name": "OT-CTRL", "description": "OT control segment"},
                {"id": 100, "name": "MGMT", "description": "Management VLAN"},
                {"id": 999, "name": "NATIVE", "description": "Native VLAN for trunks"},
            ],
            "interfaces": {
                "access_ports": [],
                "trunk_ports": [
                    {"interface": "GigabitEthernet1/0/1", "allowed_vlans": "10,20,100", "native_vlan": "999", "description": "Downlink-to-Access-1"},
                    {"interface": "GigabitEthernet1/0/2", "allowed_vlans": "10,20,100", "native_vlan": "999", "description": "Downlink-to-Access-2"},
                ],
                "port_channels": [],
            },
            "routing": {
                "svi_list": [
                    {"vlan": 10, "ip": "10.2.10.1", "mask": "255.255.255.0", "description": "OT-DATA Gateway"},
                    {"vlan": 20, "ip": "10.2.20.1", "mask": "255.255.255.0", "description": "OT-CTRL Gateway"},
                ],
                "static_routes": [
                    {"network": "0.0.0.0", "mask": "0.0.0.0", "next_hop": "10.2.100.254"},
                ],
            },
            "stp": {"mode": "rapid-pvst", "priority": {"10": "4096", "20": "4096"}},
            "services": {
                "ntp_servers": ["10.2.1.10"], "syslog_servers": ["10.2.1.20"],
                "snmp": {"version": "v3", "community": "", "v3_user": "snmpmon", "v3_auth_protocol": "sha", "v3_auth_password": "<REPLACE>", "v3_priv_protocol": "aes128", "v3_priv_password": "<REPLACE>"},
                "dhcp_relay": [],
            },
            "security": {
                "aaa": {"enabled": True, "method": "local", "radius_servers": []},
                "local_users": [{"username": "otadmin", "privilege": 15, "secret_type": "9"}],
                "ssh": {"version": 2, "timeout": 60, "retries": 3, "rsa_bits": 2048},
                "banner": "AUTHORIZED ACCESS ONLY. All access is logged and monitored.",
                "line_vty": {"transport": "ssh", "access_class": ""},
            },
            "industrial": {"panel_name": "Dist-Rack-1", "cabinet_name": "IDF-01", "peer_role": "distribution", "uplink_role": "core", "ring_link_role": "", "multicast_relevance": "medium", "industrial_notes": "IE9320 L3 distribution"},
            "notes": "",
        },
    }


def _c1200_access_template():
    return {
        "id": str(uuid.uuid4()),
        "name": "Catalyst 1200 SMB Access Switch",
        "description": "Base config for Cisco Catalyst 1200 small-business L2 managed switch. NOT IOS-XE (firmware 4.x, dedicated renderer). Management VLAN, VLANs, access/trunk ports, SNTP, syslog, SNMP. No IP routing / HSRP / VRRP.",
        "platform_family": "c1200",
        "os_version": "4.1",
        "category": "access_switch",
        "tags": ["smb", "c1200", "firmware-4", "base-config", "l2", "non-ios-xe"],
        "locked": False,
        "is_seed": True,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "config_data": {
            "name": "Catalyst 1200 SMB Access Template",
            "device": {"role": "access_switch", "vendor": "cisco", "platform_family": "c1200", "os_family": "cisco_sb", "os_version": "4.1", "hostname": "C1200-ACCESS-01"},
            "management": {"mgmt_vlan": "100", "mgmt_ip": "10.0.100.20", "mgmt_mask": "255.255.255.0", "default_gateway": "10.0.100.1", "dns_servers": ["10.0.1.10"], "domain_name": "branch.local"},
            "vlans": [
                {"id": 10, "name": "DATA", "description": "User data"},
                {"id": 20, "name": "VOICE", "description": "Voice"},
                {"id": 100, "name": "MGMT", "description": "Management"},
            ],
            "interfaces": {
                "access_ports": [
                    {"interface": "GigabitEthernet1/0/1", "vlan": "10", "description": "PC-01", "mode": "access"},
                    {"interface": "GigabitEthernet1/0/2", "vlan": "20", "description": "Phone-01", "mode": "access"},
                ],
                "trunk_ports": [
                    {"interface": "GigabitEthernet1/0/24", "allowed_vlans": "10,20,100", "native_vlan": "100", "description": "Uplink"},
                ],
                "port_channels": [],
            },
            "routing": {"svi_list": [], "static_routes": []},
            "stp": {"mode": "rapid-pvst", "priority": {}},
            "services": {
                "ntp_servers": ["10.0.1.10"], "syslog_servers": ["10.0.1.20"],
                "snmp": {"version": "v2c", "community": "BRANCH-RO", "v3_user": "", "v3_auth_protocol": "", "v3_auth_password": "", "v3_priv_protocol": "", "v3_priv_password": ""},
                "dhcp_relay": [],
            },
            "security": {
                "aaa": {"enabled": True, "method": "local", "radius_servers": []},
                "local_users": [{"username": "smbadmin", "privilege": 15, "secret_type": "9"}],
                "ssh": {"version": 2, "timeout": 60, "retries": 3, "rsa_bits": 2048},
                "banner": "AUTHORIZED ACCESS ONLY.",
                "line_vty": {"transport": "ssh", "access_class": ""},
            },
            "industrial": {"panel_name": "", "cabinet_name": "", "peer_role": "", "uplink_role": "", "ring_link_role": "", "multicast_relevance": "", "industrial_notes": ""},
            "notes": "Cisco Catalyst 1200 (SMB firmware 4.x). CLI is rendered with C1200-specific syntax.",
        },
    }
