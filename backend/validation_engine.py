"""
Validation engine for Cisco configuration projects.
Validates user inputs and produces categorized findings:
- error: Must fix before generation
- warning: Can proceed but risky
- info: Review recommended
"""

import ipaddress
import re
from platform_profiles import (
    get_platform, get_features, is_feature_supported,
    is_l3_capable, is_industrial_platform, UNMODELED_INDUSTRIAL_FEATURES
)


def validate_project(project: dict) -> list:
    """Main validation entry point. Returns list of findings."""
    findings = []
    device = project.get("device", {})
    mgmt = project.get("management", {})
    vlans = project.get("vlans", [])
    interfaces = project.get("interfaces", {})
    routing = project.get("routing", {})
    services = project.get("services", {})
    security = project.get("security", {})
    industrial = project.get("industrial", {})
    platform = device.get("platform_family", "")
    features = get_features(platform)

    # Device validation
    findings.extend(_validate_device(device))
    # Management validation
    findings.extend(_validate_management(mgmt, platform))
    # VLAN validation
    findings.extend(_validate_vlans(vlans, mgmt))
    # Interface validation
    findings.extend(_validate_interfaces(interfaces, vlans, platform))
    # Routing validation
    findings.extend(_validate_routing(routing, vlans, platform, features))
    # Services validation
    findings.extend(_validate_services(services, features))
    # Security validation
    findings.extend(_validate_security(security, features))
    # Industrial validation
    if is_industrial_platform(platform):
        findings.extend(_validate_industrial(industrial))
    # Feature support check
    findings.extend(_validate_feature_support(project, platform, features))

    return findings


def _validate_device(device: dict) -> list:
    findings = []
    hostname = device.get("hostname", "").strip()
    if not hostname:
        findings.append({"severity": "error", "field": "device.hostname", "message": "Hostname is required."})
    elif not re.match(r'^[A-Za-z][A-Za-z0-9\-_]{0,62}$', hostname):
        findings.append({"severity": "error", "field": "device.hostname", "message": "Hostname must start with a letter and contain only letters, digits, hyphens, or underscores (max 63 chars)."})

    if not device.get("platform_family"):
        findings.append({"severity": "error", "field": "device.platform_family", "message": "Platform family is required."})
    elif not get_platform(device["platform_family"]):
        findings.append({"severity": "error", "field": "device.platform_family", "message": f"Unknown platform family: {device['platform_family']}"})

    if not device.get("os_version"):
        findings.append({"severity": "error", "field": "device.os_version", "message": "OS version is required."})
    else:
        plat = get_platform(device.get("platform_family", ""))
        if plat and device["os_version"] not in plat.get("supported_versions", []):
            findings.append({"severity": "warning", "field": "device.os_version",
                             "message": f"OS version {device['os_version']} is not in the verified list for this platform. Config may need manual verification."})
    return findings


def _validate_management(mgmt: dict, platform: str) -> list:
    findings = []
    mgmt_ip = mgmt.get("mgmt_ip", "").strip()
    mgmt_mask = mgmt.get("mgmt_mask", "").strip()
    gateway = mgmt.get("default_gateway", "").strip()

    findings.extend(_validate_mgmt_ip(mgmt_ip, mgmt_mask))
    findings.extend(_validate_mgmt_gateway(mgmt_ip, mgmt_mask, gateway))
    findings.extend(_validate_mgmt_vlan(mgmt.get("mgmt_vlan")))
    findings.extend(_validate_dns_servers(mgmt.get("dns_servers", [])))
    return findings


def _validate_mgmt_ip(mgmt_ip: str, mgmt_mask: str) -> list:
    findings = []
    if mgmt_ip:
        valid, msg = _validate_ip(mgmt_ip)
        if not valid:
            findings.append({"severity": "error", "field": "management.mgmt_ip", "message": f"Invalid management IP: {msg}"})
    else:
        findings.append({"severity": "warning", "field": "management.mgmt_ip", "message": "No management IP configured. Device will not be remotely manageable."})

    if mgmt_mask:
        valid, msg = _validate_subnet_mask(mgmt_mask)
        if not valid:
            findings.append({"severity": "error", "field": "management.mgmt_mask", "message": f"Invalid subnet mask: {msg}"})
    return findings


