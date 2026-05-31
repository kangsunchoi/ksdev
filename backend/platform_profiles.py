"""
Platform profiles for Cisco device families.
Defines supported platforms, OS versions, feature support matrix,
and interface naming conventions.

Each platform_family has:
- metadata (display name, OS family, default interfaces)
- feature flags per OS version
- interface naming templates

IMPORTANT: If a feature is not explicitly listed as supported,
it must be treated as "unsupported" or "needs verification".

NOTE (version policy): supported_versions lists MAJOR IOS-XE trains only
(e.g. "17.15"). Cisco-suggested maintenance builds (e.g. 17.15.4) are not
tracked at the minor-build level here. EOL trains (17.3 / 17.6) were removed.

NOTE (C1200): The Catalyst 1200 family is NOT IOS-XE. It runs its own
small-business firmware (4.x) with a different CLI syntax, so os_family is
"cisco_sb" and it must be rendered by a dedicated renderer (see config_renderer).
"""

PLATFORM_FAMILIES = {
    "ie3300": {
        "name": "Cisco IE3300",
        "vendor": "cisco",
        "os_family": "ios_xe",
        "category": "industrial",
        "layer": 2,
        "description": "Rugged Industrial Ethernet access switch",
        "interface_prefix": "GigabitEthernet",
        "default_port_range": "1/0/1-1/0/10",
        "uplink_prefix": "GigabitEthernet",
        "uplink_range": "1/0/25-1/0/26",
        "mgig_capable": False,
        "stacking": False,
        "supported_versions": ["17.9", "17.12", "17.15"],
        "trunk_encapsulation": False,
        "notes": "L2-only platform. No IP routing. Designed for OT/industrial environments.",
    },
    "ie3400": {
        "name": "Cisco IE3400",
        "vendor": "cisco",
        "os_family": "ios_xe",
        "category": "industrial",
        "layer": 3,
        "description": "Rugged Industrial Ethernet L2/L3 switch",
        "interface_prefix": "GigabitEthernet",
        "default_port_range": "1/0/1-1/0/24",
        "uplink_prefix": "GigabitEthernet",
        "uplink_range": "1/0/25-1/0/28",
        "mgig_capable": False,
        "stacking": False,
        "supported_versions": ["17.9", "17.12", "17.15"],
        "trunk_encapsulation": False,
        "notes": "L2/L3 industrial switch. L3 requires Network Advantage license. AVOID 17.9.4/17.9.5 (boot failure per Field Notice FN74245); use 17.12 or 17.15.",
    },
    "ie3100": {
        "name": "Cisco IE3100",
        "vendor": "cisco",
        "os_family": "ios_xe",
        "category": "industrial",
        "layer": 3,
        "description": "Compact rugged Industrial Ethernet L2/L3 switch",
        "interface_prefix": "GigabitEthernet",
        "default_port_range": "1/0/1-1/0/24",
        "uplink_prefix": "GigabitEthernet",
        "uplink_range": "1/0/25-1/0/26",
        "mgig_capable": False,
        "stacking": False,
        "supported_versions": ["17.14", "17.15"],
        "trunk_encapsulation": False,
        "notes": "Newer rugged HW; supported from 17.14 onward (no older trains). L3 requires Network Advantage license.",
    },
    "ie9320": {
        "name": "Cisco IE9320",
        "vendor": "cisco",
        "os_family": "ios_xe",
        "category": "industrial",
        "layer": 3,
        "description": "Next-gen rugged industrial Ethernet switch",
        "interface_prefix": "GigabitEthernet",
        "default_port_range": "1/0/1-1/0/24",
        "uplink_prefix": "TenGigabitEthernet",
        "uplink_range": "1/0/1-1/0/4",
        "mgig_capable": False,
        "stacking": False,
        "supported_versions": ["17.12", "17.15"],
        "trunk_encapsulation": False,
        "notes": "Industrial L3 switch with enhanced capabilities.",
    },
    "catalyst_9200": {
        "name": "Cisco Catalyst 9200",
        "vendor": "cisco",
        "os_family": "ios_xe",
        "category": "campus",
        "layer": 3,
        "description": "Entry-level campus access switch",
        "interface_prefix": "GigabitEthernet",
        "default_port_range": "1/0/1-1/0/48",
        "uplink_prefix": "TenGigabitEthernet",
        "uplink_range": "1/0/1-1/0/4",
        "mgig_capable": False,
        "stacking": True,
        "supported_versions": ["17.9", "17.12", "17.15"],
        "trunk_encapsulation": False,
        "notes": "L2/L3 campus switch. L3 requires DNA license.",
    },
    "catalyst_9300": {
        "name": "Cisco Catalyst 9300",
        "vendor": "cisco",
        "os_family": "ios_xe",
        "category": "campus",
        "layer": 3,
        "description": "Flagship campus access/distribution switch",
        "interface_prefix": "GigabitEthernet",
        "default_port_range": "1/0/1-1/0/48",
        "uplink_prefix": "TenGigabitEthernet",
        "uplink_range": "1/0/1-1/0/4",
        "mgig_capable": True,
        "stacking": True,
        "supported_versions": ["17.9", "17.12", "17.15"],
        "trunk_encapsulation": False,
        "notes": "Full-featured campus switch. Supports StackWise Virtual.",
    },
    "catalyst_9500": {
        "name": "Cisco Catalyst 9500",
        "vendor": "cisco",
        "os_family": "ios_xe",
        "category": "campus",
        "layer": 3,
        "description": "Core/distribution/aggregation switch",
        "interface_prefix": "TenGigabitEthernet",
        "default_port_range": "1/0/1-1/0/48",
        "uplink_prefix": "FortyGigabitEthernet",
        "uplink_range": "1/0/1-1/0/2",
        "mgig_capable": True,
        "stacking": True,
        "supported_versions": ["17.9", "17.12", "17.15"],
        "trunk_encapsulation": False,
        "notes": "High-performance core/distribution switch.",
    },
    "wlc_9800": {
        "name": "Cisco WLC 9800",
        "vendor": "cisco",
        "os_family": "ios_xe",
        "category": "wireless",
        "layer": 3,
        "description": "Wireless LAN Controller",
        "interface_prefix": "N/A",
        "default_port_range": "N/A",
        "uplink_prefix": "N/A",
        "uplink_range": "N/A",
        "mgig_capable": False,
        "stacking": False,
        "supported_versions": ["17.12", "17.15"],
        "trunk_encapsulation": False,
        "notes": "WLC config generation is limited in this release. Only basic management and WLAN profiles are supported.",
    },
    "c1200": {
        "name": "Cisco Catalyst 1200",
        "vendor": "cisco",
        "os_family": "cisco_sb",
        "category": "smb",
        "layer": 2,
        "description": "Small-business L2 managed switch (non IOS-XE)",
        "interface_prefix": "GigabitEthernet",
        "default_port_range": "1/0/1-1/0/24",
        "uplink_prefix": "GigabitEthernet",
        "uplink_range": "1/0/25-1/0/28",
        "mgig_capable": False,
        "stacking": False,
        "supported_versions": ["4.1"],
        "trunk_encapsulation": False,
        "notes": "Cisco Small Business firmware (4.x), NOT IOS-XE. Dedicated renderer required. Interface = unit/slot/port with slot ALWAYS 0 (e.g. gi1/0/1; 'gi'/'GE' abbrev or full 'GigabitEthernet' both valid; standalone may write 'gi1'). VLANs created in 'vlan database' mode ('vlan N name X'). switchport mode access|trunk|general. No IP routing / HSRP / VRRP.",
    },
}

