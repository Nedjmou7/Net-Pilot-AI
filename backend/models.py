from typing import List, Optional, Literal, Dict, Any, Union
from pydantic import BaseModel, Field


class Device(BaseModel):
    id: str = Field(..., description="Unique alphanumeric identifier, e.g. R1, SW1, PC1")
    type: Literal["router", "switch", "pc", "server"]
    model: str = Field(..., description="Cisco or PT hardware model, e.g. 2911, 2960-24TT, PC-PT, Server-PT")
    x: float = Field(default=200.0, description="X coordinate on canvas")
    y: float = Field(default=200.0, description="Y coordinate on canvas")


class Link(BaseModel):
    a: str = Field(..., description="Device A ID")
    a_port: str = Field(..., description="Port on Device A (e.g. GigabitEthernet0/0, FastEthernet0/1)")
    b: str = Field(..., description="Device B ID")
    b_port: str = Field(..., description="Port on Device B")
    cable: Literal["straight", "cross", "console", "fiber"] = Field(default="straight")


class Vlan(BaseModel):
    id: int = Field(..., ge=1, le=4094, description="VLAN ID 1-4094")
    name: str = Field(..., description="Descriptive VLAN name, e.g. MANAGEMENT, STAFF")


class IpPlanItem(BaseModel):
    device: str = Field(..., description="Device ID")
    interface: str = Field(..., description="Interface name or subinterface, e.g. GigabitEthernet0/0 or GigabitEthernet0/0.10")
    ip: str = Field(..., description="IPv4 address, e.g. 192.168.1.1")
    mask: str = Field(..., description="Subnet mask, e.g. 255.255.255.0")
    gateway: Optional[str] = Field(default=None, description="Default gateway for end hosts")


class RoutingConfig(BaseModel):
    protocol: str = Field(
        default="none",
        description="Routing protocol requested by the user, e.g. ospf, rip, eigrp, bgp, static, none"
    )
    process_id: Optional[int] = Field(default=None, description="Process ID where applicable")
    area: Optional[int] = Field(default=None, description="Area ID where applicable")


class DhcpPool(BaseModel):
    pool_name: str
    network: str
    mask: str
    default_router: str
    dns_server: Optional[str] = None


class NatConfig(BaseModel):
    inside_interfaces: List[str] = Field(default_factory=list)
    outside_interface: str = ""
    pool_name: Optional[str] = None
    type: Literal["pat", "dynamic", "static"] = "pat"


class AclRule(BaseModel):
    id: Union[int, str]
    type: Literal["standard", "extended"] = "standard"
    action: Literal["permit", "deny"] = "permit"
    source: str
    destination: Optional[str] = None
    protocol: Optional[str] = None


class ServicesConfig(BaseModel):
    dhcp: List[DhcpPool] = Field(default_factory=list)
    nat: Optional[NatConfig] = None
    acls: List[AclRule] = Field(default_factory=list)


class Topology(BaseModel):
    name: str = Field(default="network-topology")
    devices: List[Device] = Field(default_factory=list)
    links: List[Link] = Field(default_factory=list)
    vlans: List[Vlan] = Field(default_factory=list)
    ip_plan: List[IpPlanItem] = Field(default_factory=list)
    routing: RoutingConfig = Field(default_factory=RoutingConfig)
    services: ServicesConfig = Field(default_factory=ServicesConfig)


# API Request / Response schemas
class ChatRequest(BaseModel):
    message: str
    project_id: Optional[int] = None


class ValidationResult(BaseModel):
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str
    intent: Literal["build", "question", "troubleshoot"]
    topology: Optional[Topology] = None
    sources: List[str] = Field(default_factory=list)
    validation: ValidationResult = Field(default_factory=ValidationResult)


class TopologyValidateRequest(BaseModel):
    topology: Topology


class TopologyGenerateRequest(BaseModel):
    topology: Topology


class TopologyGenerateResponse(BaseModel):
    ptbuilder_script: str
    cli_configs: Dict[str, str] = Field(default_factory=dict)


class ProjectCreateRequest(BaseModel):
    name: str
    topology: Optional[Dict[str, Any]] = None


class ProjectItem(BaseModel):
    id: int
    name: str
    topology: Dict[str, Any]
    created_at: str
    updated_at: str


class HealthResponse(BaseModel):
    status: str
    ollama_online: bool
    ollama_model: str
    database_online: bool
    chroma_online: bool
    version: str = "1.0.0"