def _validate_mgmt_gateway(mgmt_ip: str, mgmt_mask: str, gateway: str) -> list:
    findings = []
    if gateway:
        valid, msg = _validate_ip(gateway)
        if not valid:
            findings.append({"severity": "error", "field": "management.default_gateway", "message": f"Invalid gateway IP: {msg}"})
        elif mgmt_ip and mgmt_mask and not _ip_in_subnet(mgmt_ip, mgmt_mask, gateway):
            findings.append({"severity": "error", "field": "management.default_gateway",
                             "message": "Default gateway is not in the same subnet as management IP."})
    elif mgmt_ip:
        findings.append({"severity": "warning", "field": "management.default_gateway", "message": "No default gateway configured."})
    return findings


def _validate_mgmt_vlan(mgmt_vlan) -> list:
    findings = []
    if mgmt_vlan:
        try:
            v = int(mgmt_vlan)
            if v < 1 or v > 4094:
                findings.append({"severity": "error", "field": "management.mgmt_vlan", "message": "Management VLAN must be between 1 and 4094."})
        except (ValueError, TypeError):
            findings.append({"severity": "error", "field": "management.mgmt_vlan", "message": "Management VLAN must be a number."})
    return findings


def _validate_dns_servers(dns_servers: list) -> list:
    findings = []
    for dns in dns_servers:
        if dns.strip():
            valid, msg = _validate_ip(dns.strip())
            if not valid:
                findings.append({"severity": "error", "field": "management.dns_servers", "message": f"Invalid DNS server IP '{dns}': {msg}"})
    return findings


def _validate_single_vlan(index: int, vlan: dict, seen_ids: set, seen_names: set) -> list:
    """Validate one VLAN entry. Mutates seen_ids/seen_names. Returns findings for this entry."""
    findings = []
    vid = vlan.get("id")
    vname = vlan.get("name", "")

    if vid is None or vid == "":  # noqa: E711 - intentional None check + empty string check
        findings.append({"severity": "error", "field": f"vlans[{index}].id", "message": f"VLAN at index {index} has no ID."})
        return findings

    try:
        vid = int(vid)
    except (ValueError, TypeError):
        findings.append({"severity": "error", "field": f"vlans[{index}].id", "message": f"VLAN ID must be a number, got '{vid}'."})
        return findings

    if vid < 1 or vid > 4094:
        findings.append({"severity": "error", "field": f"vlans[{index}].id", "message": f"VLAN ID {vid} out of range (1-4094)."})

    if vid in seen_ids:
        findings.append({"severity": "error", "field": f"vlans[{index}].id", "message": f"Duplicate VLAN ID: {vid}."})
    seen_ids.add(vid)

    if vname and vname.lower() in seen_names:
        findings.append({"severity": "warning", "field": f"vlans[{index}].name", "message": f"Duplicate VLAN name: '{vname}'."})
    if vname:
        seen_names.add(vname.lower())

    if not vname:
        findings.append({"severity": "info", "field": f"vlans[{index}].name", "message": f"VLAN {vid} has no name. A descriptive name is recommended."})

    return findings


def _validate_mgmt_vlan_membership(mgmt: dict, vlans: list) -> list:
    """Warn if the management VLAN is not present in the configured VLAN list."""
    findings = []
    mgmt_vlan = mgmt.get("mgmt_vlan")
    if not (mgmt_vlan and vlans):
        return findings

    try:
        mv = int(mgmt_vlan)
    except (ValueError, TypeError):
        return findings

    vlan_ids = set()
    for v in vlans:
        try:
            vlan_ids.add(int(v.get("id", 0)))
        except (ValueError, TypeError):
            pass

    if mv not in vlan_ids and mv != 1:
        findings.append({"severity": "warning", "field": "management.mgmt_vlan",
                         "message": f"Management VLAN {mv} is not in the VLAN list. Add it to ensure it is created on the device."})
    return findings


