from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

class Device(BaseModel):
    id: str = Field(..., description="Unique device identifier, e.g. R1, SW1, PC1")
    type: Literal["router", "switch", "pc", "server"]
    model: str = Field(..., description="Cisco model, e.g. 2911, 2960-24TT, PC-PT, Server-PT")
    x: float = Field(default=200.0, description="X coordinate for diagram")
    y: float = Field(default=200.0, description="Y coordinate for diagram")

class Link(BaseModel):
    a: str = Field(..., description="Device A ID")
    a_port: str = Field(..., description="Port on Device A")
    b: str = Field(..., description="Device B ID")
    b_port: str = Field(..., description="Port on Device B")
    cable: Literal["straight", "crossover", "serial", "fiber", "auto"] = Field(default="straight")

class Vlan(BaseModel):
    id: int = Field(..., ge=1, le=4094, description="VLAN ID between 1 and 4094")
    name: str = Field(..., description="VLAN Name, e.g. MANAGEMENT, STAFF")

class IpAssignment(BaseModel):
    device: str = Field(..., description="Device ID")
    interface: str = Field(..., description="Port or subinterface name, e.g. GigabitEthernet0/0")
    ip: str = Field(..., description="IPv4 address")
    mask: str = Field(..., description="Subnet mask, e.g. 255.255.255.0")
    gateway: Optional[str] = Field(default=None, description="Default gateway IP for end devices")

class RoutingConfig(BaseModel):
    protocol: Literal["ospf", "rip", "static", "eigrp", "none"] = Field(default="none")
    process_id: Optional[int] = Field(default=None, description="Process ID for OSPF/EIGRP")
    area: Optional[int] = Field(default=0, description="Area number for OSPF")

class DhcpPool(BaseModel):
    pool_name: str
    network: str
    mask: str
    default_router: str
    dns_server: Optional[str] = None

class NatConfig(BaseModel):
    inside_interface: str
    outside_interface: str
    pool_name: Optional[str] = None
    overload: bool = True

class AclRule(BaseModel):
    action: Literal["permit", "deny"]
    source: str
    destination: Optional[str] = None
    port: Optional[str] = None

class AclAppliedTo(BaseModel):
    device: str
    interface: str
    direction: Literal["in", "out"]

class AclConfig(BaseModel):
    id: int
    type: Literal["standard", "extended"] = "standard"
    rules: List[str] = []
    applied_to: Optional[AclAppliedTo] = None

class ServicesConfig(BaseModel):
    dhcp: List[DhcpPool] = []
    nat: Optional[NatConfig] = None
    acls: List[AclConfig] = []

class Topology(BaseModel):
    name: str = Field(default="network-topology")
    devices: List[Device] = []
    links: List[Link] = []
    vlans: List[Vlan] = []
    ip_plan: List[IpAssignment] = []
    routing: RoutingConfig = Field(default_factory=RoutingConfig)
    services: ServicesConfig = Field(default_factory=ServicesConfig)

class ValidationResult(BaseModel):
    errors: List[str] = []
    warnings: List[str] = []
    is_valid: bool = True

class ChatRequest(BaseModel):
    message: str
    project_id: Optional[int] = None

class ChatResponse(BaseModel):
    reply: str
    intent: Literal["build", "question", "troubleshoot"]
    topology: Optional[Topology] = None
    sources: List[str] = []
    validation: ValidationResult = Field(default_factory=ValidationResult)

class GenerateRequest(BaseModel):
    topology: Topology

class GenerateResponse(BaseModel):
    ptbuilder_script: str
    cli_configs: Dict[str, str]

class ProjectCreate(BaseModel):
    name: str
    topology: Topology

class ProjectResponse(BaseModel):
    id: int
    name: str
    topology_json: str
    created_at: str
    updated_at: str
