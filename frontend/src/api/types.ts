export type DeviceType = 'router' | 'switch' | 'pc' | 'server';

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
  cable: 'straight' | 'crossover' | 'serial' | 'fiber' | 'auto';
}

export interface Vlan {
  id: number;
  name: string;
}

export interface IpAssignment {
  device: string;
  interface: string;
  ip: string;
  mask: string;
  gateway?: string | null;
}

export interface RoutingConfig {
  protocol: 'ospf' | 'rip' | 'static' | 'eigrp' | 'none';
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
  inside_interface: string;
  outside_interface: string;
  pool_name?: string | null;
  overload: boolean;
}

export interface AclConfig {
  id: number;
  type: 'standard' | 'extended';
  rules: string[];
  applied_to?: {
    device: string;
    interface: string;
    direction: 'in' | 'out';
  } | null;
}

export interface ServicesConfig {
  dhcp: DhcpPool[];
  nat: NatConfig | null;
  acls: AclConfig[];
}

export interface Topology {
  name: string;
  devices: Device[];
  links: Link[];
  vlans: Vlan[];
  ip_plan: IpAssignment[];
  routing: RoutingConfig;
  services: ServicesConfig;
}

export interface ValidationResult {
  errors: string[];
  warnings: string[];
  is_valid: boolean;
}

export interface ChatResponse {
  reply: string;
  intent: 'build' | 'question' | 'troubleshoot';
  topology?: Topology | null;
  sources: string[];
  validation: ValidationResult;
}

export interface GenerateResponse {
  ptbuilder_script: string;
  cli_configs: Record<string, string>;
}

export interface Project {
  id: number;
  name: string;
  topology_json: string;
  created_at: string;
  updated_at: string;
}

export interface HealthStatus {
  status: string;
  database: string;
  ollama: {
    status: string;
    ollama_connected: boolean;
    model: string;
    model_available: boolean;
    models_installed?: string[];
  };
}