def _validate_vlans(vlans: list, mgmt: dict) -> list:
    findings = []
    seen_ids = set()
    seen_names = set()

    for i, vlan in enumerate(vlans):
        findings.extend(_validate_single_vlan(i, vlan, seen_ids, seen_names))

    findings.extend(_validate_mgmt_vlan_membership(mgmt, vlans))
    return findings


def _validate_interfaces(interfaces: dict, vlans: list, platform: str) -> list:
    findings = []
    vlan_ids = set()
    for v in vlans:
        try:
            vlan_ids.add(int(v.get("id", 0)))
        except (ValueError, TypeError):
            pass

    all_intf_names = set()
    findings.extend(_validate_access_ports(interfaces.get("access_ports", []), vlan_ids, all_intf_names))
    findings.extend(_validate_trunk_ports(interfaces.get("trunk_ports", []), all_intf_names))
    findings.extend(_validate_port_channels(interfaces.get("port_channels", []), all_intf_names))
    return findings


def _validate_access_ports(ports: list, vlan_ids: set, all_intf_names: set) -> list:
    findings = []
    for i, port in enumerate(ports):
        intf = port.get("interface", "").strip()
        if not intf:
            findings.append({"severity": "error", "field": f"interfaces.access_ports[{i}].interface", "message": "Interface name is required."})
        elif intf in all_intf_names:
            findings.append({"severity": "error", "field": f"interfaces.access_ports[{i}].interface", "message": f"Duplicate interface: {intf}. An interface can only be configured once."})
        else:
            all_intf_names.add(intf)

        vlan = port.get("vlan")
        if vlan:
            try:
                v = int(vlan)
                if vlan_ids and v not in vlan_ids and v != 1:
                    findings.append({"severity": "warning", "field": f"interfaces.access_ports[{i}].vlan",
                                     "message": f"Access VLAN {v} on {intf} is not in the VLAN list."})
            except (ValueError, TypeError):
                findings.append({"severity": "error", "field": f"interfaces.access_ports[{i}].vlan", "message": f"Invalid VLAN ID on {intf}."})

        if not port.get("description"):
            findings.append({"severity": "info", "field": f"interfaces.access_ports[{i}].description",
                             "message": f"No description on {intf or f'access port {i}'}. Descriptions are recommended."})
    return findings


def _validate_trunk_ports(ports: list, all_intf_names: set) -> list:
    findings = []
    for i, port in enumerate(ports):
        intf = port.get("interface", "").strip()
        if not intf:
            findings.append({"severity": "error", "field": f"interfaces.trunk_ports[{i}].interface", "message": "Interface name is required."})
        elif intf in all_intf_names:
            findings.append({"severity": "error", "field": f"interfaces.trunk_ports[{i}].interface", "message": f"Duplicate interface: {intf}."})
        else:
            all_intf_names.add(intf)

        allowed = port.get("allowed_vlans", "").strip()
        if allowed and allowed.lower() != "all":
            valid, msg = _validate_vlan_list(allowed)
            if not valid:
                findings.append({"severity": "error", "field": f"interfaces.trunk_ports[{i}].allowed_vlans",
                                 "message": f"Invalid trunk allowed VLAN list on {intf}: {msg}"})

        native = port.get("native_vlan")
        if native:
            try:
                nv = int(native)
                if nv == 1:
                    findings.append({"severity": "warning", "field": f"interfaces.trunk_ports[{i}].native_vlan",
                                     "message": f"Native VLAN on {intf} is VLAN 1 (default). Consider using a dedicated native VLAN."})
            except (ValueError, TypeError):
                findings.append({"severity": "error", "field": f"interfaces.trunk_ports[{i}].native_vlan", "message": f"Invalid native VLAN on {intf}."})

        if not port.get("description"):
            findings.append({"severity": "info", "field": f"interfaces.trunk_ports[{i}].description",
                             "message": f"No description on trunk {intf or f'trunk port {i}'}."})
    return findings


