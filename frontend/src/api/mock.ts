import { Topology, ChatResponse, ValidationResult, GenerateResponse, ProjectItem, HealthResponse } from "../types/topology";

export const SAMPLE_OSPF_TOPOLOGY: Topology = {
  name: "3-router-ospf-backbone",
  devices: [
    { id: "R1", type: "router", model: "2911", x: 200, y: 140 },
    { id: "R2", type: "router", model: "2911", x: 480, y: 140 },
    { id: "R3", type: "router", model: "2911", x: 760, y: 140 },
    { id: "SW1", type: "switch", model: "2960-24TT", x: 200, y: 300 },
    { id: "SW2", type: "switch", model: "2960-24TT", x: 760, y: 300 },
    { id: "PC1", type: "pc", model: "PC-PT", x: 140, y: 460 },
    { id: "PC2", type: "pc", model: "PC-PT", x: 260, y: 460 },
    { id: "PC3", type: "pc", model: "PC-PT", x: 760, y: 460 }
  ],
  links: [
    { a: "R1", a_port: "GigabitEthernet0/1", b: "R2", b_port: "GigabitEthernet0/0", cable: "cross" },
    { a: "R2", a_port: "GigabitEthernet0/1", b: "R3", b_port: "GigabitEthernet0/0", cable: "cross" },
    { a: "R1", a_port: "GigabitEthernet0/0", b: "SW1", b_port: "GigabitEthernet0/1", cable: "straight" },
    { a: "R3", a_port: "GigabitEthernet0/1", b: "SW2", b_port: "GigabitEthernet0/1", cable: "straight" },
    { a: "SW1", a_port: "FastEthernet0/1", b: "PC1", b_port: "FastEthernet0", cable: "straight" },
    { a: "SW1", a_port: "FastEthernet0/2", b: "PC2", b_port: "FastEthernet0", cable: "straight" },
    { a: "SW2", a_port: "FastEthernet0/1", b: "PC3", b_port: "FastEthernet0", cable: "straight" }
  ],
  vlans: [
    { id: 10, name: "MANAGEMENT" },
    { id: 20, name: "STAFF" }
  ],
  ip_plan: [
    { device: "R1", interface: "GigabitEthernet0/1", ip: "10.0.12.1", mask: "255.255.255.252", gateway: null },
    { device: "R2", interface: "GigabitEthernet0/0", ip: "10.0.12.2", mask: "255.255.255.252", gateway: null },
    { device: "R2", interface: "GigabitEthernet0/1", ip: "10.0.23.1", mask: "255.255.255.252", gateway: null },
    { device: "R3", interface: "GigabitEthernet0/0", ip: "10.0.23.2", mask: "255.255.255.252", gateway: null },
    { device: "R1", interface: "GigabitEthernet0/0.10", ip: "192.168.10.1", mask: "255.255.255.0", gateway: null },
    { device: "R1", interface: "GigabitEthernet0/0.20", ip: "192.168.20.1", mask: "255.255.255.0", gateway: null },
    { device: "R3", interface: "GigabitEthernet0/1", ip: "192.168.30.1", mask: "255.255.255.0", gateway: null },
    { device: "PC1", interface: "FastEthernet0", ip: "192.168.10.10", mask: "255.255.255.0", gateway: "192.168.10.1" },
    { device: "PC2", interface: "FastEthernet0", ip: "192.168.20.10", mask: "255.255.255.0", gateway: "192.168.20.1" },
    { device: "PC3", interface: "FastEthernet0", ip: "192.168.30.10", mask: "255.255.255.0", gateway: "192.168.30.1" }
  ],
  routing: { protocol: "ospf", process_id: 1, area: 0 },
  services: {
    dhcp: [
      { pool_name: "MGMT_POOL", network: "192.168.10.0", mask: "255.255.255.0", default_router: "192.168.10.1", dns_server: "1.1.1.1" },
      { pool_name: "STAFF_POOL", network: "192.168.20.0", mask: "255.255.255.0", default_router: "192.168.20.1", dns_server: "1.1.1.1" }
    ],
    nat: null,
    acls: []
  }
};

export async function mockChat(message: string): Promise<ChatResponse> {
  await new Promise((r) => setTimeout(r, 800));
  const lower = message.toLowerCase();

  if (lower.includes("ping") || lower.includes("why") || lower.includes("troubleshoot")) {
    return {
      reply: `Troubleshooting Analysis for ping failure:\n\n` +
        `1. **Default Gateway Check**: Confirm that PC1 has default gateway set to the router interface in the same subnet (e.g. 192.168.10.1).\n` +
        `2. **Interface Status**: Check 'show ip interface brief' to verify interfaces are administratively up and line protocol is up.\n` +
        `3. **VLAN Assignment**: Ensure switchport connecting PC1 is assigned to the correct VLAN.\n` +
        `4. **ARP Resolution**: Verify ARP entry using 'arp -a' on PC and 'show arp' on the router.`,
      intent: "troubleshoot",
      topology: null,
      sources: ["troubleshooting-connectivity-ping-traceroute.md", "ipv4-default-gateway.md"],
      validation: { errors: [], warnings: [] }
    };
  }

  return {
    reply: `Here is the requested Cisco topology '${SAMPLE_OSPF_TOPOLOGY.name}'. Configured with 3 routers, OSPF Area 0, and DHCP pools.`,
    intent: "build",
    topology: SAMPLE_OSPF_TOPOLOGY,
    sources: ["ospfv2-single-area-configuration.md", "router-on-a-stick-intervlan.md"],
    validation: { errors: [], warnings: [] }
  };
}

export async function mockValidate(topology: Topology): Promise<ValidationResult> {
  const errors: string[] = [];
  const warnings: string[] = [];
  if (!topology.devices || topology.devices.length === 0) {
    errors.push("Topology contains no devices.");
  }
  return { errors, warnings };
}

export async function mockGenerate(topology: Topology): Promise<GenerateResponse> {
  const configs: Record<string, string> = {};
  for (const dev of topology.devices) {
    configs[dev.id] = `! Cisco IOS Configuration for ${dev.id} (${dev.model})\nenable\nconfigure terminal\nhostname ${dev.id}\nno ip domain-lookup\nend\nwrite memory`;
  }
  const script = `// PTBuilder Script for ${topology.name}\nfunction main() {\n  echo("Building topology ${topology.name}...");\n}\nmain();`;
  return { ptbuilder_script: script, cli_configs: configs };
}

export async function mockProjects(): Promise<ProjectItem[]> {
  return [
    {
      id: 1,
      name: "3-Router OSPF Backbone",
      topology: SAMPLE_OSPF_TOPOLOGY,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    }
  ];
}

export async function mockHealth(): Promise<HealthResponse> {
  return {
    status: "healthy",
    ollama_online: false,
    ollama_model: "gemma4:e4b (Local Mock / Offline)",
    database_online: true,
    chroma_online: true,
    version: "1.0.0"
  };
}