# Feature support matrix: (platform_family) -> set of supported features
# If a feature is NOT in this set, it is treated as unsupported for that platform.
FEATURE_SUPPORT = {
    "ie3300": {
        "hostname", "service_timestamps", "service_password_encryption",
        "aaa_local", "local_users", "vlans", "access_ports", "trunk_ports",
        "port_channel", "stp_rapid_pvst", "stp_portfast", "stp_bpduguard",
        "mgmt_vlan", "mgmt_ip_l2", "default_gateway",
        "dns", "domain_name", "ntp", "syslog", "snmp_v2c", "snmp_v3",
        "ssh", "banner", "line_vty", "line_console",
    },
    "ie3400": {
        "hostname", "service_timestamps", "service_password_encryption",
        "aaa_local", "aaa_radius", "local_users", "vlans", "access_ports", "trunk_ports",
        "port_channel", "stp_rapid_pvst", "stp_portfast", "stp_bpduguard",
        "mgmt_vlan", "mgmt_ip_l2", "mgmt_ip_svi", "default_gateway",
        "svi", "static_routing", "ip_routing",
        "dns", "domain_name", "ntp", "syslog", "snmp_v2c", "snmp_v3",
        "ssh", "banner", "line_vty", "line_console",
        "dhcp_relay",
    },
    "ie3100": {
        "hostname", "service_timestamps", "service_password_encryption",
        "aaa_local", "aaa_radius", "local_users", "vlans", "access_ports", "trunk_ports",
        "port_channel", "stp_rapid_pvst", "stp_portfast", "stp_bpduguard",
        "mgmt_vlan", "mgmt_ip_l2", "mgmt_ip_svi", "default_gateway",
        "svi", "static_routing", "ip_routing",
        "dns", "domain_name", "ntp", "syslog", "snmp_v2c", "snmp_v3",
        "ssh", "banner", "line_vty", "line_console",
        "dhcp_relay",
    },
    "ie9320": {
        "hostname", "service_timestamps", "service_password_encryption",
        "aaa_local", "aaa_radius", "local_users", "vlans", "access_ports", "trunk_ports",
        "port_channel", "stp_rapid_pvst", "stp_portfast", "stp_bpduguard",
        "mgmt_vlan", "mgmt_ip_l2", "mgmt_ip_svi", "default_gateway",
        "svi", "static_routing", "ip_routing",
        "dns", "domain_name", "ntp", "syslog", "snmp_v2c", "snmp_v3",
        "ssh", "banner", "line_vty", "line_console",
        "dhcp_relay",
    },
    "catalyst_9200": {
        "hostname", "service_timestamps", "service_password_encryption",
        "aaa_local", "aaa_radius", "local_users", "vlans", "access_ports", "trunk_ports",
        "port_channel", "stp_rapid_pvst", "stp_mst", "stp_portfast", "stp_bpduguard",
        "mgmt_vlan", "mgmt_ip_svi", "default_gateway",
        "svi", "static_routing", "ip_routing",
        "dns", "domain_name", "ntp", "syslog", "snmp_v2c", "snmp_v3",
        "ssh", "banner", "line_vty", "line_console",
        "dhcp_relay", "hsrp",
    },
    "catalyst_9300": {
        "hostname", "service_timestamps", "service_password_encryption",
        "aaa_local", "aaa_radius", "local_users", "vlans", "access_ports", "trunk_ports",
        "port_channel", "stp_rapid_pvst", "stp_mst", "stp_portfast", "stp_bpduguard",
        "mgmt_vlan", "mgmt_ip_svi", "default_gateway",
        "svi", "static_routing", "ip_routing",
        "dns", "domain_name", "ntp", "syslog", "snmp_v2c", "snmp_v3",
        "ssh", "banner", "line_vty", "line_console",
        "dhcp_relay", "hsrp", "vrrp",
    },
    "catalyst_9500": {
        "hostname", "service_timestamps", "service_password_encryption",
        "aaa_local", "aaa_radius", "local_users", "vlans", "access_ports", "trunk_ports",
        "port_channel", "stp_rapid_pvst", "stp_mst", "stp_portfast", "stp_bpduguard",
        "mgmt_vlan", "mgmt_ip_svi", "default_gateway",
        "svi", "static_routing", "ip_routing",
        "dns", "domain_name", "ntp", "syslog", "snmp_v2c", "snmp_v3",
        "ssh", "banner", "line_vty", "line_console",
        "dhcp_relay", "hsrp", "vrrp",
    },
    "wlc_9800": {
        "hostname", "service_timestamps", "service_password_encryption",
        "aaa_local", "local_users", "dns", "domain_name", "ntp", "syslog",
        "snmp_v2c", "snmp_v3", "ssh", "banner", "line_vty", "line_console",
        "wlc_wlan", "wlc_policy_profile", "wlc_policy_tag",
    },
    "c1200": {
        "hostname", "service_password_encryption",
        "aaa_local", "local_users", "vlans", "access_ports", "trunk_ports",
        "port_channel", "stp_rapid_pvst", "stp_portfast", "stp_bpduguard",
        "mgmt_vlan", "mgmt_ip_l2", "default_gateway",
        "dns", "domain_name", "ntp", "syslog", "snmp_v2c", "snmp_v3",
        "ssh", "banner", "line_vty", "line_console",
    },
}