def _validate_port_channels(port_channels: list, all_intf_names: set) -> list:
    findings = []
    for i, pc in enumerate(port_channels):
        pc_id = pc.get("id")
        members = pc.get("members", [])
        if not pc_id:
            findings.append({"severity": "error", "field": f"interfaces.port_channels[{i}].id", "message": "Port-channel ID is required."})
        if len(members) < 2:
            findings.append({"severity": "warning", "field": f"interfaces.port_channels[{i}].members",
                             "message": f"Port-channel {pc_id} has fewer than 2 members."})
        for m in members:
            if m.strip() in all_intf_names:
                findings.append({"severity": "error", "field": f"interfaces.port_channels[{i}].members",
                                 "message": f"Interface {m} is already assigned as a standalone port and as a port-channel member."})
    return findings


def _validate_routing(routing: dict, vlans: list, platform: str, features: set) -> list:
    findings = []
    vlan_ids = set()
    for v in vlans:
        try:
            vlan_ids.add(int(v.get("id", 0)))
        except (ValueError, TypeError):
            pass

    findings.extend(_validate_svis(routing.get("svi_list", []), vlan_ids, features))
    findings.extend(_validate_static_routes(routing.get("static_routes", []), features))
    return findings


def _validate_svis(svi_list: list, vlan_ids: set, features: set) -> list:
    findings = []
    svi_ips = set()
    for i, svi in enumerate(svi_list):
        if "svi" not in features and "ip_routing" not in features:
            findings.append({"severity": "error", "field": f"routing.svi_list[{i}]",
                             "message": "SVIs are not supported on this platform. L3 routing is not available."})
            break

        vid = svi.get("vlan")
        ip = svi.get("ip", "").strip()
        mask = svi.get("mask", "").strip()

        if vid:
            try:
                v = int(vid)
                if vlan_ids and v not in vlan_ids:
                    findings.append({"severity": "warning", "field": f"routing.svi_list[{i}].vlan",
                                     "message": f"SVI VLAN {v} is not in the VLAN list."})
            except (ValueError, TypeError):
                findings.append({"severity": "error", "field": f"routing.svi_list[{i}].vlan", "message": "Invalid VLAN ID for SVI."})

        if ip:
            valid, msg = _validate_ip(ip)
            if not valid:
                findings.append({"severity": "error", "field": f"routing.svi_list[{i}].ip", "message": f"Invalid SVI IP: {msg}"})
            elif ip in svi_ips:
                findings.append({"severity": "error", "field": f"routing.svi_list[{i}].ip", "message": f"Duplicate IP address: {ip}"})
            else:
                svi_ips.add(ip)

        if mask:
            valid, msg = _validate_subnet_mask(mask)
            if not valid:
                findings.append({"severity": "error", "field": f"routing.svi_list[{i}].mask", "message": f"Invalid SVI subnet mask: {msg}"})
    return findings


def _validate_static_routes(routes: list, features: set) -> list:
    findings = []
    for i, route in enumerate(routes):
        if "static_routing" not in features:
            findings.append({"severity": "error", "field": f"routing.static_routes[{i}]",
                             "message": "Static routing is not supported on this platform."})
            break

        network = route.get("network", "").strip()
        _mask = route.get("mask", "").strip()  # stored for future validation
        next_hop = route.get("next_hop", "").strip()

        if network:
            valid, msg = _validate_ip(network)
            if not valid and network != "0.0.0.0":
                findings.append({"severity": "error", "field": f"routing.static_routes[{i}].network", "message": f"Invalid network: {msg}"})

        if next_hop:
            valid, msg = _validate_ip(next_hop)
            if not valid:
                findings.append({"severity": "error", "field": f"routing.static_routes[{i}].next_hop", "message": f"Invalid next-hop: {msg}"})
    return findings


def _validate_services(services: dict, features: set) -> list:
    findings = []
    findings.extend(_validate_ntp_servers(services.get("ntp_servers", [])))
    findings.extend(_validate_syslog_servers(services.get("syslog_servers", [])))
    findings.extend(_validate_snmp(services.get("snmp", {})))
    findings.extend(_validate_dhcp_relay(services.get("dhcp_relay", []), features))
    return findings


