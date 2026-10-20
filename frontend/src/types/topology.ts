export type DeviceType = "router" | "switch" | "pc" | "server";
export type CableType = "straight" | "cross" | "console" | "fiber";
export type RoutingProtocol = "ospf" | "rip" | "static" | "none";

export interface Device {
  id: string;
  type: DeviceType;
  model: string;
  x: number;
  y: number;
}

export interface Link {
  a: string;
  a_port: string;
  b: string;
  b_port: string;
  cable: CableType;
}

export interface Vlan {
  id: number;
  name: string;
}

export interface IpPlanItem {
  device: string;
  interface: string;
  ip: string;
  mask: string;
  gateway?: string | null;
}

export interface RoutingConfig {
  protocol: RoutingProtocol;
  process_id?: number | null;
  area?: number | null;
}

export interface DhcpPool {
  pool_name: string;
  network: string;
  mask: string;
  default_router: string;
  dns_server?: string | null;
}

export interface NatConfig {
  inside_interfaces: string[];
  outside_interface: string;
  pool_name?: string | null;
  type: "pat" | "dynamic" | "static";
}

export interface AclRule {
  id: number | string;
  type: "standard" | "extended";
  action: "permit" | "deny";
  source: string;
  destination?: string | null;
  protocol?: string | null;
}

export interface ServicesConfig {
  dhcp: DhcpPool[];
  nat?: NatConfig | null;
  acls: AclRule[];
}

export interface Topology {
  name: string;
  devices: Device[];
  links: Link[];
  vlans: Vlan[];
  ip_plan: IpPlanItem[];
  routing: RoutingConfig;
  services: ServicesConfig;
}

export interface ValidationResult {
  errors: string[];
  warnings: string[];
}

export interface ChatResponse {
  reply: string;
  intent: "build" | "question" | "troubleshoot";
  topology?: Topology | null;
  sources: string[];
  validation: ValidationResult;
}

export interface GenerateResponse {
  ptbuilder_script: string;
  cli_configs: Record<string, string>;
}

export interface ProjectItem {
  id: number;
  name: string;
  topology: Topology;
  created_at: string;
  updated_at: string;
  messages?: Array<{
    id: number;
    role: "user" | "assistant";
    content: string;
    intent?: string;
    created_at: string;
  }>;
}

export interface HealthResponse {
  status: string;
  ollama_online: boolean;
  ollama_model: string;
  database_online: boolean;
  chroma_online: boolean;
  version: string;
}