# Industrial protocol features - NOT modeled, must show as "needs verification"
UNMODELED_INDUSTRIAL_FEATURES = {
    "prp", "hsr", "rep", "mrp", "ptp", "cip", "profinet",
    "modbus_tcp", "dlr", "redbox", "industrial_redundancy",
}

# Device roles
DEVICE_ROLES = {
    "access_switch": "Access Switch",
    "distribution_switch": "Distribution / L3 Switch",
    "core_switch": "Core Switch",
    "industrial_access": "Industrial Access Switch",
    "industrial_distribution": "Industrial Distribution Switch",
    "wlc": "Wireless LAN Controller",
}

# Role-platform compatibility
ROLE_PLATFORM_MAP = {
    # c1200 enabled: dedicated C1200 (Small Business) renderer shipped in stage 3.
    "access_switch": ["ie3300", "ie3400", "ie3100", "catalyst_9200", "catalyst_9300", "c1200"],
    "distribution_switch": ["ie3400", "ie9320", "catalyst_9300", "catalyst_9500"],
    "core_switch": ["catalyst_9500"],
    "industrial_access": ["ie3300", "ie3400", "ie3100"],
    "industrial_distribution": ["ie3400", "ie9320"],
    "wlc": ["wlc_9800"],
}


def get_platform(platform_family):
    """Get platform profile by family key."""
    return PLATFORM_FAMILIES.get(platform_family)


def get_features(platform_family):
    """Get supported features for a platform."""
    return FEATURE_SUPPORT.get(platform_family, set())


def is_feature_supported(platform_family, feature):
    """Check if a specific feature is supported on a platform."""
    return feature in FEATURE_SUPPORT.get(platform_family, set())


def is_industrial_platform(platform_family):
    """Check if platform is in the industrial (IE) category."""
    profile = PLATFORM_FAMILIES.get(platform_family, {})
    return profile.get("category") == "industrial"


def is_l3_capable(platform_family):
    """Check if platform supports Layer 3 routing."""
    profile = PLATFORM_FAMILIES.get(platform_family, {})
    return profile.get("layer", 2) >= 3


def get_platform_list():
    """Return list of platforms for API response."""
    result = []
    for key, val in PLATFORM_FAMILIES.items():
        result.append({
            "id": key,
            "name": val["name"],
            "os_family": val["os_family"],
            "category": val["category"],
            "layer": val["layer"],
            "supported_versions": val["supported_versions"],
            "description": val["description"],
            "notes": val["notes"],
            "is_industrial": val["category"] == "industrial",
        })
    return result