def _validate_dhcp_relay(entries: list, features: set) -> list:
    findings = []
    if entries and "dhcp_relay" not in features:
        findings.append({"severity": "error", "field": "services.dhcp_relay",
                         "message": "DHCP relay is not supported on this platform."})
        return findings
    for i, entry in enumerate(entries):
        vlan = str(entry.get("svi_vlan", "")).strip()
        helper = (entry.get("helper_ip", "") or "").strip()
        if not vlan:
            findings.append({"severity": "error", "field": f"services.dhcp_relay[{i}].svi_vlan",
                             "message": "DHCP relay entry requires an SVI VLAN."})
        else:
            try:
                v = int(vlan)
                if v < 1 or v > 4094:
                    findings.append({"severity": "error", "field": f"services.dhcp_relay[{i}].svi_vlan",
                                     "message": f"DHCP relay VLAN {v} out of range (1-4094)."})
            except (ValueError, TypeError):
                findings.append({"severity": "error", "field": f"services.dhcp_relay[{i}].svi_vlan",
                                 "message": "DHCP relay VLAN must be a number."})
        if not helper:
            findings.append({"severity": "error", "field": f"services.dhcp_relay[{i}].helper_ip",
                             "message": "DHCP helper-address (IP) is required."})
        else:
            valid, msg = _validate_ip(helper)
            if not valid:
                findings.append({"severity": "error", "field": f"services.dhcp_relay[{i}].helper_ip",
                                 "message": f"Invalid DHCP helper IP: {msg}"})
    return findings


def _validate_ntp_servers(ntp_servers: list) -> list:
    findings = []
    for ntp in ntp_servers:
        if ntp.strip():
            valid, msg = _validate_ip(ntp.strip())
            if not valid:
                findings.append({"severity": "error", "field": "services.ntp_servers", "message": f"Invalid NTP server IP '{ntp}': {msg}"})

    if not ntp_servers or not any(s.strip() for s in ntp_servers):
        findings.append({"severity": "warning", "field": "services.ntp_servers", "message": "No NTP servers configured. Time synchronization is critical for logging and certificates."})
    return findings


def _validate_syslog_servers(syslog_servers: list) -> list:
    findings = []
    for syslog in syslog_servers:
        if syslog.strip():
            valid, msg = _validate_ip(syslog.strip())
            if not valid:
                findings.append({"severity": "error", "field": "services.syslog_servers", "message": f"Invalid syslog server IP '{syslog}': {msg}"})
    return findings


def _validate_snmp(snmp: dict) -> list:
    findings = []
    if snmp.get("version") != "v3":
        return findings

    if not snmp.get("v3_user"):
        findings.append({"severity": "error", "field": "services.snmp.v3_user", "message": "SNMPv3 requires a username."})
    if not snmp.get("v3_auth_protocol"):
        findings.append({"severity": "error", "field": "services.snmp.v3_auth_protocol", "message": "SNMPv3 requires an authentication protocol (SHA/MD5)."})
    if not snmp.get("v3_auth_password"):
        findings.append({"severity": "error", "field": "services.snmp.v3_auth_password", "message": "SNMPv3 requires an authentication password."})
    if snmp.get("v3_priv_protocol") and not snmp.get("v3_priv_password"):
        findings.append({"severity": "error", "field": "services.snmp.v3_priv_password", "message": "SNMPv3 privacy protocol requires a privacy password."})
    return findings


def _validate_security(security: dict, features: set) -> list:
    findings = []
    aaa = security.get("aaa", {})

    if aaa.get("enabled"):
        if aaa.get("method") == "radius":
            if "aaa_radius" not in features:
                findings.append({"severity": "error", "field": "security.aaa.method",
                                 "message": "RADIUS AAA is not supported on this platform."})
            elif not aaa.get("radius_servers"):
                findings.append({"severity": "error", "field": "security.aaa.radius_servers",
                                 "message": "AAA with RADIUS requires at least one RADIUS server."})

    users = security.get("local_users", [])
    if not users:
        findings.append({"severity": "warning", "field": "security.local_users",
                         "message": "No local users configured. At least one admin account is recommended."})

    seen_usernames = set()
    for i, user in enumerate(users):
        uname = user.get("username", "").strip()
        if not uname:
            findings.append({"severity": "error", "field": f"security.local_users[{i}].username", "message": "Username is required."})
        elif uname.lower() in seen_usernames:
            findings.append({"severity": "error", "field": f"security.local_users[{i}].username", "message": f"Duplicate username: {uname}"})
        else:
            seen_usernames.add(uname.lower())

    banner = security.get("banner", "")
    if not banner:
        findings.append({"severity": "info", "field": "security.banner", "message": "No login banner configured. A legal notice banner is recommended for production."})

    return findings


