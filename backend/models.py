"""
Pydantic models for API request/response validation.
These define the data contracts between frontend and backend.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid


class DeviceConfig(BaseModel):
    role: str = "access_switch"
    vendor: str = "cisco"
    platform_family: str = ""
    os_family: str = "ios_xe"
    os_version: str = "17.9"
    hostname: str = ""


class ManagementConfig(BaseModel):
    mgmt_vlan: Optional[str] = ""
    mgmt_ip: str = ""
    mgmt_mask: str = "255.255.255.0"
    default_gateway: str = ""
    dns_servers: List[str] = []
    domain_name: str = ""


class VlanEntry(BaseModel):
    id: Any = ""
    name: str = ""
    description: str = ""


class AccessPort(BaseModel):
    interface: str = ""
    vlan: Optional[str] = ""
    voice_vlan: Optional[str] = ""
    description: str = ""
    mode: str = "access"


class TrunkPort(BaseModel):
    interface: str = ""
    allowed_vlans: str = ""
    native_vlan: Optional[str] = ""
    description: str = ""


class PortChannel(BaseModel):
    id: Any = ""
    members: List[str] = []
    mode: str = "trunk"
    protocol: str = "lacp"
    allowed_vlans: str = ""
    vlan: Optional[str] = ""
    description: str = ""


class InterfaceConfig(BaseModel):
    access_ports: List[AccessPort] = []
    trunk_ports: List[TrunkPort] = []
    port_channels: List[PortChannel] = []


class SviEntry(BaseModel):
    vlan: Any = ""
    ip: str = ""
    mask: str = "255.255.255.0"
    description: str = ""


class StaticRoute(BaseModel):
    network: str = ""
    mask: str = ""
    next_hop: str = ""


class RoutingConfig(BaseModel):
    svi_list: List[SviEntry] = []
    static_routes: List[StaticRoute] = []


class StpConfig(BaseModel):
    mode: str = "rapid-pvst"
    priority: Dict[str, Any] = {}


class SnmpConfig(BaseModel):
    version: str = ""
    community: str = ""
    v3_user: str = ""
    v3_auth_protocol: str = ""
    v3_auth_password: str = ""
    v3_priv_protocol: str = ""
    v3_priv_password: str = ""


class DhcpRelay(BaseModel):
    svi_vlan: str = ""
    helper_ip: str = ""


class ServiceConfig(BaseModel):
    ntp_servers: List[str] = []
    syslog_servers: List[str] = []
    snmp: SnmpConfig = SnmpConfig()
    dhcp_relay: List[DhcpRelay] = []


class RadiusServer(BaseModel):
    ip: str = ""
    key: str = ""


class AaaConfig(BaseModel):
    enabled: bool = True
    method: str = "local"
    radius_servers: List[RadiusServer] = []


class LocalUser(BaseModel):
    username: str = ""
    privilege: int = 15
    secret_type: str = "9"


class SshConfig(BaseModel):
    version: int = 2
    timeout: int = 60
    retries: int = 3
    rsa_bits: int = 2048


class LineVtyConfig(BaseModel):
    transport: str = "ssh"
    access_class: str = ""


class SecurityConfig(BaseModel):
    aaa: AaaConfig = AaaConfig()
    local_users: List[LocalUser] = []
    ssh: SshConfig = SshConfig()
    banner: str = ""
    line_vty: LineVtyConfig = LineVtyConfig()


class IndustrialConfig(BaseModel):
    panel_name: str = ""
    cabinet_name: str = ""
    peer_role: str = "none"
    uplink_role: str = ""
    ring_link_role: str = ""
    multicast_relevance: str = ""
    industrial_notes: str = ""


class ProjectCreate(BaseModel):
    name: str = ""
    device: DeviceConfig = DeviceConfig()
    management: ManagementConfig = ManagementConfig()
    vlans: List[VlanEntry] = []
    interfaces: InterfaceConfig = InterfaceConfig()
    routing: RoutingConfig = RoutingConfig()
    stp: StpConfig = StpConfig()
    services: ServiceConfig = ServiceConfig()
    security: SecurityConfig = SecurityConfig()
    industrial: IndustrialConfig = IndustrialConfig()
    notes: str = ""


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    device: Optional[DeviceConfig] = None
    management: Optional[ManagementConfig] = None
    vlans: Optional[List[VlanEntry]] = None
    interfaces: Optional[InterfaceConfig] = None
    routing: Optional[RoutingConfig] = None
    stp: Optional[StpConfig] = None
    services: Optional[ServiceConfig] = None
    security: Optional[SecurityConfig] = None
    industrial: Optional[IndustrialConfig] = None
    notes: Optional[str] = None


class TemplateCreate(BaseModel):
    name: str = ""
    description: str = ""
    platform_family: str = ""
    os_version: str = ""
    category: str = ""
    tags: List[str] = []
    config_data: ProjectCreate = ProjectCreate()


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    config_data: Optional[ProjectCreate] = None


class ValidationFinding(BaseModel):
    severity: str  # error, warning, info
    field: str
    message: str