def _validate_industrial(industrial: dict) -> list:
    findings = []
    if not industrial.get("panel_name") and not industrial.get("cabinet_name"):
        findings.append({"severity": "info", "field": "industrial",
                         "message": "No panel/cabinet name specified. Recommended for OT asset tracking."})
    return findings


def _validate_feature_support(project: dict, platform: str, features: set) -> list:
    findings = []
    interfaces = project.get("interfaces", {})
    routing = project.get("routing", {})
    services = project.get("services", {})

    if interfaces.get("port_channels") and "port_channel" not in features:
        findings.append({"severity": "error", "field": "interfaces.port_channels",
                         "message": "Port-channel is not supported on this platform."})

    if routing.get("svi_list") and "svi" not in features:
        findings.append({"severity": "error", "field": "routing.svi_list",
                         "message": "SVIs (inter-VLAN routing) are not supported on this platform."})

    if services.get("snmp", {}).get("version") == "v3" and "snmp_v3" not in features:
        findings.append({"severity": "error", "field": "services.snmp",
                         "message": "SNMPv3 is not supported on this platform."})

    return findings


# --- Helper functions ---

def _validate_ip(ip_str: str) -> tuple:
    try:
        ip = ipaddress.ip_address(ip_str.strip())
        if ip.is_multicast:
            return False, "Multicast addresses are not valid for this field."
        return True, ""
    except ValueError as e:
        return False, str(e)


def _validate_subnet_mask(mask_str: str) -> tuple:
    try:
        parts = mask_str.strip().split(".")
        if len(parts) != 4:
            return False, "Subnet mask must have 4 octets."
        val = 0
        for p in parts:
            o = int(p)
            if o < 0 or o > 255:
                return False, f"Octet {o} out of range."
            val = (val << 8) | o
        # Check it's a valid mask (contiguous 1s followed by 0s)
        if val == 0:
            return False, "Subnet mask cannot be 0.0.0.0"
        inverted = val ^ 0xFFFFFFFF
        if (inverted & (inverted + 1)) != 0:
            return False, "Not a valid subnet mask (non-contiguous bits)."
        return True, ""
    except (ValueError, TypeError) as e:
        return False, str(e)


def _validate_vlan_list(vlan_str: str) -> tuple:
    """Validate a VLAN list string like '10,20,30-40,100'"""
    try:
        parts = vlan_str.replace(" ", "").split(",")
        for part in parts:
            if "-" in part:
                start, end = part.split("-", 1)
                s, e = int(start), int(end)
                if s < 1 or e > 4094 or s > e:
                    return False, f"Invalid VLAN range: {part}"
            else:
                v = int(part)
                if v < 1 or v > 4094:
                    return False, f"VLAN {v} out of range (1-4094)."
        return True, ""
    except (ValueError, TypeError):
        return False, "Invalid format. Use comma-separated IDs or ranges (e.g., 10,20,30-40)."


def _ip_in_subnet(ip_str: str, mask_str: str, gateway_str: str) -> bool:
    """Check if gateway is in the same subnet as ip/mask."""
    try:
        _ip = ipaddress.ip_address(ip_str.strip())  # validates format
        gw = ipaddress.ip_address(gateway_str.strip())
        # Convert mask to prefix length
        parts = mask_str.strip().split(".")
        val = 0
        for p in parts:
            val = (val << 8) | int(p)
        prefix_len = bin(val).count("1")
        network = ipaddress.ip_network(f"{ip_str.strip()}/{prefix_len}", strict=False)
        return gw in network
    except (ValueError, TypeError):
        return False
