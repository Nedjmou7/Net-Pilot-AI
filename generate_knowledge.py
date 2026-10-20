import os

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "knowledge")
os.makedirs(KNOWLEDGE_DIR, exist_ok=True)

DOCS = [
    # IP Addressing & Subnetting (1-10)
    ("01-ipv4-addressing-classes.md", "IPv4 Addressing and Classes", """# IPv4 Addressing and Classes

IPv4 addresses are 32-bit logical identifiers divided into four 8-bit octets separated by dots. Historically, IPv4 used classful addressing:
- **Class A**: Range `1.0.0.0` to `126.255.255.255` (Default mask: `255.0.0.0` or `/8`). Designed for massive networks with over 16 million hosts.
- **Class B**: Range `128.0.0.0` to `191.255.255.255` (Default mask: `255.255.0.0` or `/16`). Designed for medium-to-large organizations with up to 65,534 hosts.
- **Class C**: Range `192.0.0.0` to `223.255.255.255` (Default mask: `255.255.255.0` or `/24`). Designed for small networks with up to 254 hosts.
- **Class D**: Range `224.0.0.0` to `239.255.255.255` used for Multicast traffic (e.g., OSPF `224.0.0.5`, RIPv2 `224.0.0.9`).
- **Class E**: Range `240.0.0.0` to `255.255.255.255` reserved for experimental research.

The address `127.0.0.0/8` is reserved for host loopback diagnostic testing.

```cisco
Router(config)# interface GigabitEthernet0/0
Router(config-if)# ip address 192.168.1.1 255.255.255.0
Router(config-if)# no shutdown
```

### Common Mistakes
- Assigning the network ID (all host bits 0) or the broadcast IP (all host bits 1) to a host interface.
- Confusing Class D multicast addresses with standard unicast host addresses.
"""),

    ("02-private-vs-public-ip.md", "Private vs Public IPv4 Addresses", """# Private vs Public IPv4 Addresses

RFC 1918 defines three private IPv4 address blocks reserved for internal local area networks (LANs). Private addresses cannot be routed across the public Internet and must be translated using NAT/PAT.

- **Class A Private**: `10.0.0.0` to `10.255.255.255` (`10.0.0.0/8`)
- **Class B Private**: `172.16.0.0` to `172.31.255.255` (`172.16.0.0/12`)
- **Class C Private**: `192.168.0.0` to `192.168.255.255` (`192.168.0.0/16`)

Public IP addresses are globally unique and allocated by IANA/RIRs (ARIN, RIPE, APNIC, LACNIC, AFRINIC) to ISPs and enterprises.

```cisco
Router(config)# interface GigabitEthernet0/0
Router(config-if)# ip address 10.10.10.1 255.255.255.0
Router(config-if)# no shutdown
```

### Common Mistakes
- Using a public IP space (e.g. `8.8.8.0/24`) inside an enterprise intranet without owning the block, leading to unreachable Internet services.
- Failing to configure NAT on border routers before routing private traffic to an Internet ISP.
"""),

    ("03-subnetting-and-cidr.md", "Subnetting and CIDR Notation", """# Subnetting and CIDR Notation

Classless Inter-Domain Routing (CIDR) eliminates rigid class boundaries by allowing arbitrary prefix lengths denoted with a slash (`/`). Subnetting borrows bits from the host portion of an address and assigns them to the network prefix.

Key Formulas:
- Number of Subnets = `2^s` (where `s` is borrowed subnet bits)
- Usable Hosts per Subnet = `2^h - 2` (where `h` is remaining host bits)
- Common Prefix Masks:
  * `/24` = `255.255.255.0` (254 hosts)
  * `/25` = `255.255.255.128` (126 hosts)
  * `/26` = `255.255.255.192` (62 hosts)
  * `/27` = `255.255.255.224` (30 hosts)
  * `/28` = `255.255.255.240` (14 hosts)
  * `/29` = `255.255.255.248` (6 hosts)
  * `/30` = `255.255.255.252` (2 hosts, ideal for point-to-point router links)

```cisco
Router(config)# interface GigabitEthernet0/1
Router(config-if)# ip address 10.0.0.1 255.255.255.252
Router(config-if)# no shutdown
```

### Common Mistakes
- Forgetting to subtract 2 for the network ID and broadcast address when calculating required host capacity.
- Miscalculating the magic number increment (`256 - mask_octet`), causing subnets to overlap.
"""),

    ("04-vlsm-variable-length-subnet-masking.md", "Variable Length Subnet Masking (VLSM)", """# Variable Length Subnet Masking (VLSM)

Variable Length Subnet Masking (VLSM) allows multiple subnet masks within the same network space, avoiding IP address wastage. The fundamental rule of VLSM is: always allocate subnets in descending order of size (largest host requirements first).

Example allocating `192.168.1.0/24`:
1. Subnet A (Needs 50 hosts): Needs `/26` (`255.255.255.192`), block `192.168.1.0 - 192.168.1.63`.
2. Subnet B (Needs 25 hosts): Needs `/27` (`255.255.255.224`), block `192.168.1.64 - 192.168.1.95`.
3. Subnet C (WAN point-to-point): Needs `/30` (`255.255.255.252`), block `192.168.1.96 - 192.168.1.99`.

```cisco
Router(config)# interface GigabitEthernet0/0
Router(config-if)# ip address 192.168.1.1 255.255.255.192
Router(config)# interface GigabitEthernet0/1
Router(config-if)# ip address 192.168.1.97 255.255.255.252
```

### Common Mistakes
- Subnetting from the bottom up, creating non-contiguous fragmented gaps.
- Overlapping subnets when dividing a parent block into different prefix sizes.
"""),

    ("05-default-gateway-concepts.md", "Default Gateway Concepts and Configuration", """# Default Gateway Concepts and Configuration

The default gateway is the layer 3 interface IP on a local network to which host devices send traffic destined for remote networks (networks outside their own broadcast domain). When a host determines that destination IP is not in its local subnet via bitwise AND with its subnet mask, it sends an ARP request for the default gateway's MAC address and encapsulates the packet toward the gateway router.

On Cisco IOS Switches (Layer 2):
```cisco
Switch(config)# interface vlan 1
Switch(config-if)# ip address 192.168.1.2 255.255.255.0
Switch(config-if)# no shutdown
Switch(config)# ip default-gateway 192.168.1.1
```

On PCs in Packet Tracer:
In IP Configuration desktop tab, set:
- IPv4 Address: `192.168.1.10`
- Subnet Mask: `255.255.255.0`
- Default Gateway: `192.168.1.1`

### Common Mistakes
- Setting the PC's default gateway to an IP address outside its configured subnet.
- Forgetting `ip default-gateway` on layer 2 switches, preventing remote SSH/Telnet management.
"""),

    ("06-apipa-and-loopback.md", "APIPA and Loopback Addresses", """# APIPA and Loopback Addresses

Automatic Private IP Addressing (APIPA) is used when a DHCP client cannot obtain an IP lease from a DHCP server:
- APIPA range: `169.254.0.1` to `169.254.255.254` (`169.254.0.0/16`).
- If a PC has a `169.254.x.x` address, DHCP discovery has failed.

Loopback Interfaces on Cisco Routers:
A Loopback interface is a virtual software interface that never goes down as long as the router remains powered. Used for:
- Stable Router IDs in OSPF and BGP.
- Reliable management and diagnostic ping endpoints.

```cisco
Router(config)# interface loopback 0
Router(config-if)# ip address 10.255.255.1 255.255.255.255
```

### Common Mistakes
- Assuming an APIPA address (`169.254.x.x`) can communicate with internet gateways.
- Not using a `/32` (`255.255.255.255`) mask on router loopback interfaces, wasting address space.
"""),

    # VLANs & Trunking (7-16)
    ("07-vlan-fundamentals.md", "VLAN Fundamentals and Benefits", """# VLAN Fundamentals and Benefits

A Virtual Local Area Network (VLAN) is a logical grouping of switch ports that creates isolated broadcast domains at Layer 2. By default, all switch ports belong to VLAN 1 (the default administrative VLAN).

Benefits of VLANs:
- **Security**: Isolates sensitive departments (e.g. Finance, HR).
- **Cost Reduction**: Reuses existing physical switch infrastructure.
- **Broadcast Control**: Reduces broadcast traffic storm impact.
- **Improved Performance**: Smaller broadcast domains increase CPU efficiency.

```cisco
Switch# configure terminal
Switch(config)# vlan 10
Switch(config-vlan)# name MANAGEMENT
Switch(config-vlan)# vlan 20
Switch(config-vlan)# name SALES
Switch(config-vlan)# exit
```

### Common Mistakes
- Creating access ports assigned to a VLAN without first creating the VLAN in global configuration mode.
- Changing or deleting VLAN 1, which cannot be renamed or deleted.
"""),

    ("08-switchport-access-ports.md", "Switch Access Port Configuration", """# Switch Access Port Configuration

Access ports connect end devices (PCs, printers, servers) to a single VLAN. Traffic leaving an access port toward a PC is untagged (standard 802.3 Ethernet frame without 802.1Q header).

```cisco
Switch(config)# interface FastEthernet0/1
Switch(config-if)# switchport mode access
Switch(config-if)# switchport access vlan 10
Switch(config-if)# spanning-tree portfast
Switch(config-if)# no shutdown
```

To configure multiple ports simultaneously:
```cisco
Switch(config)# interface range FastEthernet0/1 - 10
Switch(config-if-range)# switchport mode access
Switch(config-if-range)# switchport access vlan 10
```

### Common Mistakes
- Leaving ports in dynamic desirable or dynamic auto modes, which can allow rogue VLAN trunking attacks.
- Forgetting `spanning-tree portfast` on end-host ports, causing DHCP timeouts due to STP 30-second listening/learning delays.
"""),

    ("09-802-1q-trunking.md", "IEEE 802.1Q Trunking Protocol", """# IEEE 802.1Q Trunking Protocol

A trunk link carries traffic for multiple VLANs over a single physical cable between switches, or between a switch and a router. IEEE 802.1Q inserts a 4-byte tag into the standard Ethernet frame:
- Tag Protocol Identifier (TPID): `0x8100` (16 bits)
- Priority Code Point (PCP): 3 bits (QoS CoS)
- Drop Eligible Indicator (DEI): 1 bit
- VLAN Identifier (VID): 12 bits (supports VLANs 1 to 4094)

```cisco
Switch(config)# interface GigabitEthernet0/1
Switch(config-if)# switchport mode trunk
Switch(config-if)# switchport trunk allowed vlan 10,20,30
Switch(config-if)# no shutdown
```

On Layer 3 switches (e.g. Cisco 3560):
```cisco
Switch(config-if)# switchport trunk encapsulation dot1q
Switch(config-if)# switchport mode trunk
```

### Common Mistakes
- Missing `switchport trunk encapsulation dot1q` on Catalyst 3560 switches before running `switchport mode trunk`.
- Restricting allowed VLANs on one side of a trunk while forgetting the other side.
"""),

    ("10-native-vlan-security.md", "Native VLAN Concepts and Security", """# Native VLAN Concepts and Security

In 802.1Q trunking, the Native VLAN carries untagged frames across the trunk link. By default, the native VLAN is VLAN 1. When an 802.1Q trunk receives an untagged frame, it forwards it to the native VLAN.

Security Best Practices:
1. Never use default VLAN 1 as the native VLAN.
2. Change the native VLAN to an unused, dedicated non-routed VLAN ID (e.g. VLAN 999).
3. The native VLAN must match on both ends of the trunk link; mismatch causes CDP native VLAN mismatch errors and cross-VLAN traffic leakage.

```cisco
Switch(config)# vlan 999
Switch(config-vlan)# name NATIVE_UNUSED
Switch(config)# interface GigabitEthernet0/1
Switch(config-if)# switchport trunk native vlan 999
```

### Common Mistakes
- Configuring different native VLANs on the two ends of a trunk link, triggering `%CDP-4-NATIVE_VLAN_MISMATCH`.
- Assigning host access ports to the native VLAN.
"""),

    ("11-intervlan-router-on-a-stick.md", "Inter-VLAN Routing with Router-on-a-Stick", """# Inter-VLAN Routing with Router-on-a-Stick

Router-on-a-Stick (ROAS) enables routing between different VLANs using a single physical router interface divided into logical subinterfaces. Each subinterface acts as the default gateway for one VLAN.

Configuration on Cisco 2911 Router:
```cisco
Router(config)# interface GigabitEthernet0/0
Router(config-if)# no shutdown
Router(config-if)# exit

Router(config)# interface GigabitEthernet0/0.10
Router(config-subif)# encapsulation dot1Q 10
Router(config-subif)# ip address 192.168.10.1 255.255.255.0

Router(config)# interface GigabitEthernet0/0.20
Router(config-subif)# encapsulation dot1Q 20
Router(config-subif)# ip address 192.168.20.1 255.255.255.0
```

Switch Port connecting to the Router must be configured as a trunk:
```cisco
Switch(config)# interface GigabitEthernet0/1
Switch(config-if)# switchport mode trunk
```

### Common Mistakes
- Forgetting `no shutdown` on the physical parent interface (`GigabitEthernet0/0`).
- Configuring `ip address` before running `encapsulation dot1Q <vlan_id>`.
- Configuring the switch port connecting to the router as an access port instead of a trunk.
"""),

    ("12-intervlan-svi-layer3-switch.md", "Inter-VLAN Routing with SVI on Layer 3 Switch", """# Inter-VLAN Routing with SVI on Layer 3 Switch

A Switch Virtual Interface (SVI) is a routed virtual interface representing a VLAN on a multilayer switch (such as Cisco Catalyst 3560). SVIs provide hardware-accelerated wire-speed inter-VLAN routing without traffic traversing an external router.

Configuration Steps:
1. Enable IP routing globally: `ip routing`
2. Create the VLANs: `vlan 10`, `vlan 20`
3. Configure SVIs with default gateway IP addresses:

```cisco
Switch(config)# ip routing
Switch(config)# vlan 10
Switch(config)# vlan 20

Switch(config)# interface Vlan 10
Switch(config-if)# ip address 192.168.10.1 255.255.255.0
Switch(config-if)# no shutdown

Switch(config)# interface Vlan 20
Switch(config-if)# ip address 192.168.20.1 255.255.255.0
Switch(config-if)# no shutdown
```

### Common Mistakes
- Omitting `ip routing` on the multilayer switch; without it, the switch behaves as a pure Layer 2 bridge.
- An SVI stays down/down unless at least one active switch port in that VLAN is up.
"""),

    # Routing Fundamentals & Protocols (13-25)
    ("13-static-routing.md", "Static Routing and Default Routes", """# Static Routing and Default Routes

Static routes are manually configured routing table entries specifying how to reach a remote network destination. They have an Administrative Distance (AD) of 1 by default.

Syntax:
`ip route <network> <mask> {next-hop-ip | exit-interface} [distance]`

1. Standard Static Route:
```cisco
Router(config)# ip route 192.168.2.0 255.255.255.0 10.0.0.2
```

2. Default Static Route (Gateway of Last Resort):
Matches all packets not explicitly matched by any specific routing table entry.
```cisco
Router(config)# ip route 0.0.0.0 0.0.0.0 10.0.0.2
```

3. Floating Static Route:
A backup route configured with an administrative distance higher than the primary routing protocol (e.g. AD 90 or 110):
```cisco
Router(config)# ip route 0.0.0.0 0.0.0.0 192.168.99.1 120
```

### Common Mistakes
- Using exit interface on multiaccess broadcast Ethernet networks instead of next-hop IP, causing excessive ARP requests.
- Specifying a next-hop IP that is not directly connected or routable.
"""),

    ("14-rip-routing-protocol.md", "Routing Information Protocol (RIPv2)", """# Routing Information Protocol (RIPv2)

RIPv2 is a distance-vector routing protocol that uses hop count as its metric (maximum 15 hops; 16 hops is considered unreachable). RIPv2 sends multicast updates to `224.0.0.9` every 30 seconds and supports VLSM and classless routing.

Configuration:
```cisco
Router(config)# router rip
Router(config-router)# version 2
Router(config-router)# no auto-summary
Router(config-router)# network 192.168.1.0
Router(config-router)# network 10.0.0.0
Router(config-router)# passive-interface GigabitEthernet0/0
```

Verification:
```cisco
Router# show ip route rip
Router# show ip protocols
```

### Common Mistakes
- Forgetting `no auto-summary`, which causes RIP to summarize networks to their classful boundaries.
- Forgetting `version 2`, leaving the router in RIPv1 broadcast mode.
"""),

    ("15-ospf-single-area.md", "OSPF Single Area Configuration", """# OSPF Single Area Configuration

Open Shortest Path First (OSPF) is an open-standard link-state routing protocol (RFC 2328). It uses Dijkstra's Shortest Path First (SPF) algorithm, has an administrative distance of 110, and uses cost (inverse of bandwidth) as metric.

In single-area OSPF, all routers reside in Area 0 (Backbone Area).

Configuration:
```cisco
Router(config)# router ospf 1
Router(config-router)# router-id 1.1.1.1
Router(config-router)# network 192.168.1.0 0.0.0.255 area 0
Router(config-router)# network 10.0.12.0 0.0.0.3 area 0
Router(config-router)# passive-interface GigabitEthernet0/0
```

Verification Commands:
```cisco
Router# show ip ospf neighbor
Router# show ip ospf interface brief
Router# show ip route ospf
```

### Common Mistakes
- Using a subnet mask instead of a wildcard mask in the `network` command.
- Area ID mismatch between connected neighbors, preventing FULL adjacency state.
"""),

    ("16-ospf-multi-area.md", "OSPF Multi-Area Architecture", """# OSPF Multi-Area Architecture

Multi-area OSPF reduces SPF calculations, restricts routing update propagation, and shrinks routing table sizes through summarization.

Key Concepts:
- **Area 0 (Backbone)**: Core transit area; all other areas must connect directly to Area 0.
- **Area Border Router (ABR)**: Router with interfaces in Area 0 and one or more non-backbone areas.
- **Autonomous System Boundary Router (ASBR)**: Router that redistributes routes from external sources (e.g. BGP, RIP, static) into OSPF.

Configuration on ABR:
```cisco
Router(config)# router ospf 1
Router(config-router)# router-id 2.2.2.2
Router(config-router)# network 10.0.1.0 0.0.0.3 area 0
Router(config-router)# network 192.168.10.0 0.0.0.255 area 1
```

### Common Mistakes
- Creating disconnected non-backbone areas that do not connect to Area 0.
- Forgetting to summarize routes on ABR using `area <id> range <network> <mask>`.
"""),

    ("17-ospf-neighbor-adjacencies.md", "OSPF Neighbor Adjacency States", """# OSPF Neighbor Adjacency States

Two OSPF routers progress through seven formal states to become fully adjacent:
1. **Down**: No OSPF hello packets received.
2. **Init**: Hello received, but router does not see its own router ID in neighbor's hello.
3. **2-Way**: Bidirectional communication established (DR/BDR election happens here on broadcast networks).
4. **ExStart**: Master/Slave relationship negotiated and initial sequence number chosen.
5. **Exchange**: Database Description (DBD) packets exchanged.
6. **Loading**: Link State Requests (LSR) and Link State Updates (LSU) synchronize the LSDB.
7. **Full**: Routers have identical LSDBs; adjacency is fully established.

Neighbor Requirements:
- Same Area ID
- Same Subnet and Subnet Mask
- Matching Hello (10s) and Dead (40s) timers
- Matching Authentication credentials
- Matching MTU size

### Common Mistakes
- Mismatched MTU causing routers to stick in `EXSTART` or `EXCHANGE` state.
- Mismatched hello/dead intervals preventing neighbor discovery.
"""),

    ("18-eigrp-fundamentals.md", "EIGRP Protocol and Configuration", """# EIGRP Protocol and Configuration

Enhanced Interior Gateway Routing Protocol (EIGRP) is an advanced distance-vector routing protocol developed by Cisco. It uses the Diffusing Update Algorithm (DUAL) for fast loop-free convergence.

Key Attributes:
- Administrative Distance: 90 (Internal), 170 (External).
- Composite Metric: Bandwidth and Delay (`K1=1, K3=1`).
- Multicast Address: `224.0.0.10`.
- Successor: The best primary path placed in routing table.
- Feasible Successor (FS): A backup path that meets the Feasibility Condition (`Reported Distance < Feasible Distance`).

Configuration:
```cisco
Router(config)# router eigrp 100
Router(config-router)# no auto-summary
Router(config-router)# network 192.168.1.0 0.0.0.255
Router(config-router)# network 10.0.0.0 0.0.0.3
Router(config-router)# passive-interface GigabitEthernet0/0
```

### Common Mistakes
- Autonomous system (AS) number mismatch between routers (`router eigrp 100` vs `200`).
- Forgetting `no auto-summary` on older Cisco IOS versions.
"""),

    # DHCP, NAT, ACLs (19-35)
    ("19-dhcp-server-ios.md", "Cisco IOS DHCP Server Configuration", """# Cisco IOS DHCP Server Configuration

Cisco IOS routers can serve as dynamic DHCP servers for LAN clients, distributing IP addresses, subnet masks, default gateways, and DNS servers.

Configuration:
```cisco
Router(config)# ip dhcp excluded-address 192.168.10.1 192.168.10.10
Router(config)# ip dhcp pool LAN_POOL_10
Router(dhcp-config)# network 192.168.10.0 255.255.255.0
Router(dhcp-config)# default-router 192.168.10.1
Router(dhcp-config)# dns-server 8.8.8.8
Router(dhcp-config)# domain-name company.local
Router(dhcp-config)# lease 7
```

Verification:
```cisco
Router# show ip dhcp binding
Router# show ip dhcp pool
Router# show ip dhcp conflict
```

### Common Mistakes
- Forgetting `ip dhcp excluded-address` for the router's own interface IP, creating duplicate IP conflicts.
- Typo in `default-router` pointing hosts to an unroutable IP address.
"""),

    ("20-dhcp-relay-ip-helper.md", "DHCP Relay and IP Helper-Address", """# DHCP Relay and IP Helper-Address

DHCP client requests are broadcast packets (`255.255.255.255`). Routers drop broadcast packets by default. When the centralized DHCP server is located on a different subnet or across a WAN, the router interface facing the clients must be configured with `ip helper-address` to relay broadcast requests as unicast packets to the DHCP server.

Configuration:
```cisco
Router(config)# interface GigabitEthernet0/0
Router(config-if)# ip helper-address 10.1.1.50
```

When using Router-on-a-Stick:
```cisco
Router(config)# interface GigabitEthernet0/0.10
Router(config-subif)# ip helper-address 10.1.1.50
```

### Common Mistakes
- Applying `ip helper-address` on the interface facing the server instead of the interface facing the client broadcast domain.
- Forgetting to route traffic between the client subnet and the DHCP server.
"""),

    ("21-nat-and-pat-concepts.md", "NAT and PAT Concepts", """# NAT and PAT Concepts

Network Address Translation (NAT) translates private RFC 1918 IPv4 addresses into globally routable public IPv4 addresses.

Types of NAT:
1. **Static NAT**: One-to-one mapping between an internal private IP and an external public IP. Typically used for hosting internal web servers.
2. **Dynamic NAT**: Many-to-many mapping from a pool of public IPs on a first-come, first-served basis.
3. **Port Address Translation (PAT / NAT Overload)**: Many-to-one mapping that translates multiple private IPs to a single public IP using unique source layer 4 port numbers (TCP/UDP).

Terminology:
- **Inside Local**: Private IP of an inside host.
- **Inside Global**: Public IP representing the inside host to the outside.
- **Outside Local**: Outside destination IP as known internally.
- **Outside Global**: Real public IP assigned to the outside destination.

### Common Mistakes
- Confusing inside and outside interfaces.
- Failing to include the `overload` keyword when sharing a single public IP address among multiple hosts.
"""),

    ("22-pat-overload-configuration.md", "Port Address Translation (PAT) Overload Configuration", """# Port Address Translation (PAT) Overload Configuration

PAT (NAT Overload) allows hundreds of internal hosts to access the Internet using a single router public IP interface.

Configuration Steps:
1. Define inside and outside interfaces:
```cisco
Router(config)# interface GigabitEthernet0/0
Router(config-if)# ip nat inside
Router(config)# interface GigabitEthernet0/1
Router(config-if)# ip nat outside
```
2. Define standard ACL matching inside traffic:
```cisco
Router(config)# access-list 1 permit 192.168.0.0 0.0.255.255
```
3. Enable NAT overload on outside interface:
```cisco
Router(config)# ip nat inside source list 1 interface GigabitEthernet0/1 overload
```

Verification:
```cisco
Router# show ip nat translations
Router# show ip nat statistics
Router# clear ip nat translation *
```

### Common Mistakes
- Forgetting `ip nat inside` or `ip nat outside` on the relevant interfaces.
- Wildcard mask error in the permit ACL preventing inside host traffic from matching.
"""),

    ("23-standard-access-lists.md", "Standard Access Control Lists (ACL)", """# Standard Access Control Lists (ACL)

Standard ACLs filter traffic based solely on the source IPv4 address.
- Numbered range: `1` to `99` and `1300` to `1999`.
- Placement Rule: Place standard ACLs **as close to the destination as possible** to avoid inadvertently blocking legitimate traffic to other destinations.
- Implicit Deny: Every ACL ends with an invisible `deny any` statement.

Configuration:
```cisco
Router(config)# access-list 10 permit 192.168.10.0 0.0.0.255
Router(config)# access-list 10 deny any
Router(config)# interface GigabitEthernet0/1
Router(config-if)# ip access-group 10 out
```

Named Standard ACL:
```cisco
Router(config)# ip access-list standard BLOCK_GUESTS
Router(config-std-nacl)# permit 192.168.1.50
Router(config-std-nacl)# deny 192.168.1.0 0.0.0.255
Router(config-std-nacl)# permit any
```

### Common Mistakes
- Placing a standard ACL close to the source, inadvertently blocking the source from reaching ALL networks.
- Forgetting the implicit `deny any` at the end of the ACL, blocking more traffic than intended.
"""),

    ("24-extended-access-lists.md", "Extended Access Control Lists (ACL)", """# Extended Access Control Lists (ACL)

Extended ACLs filter traffic based on source IP, destination IP, protocol (IP, TCP, UDP, ICMP), and port numbers (HTTP 80, HTTPS 443, DNS 53, SSH 22).
- Numbered range: `100` to `199` and `2000` to `2699`.
- Placement Rule: Place extended ACLs **as close to the source as possible** to prevent unwanted traffic from traversing network bandwidth.

Configuration Example:
Allow subnet `192.168.10.0/24` to access web servers (`80, 443`), but block ping (ICMP) and all other traffic:
```cisco
Router(config)# access-list 101 permit tcp 192.168.10.0 0.0.0.255 any eq 80
Router(config)# access-list 101 permit tcp 192.168.10.0 0.0.0.255 any eq 443
Router(config)# access-list 101 deny icmp 192.168.10.0 0.0.0.255 any
Router(config)# access-list 101 permit ip any any

Router(config)# interface GigabitEthernet0/0
Router(config-if)# ip access-group 101 in
```

### Common Mistakes
- Applying the ACL in the wrong direction (`in` instead of `out`, or vice versa).
- Specifying source and destination ports in the wrong order.
"""),

    # Switching & Security (25-35)
    ("25-spanning-tree-protocol.md", "Spanning Tree Protocol (STP) and Election", """# Spanning Tree Protocol (STP) and Election

STP (IEEE 802.1D) prevents Layer 2 switching loops and broadcast storms in networks with redundant physical links by logically placing redundant switch ports into a blocking state.

Root Bridge Election:
1. Lowest Bridge Priority (Default: `32768`).
2. If priority tied: Lowest MAC Address wins.

Port Roles:
- **Root Port (RP)**: Lowest cost path toward the Root Bridge (one per non-root switch).
- **Designated Port (DP)**: Lowest cost path on a segment (forwards traffic; all ports on Root Bridge are DPs).
- **Blocking / Alternate Port**: Discards frames to prevent loops.

Configuration:
```cisco
Switch(config)# spanning-tree vlan 1 priority 4096
! Or using root primary macro:
Switch(config)# spanning-tree vlan 1 root primary
```

### Common Mistakes
- Leaving default priority on all switches, allowing an old unmanaged access switch to become the root bridge.
- Confusing bridge priority increments: must be multiples of 4096.
"""),

    ("26-portfast-and-bpduguard.md", "STP PortFast and BPDU Guard", """# STP PortFast and BPDU Guard

By default, an STP port takes 30 to 50 seconds to reach forwarding state (Listening 15s -> Learning 15s -> Forwarding). For end-user devices (PCs, servers), this delay causes DHCP discovery timeouts.

- **PortFast**: Immediately transitions an access port from blocking to forwarding, bypassing listening and learning states.
- **BPDU Guard**: Shuts down a PortFast-enabled port (places into `err-disable`) if a BPDU packet is received, protecting against rogue switches connected to access ports.

Configuration:
```cisco
Switch(config)# interface FastEthernet0/1
Switch(config-if)# switchport mode access
Switch(config-if)# spanning-tree portfast
Switch(config-if)# spanning-tree bpduguard enable
```

Globally:
```cisco
Switch(config)# spanning-tree portfast default
Switch(config)# spanning-tree portfast bpduguard default
```

### Common Mistakes
- Enabling PortFast on switch-to-switch trunk links, causing catastrophic bridging loops.
- Not knowing how to recover an `err-disabled` port (`shutdown` followed by `no shutdown`).
"""),

    ("27-etherchannel-lacp-pagp.md", "EtherChannel (Link Aggregation) Configuration", """# EtherChannel (Link Aggregation) Configuration

EtherChannel bundles up to 8 physical Ethernet links into a single logical channel (Port-Channel), providing link redundancy and aggregated bandwidth.

Protocols:
1. **LACP (IEEE 802.3ad - Open Standard)**:
   - Modes: `active` (initiates negotiation), `passive` (waits for partner).
2. **PAgP (Cisco Proprietary)**:
   - Modes: `desirable` (initiates), `auto` (waits).
3. **Static (Manual)**:
   - Mode: `on` (no negotiation).

LACP Configuration:
```cisco
Switch(config)# interface range GigabitEthernet0/1 - 2
Switch(config-if-range)# channel-group 1 mode active
Switch(config-if-range)# exit

Switch(config)# interface port-channel 1
Switch(config-if)# switchport mode trunk
Switch(config-if)# switchport trunk allowed vlan 10,20
```

### Common Mistakes
- Mismatched duplex, speed, or VLAN settings across physical member interfaces.
- Combining `passive` with `passive` or `auto` with `auto`, preventing channel negotiation.
"""),

    ("28-port-security.md", "Switch Port Security", """# Switch Port Security

Port Security restricts input to an interface by limiting the MAC addresses permitted to send traffic through that switch port.

Violation Modes:
- **Shutdown**: Port enters `err-disable` state immediately; sends SNMP trap and syslog message. (Default)
- **Restrict**: Drops frames from unauthorized MACs; increments violation counter and logs syslog message.
- **Protect**: Drops frames from unauthorized MACs silently without logging.

Configuration:
```cisco
Switch(config)# interface FastEthernet0/1
Switch(config-if)# switchport mode access
Switch(config-if)# switchport port-security
Switch(config-if)# switchport port-security maximum 2
Switch(config-if)# switchport port-security mac-address sticky
Switch(config-if)# switchport port-security violation shutdown
```

### Common Mistakes
- Trying to enable port security on dynamic switchports; port MUST be in static access mode (`switchport mode access`).
- Forgetting `switchport port-security` before setting maximum or sticky commands.
"""),

    ("29-ssh-remote-access.md", "Configuring Secure Shell (SSH) Remote Management", """# Configuring Secure Shell (SSH) Remote Management

Telnet transmits management credentials in plaintext. Secure Shell (SSH) encrypts all session communication using cryptographic keys.

Cisco IOS SSH Prerequisites:
1. Hostname must not be the default `Router` or `Switch`.
2. IP domain name must be configured.
3. RSA crypto key pair generated (minimum 1024 bits for SSHv2).
4. Local user account with password or secret.
5. VTY lines set to accept SSH.

Configuration:
```cisco
Router(config)# hostname R1
R1(config)# ip domain-name cisco.lab
R1(config)# crypto key generate rsa modulus 2048
R1(config)# ip ssh version 2
R1(config)# username admin privilege 15 secret Cisco123!
R1(config)# line vty 0 4
R1(config-line)# login local
R1(config-line)# transport input ssh
R1(config-line)# exit
```

### Common Mistakes
- Attempting `crypto key generate rsa` with default hostname `Router`, which fails.
- Leaving `transport input telnet` or omitting `login local` on VTY lines.
"""),

    # Troubleshooting & Packet Tracer Tips (30-40)
    ("30-troubleshooting-ping-icmp.md", "Ping Diagnostics and ICMP Troubleshooting", """# Ping Diagnostics and ICMP Troubleshooting

The `ping` command uses ICMP Echo Request (Type 8) and ICMP Echo Reply (Type 0) to test Layer 3 reachability.

Cisco IOS Ping Characters:
- `!`: Successful Echo Reply received.
- `.`: Timed out waiting for reply (often ARP delay or routing black hole).
- `U`: Destination Unreachable ICMP packet returned by router.
- `Q`: Source quench (device congested).
- `M`: Could not fragment.

Extended Ping:
```cisco
Router# ping
Target IP address: 192.168.2.10
Repeat count [5]: 10
Datagram size [100]: 1500
Source address or interface: 10.0.12.1
```

Step-by-step Troubleshooting Path:
1. Ping `127.0.0.1` (verifies local TCP/IP protocol stack).
2. Ping local device IP address (verifies NIC hardware).
3. Ping default gateway IP (verifies local LAN and switch connectivity).
4. Ping remote router IP (verifies routing table and WAN links).
5. Ping remote host or server.

### Common Mistakes
- Panicking on the first `.` of a 5-packet ping: the first packet is often dropped while the switch/router resolves ARP.
- Forgetting that host personal firewalls (Windows Defender) drop ICMP requests by default.
"""),

    ("31-troubleshooting-show-commands.md", "Essential Cisco IOS Show Commands", """# Essential Cisco IOS Show Commands

The following `show` commands form the foundation of CCNA network diagnostics:

1. Interface Verification:
```cisco
Router# show ip interface brief
```
Checks IP assignments and Status/Protocol states (`up/up` is functional; `up/down` indicates layer 2 framing/clocking fault; `administratively down` indicates `shutdown` command).

2. Routing Table:
```cisco
Router# show ip route
```
Inspect codes: `C` (Connected), `S` (Static), `O` (OSPF), `D` (EIGRP), `R` (RIP). Verify presence of destination network or `0.0.0.0/0`.

3. CDP Neighbors (Layer 2 discovery):
```cisco
Router# show cdp neighbors
Router# show cdp neighbors detail
```
Discovers directly connected Cisco devices, remote port names, and IP addresses.

4. Switch MAC Table:
```cisco
Switch# show mac address-table
```

### Common Mistakes
- Overlooking the difference between status `down` and `administratively down`.
- Forgetting to check `show ip route` before assuming physical link or cable failure.
"""),

    ("32-packet-tracer-cable-types.md", "Packet Tracer Cable Types and Connections", """# Packet Tracer Cable Types and Connections

Connecting network devices requires matching the physical cable type to the MDI/MDIX specification:

1. **Straight-Through Cable (Solid Black Line in PT)**:
   - Connects unlike devices:
     * Switch to Router
     * Switch to PC / Server
     * Hub to PC

2. **Crossover Cable (Dashed Black Line in PT)**:
   - Connects like devices:
     * Switch to Switch
     * Router to Router (GigabitEthernet)
     * PC to PC
     * PC to Router (both use MDI pinouts!)

3. **Serial DTE/DCE Cable (Red Lightning Bolt in PT)**:
   - Connects router serial WAN interfaces (HWIC-2T).
   - The DCE end provides clock rate: `clock rate 64000`.

4. **Console Cable (Light Blue Line)**:
   - Connects PC RS-232 serial port to Router/Switch Console port.

### Common Mistakes
- Connecting a PC directly to a Router Ethernet port using a straight-through cable in Packet Tracer (must use crossover cable).
- Forgetting `clock rate` on the DCE serial interface in Packet Tracer.
"""),

    ("33-packet-tracer-device-models.md", "Packet Tracer Supported Device Models", """# Packet Tracer Supported Device Models

TopoGemma supports standard Cisco models in Packet Tracer:

1. **Cisco 2911 Integrated Services Router**:
   - 3 Onboard GigabitEthernet ports: `GigabitEthernet0/0`, `GigabitEthernet0/1`, `GigabitEthernet0/2`.
   - Expansion slots for HWIC-2T serial modules.

2. **Cisco 1941 Router**:
   - 2 Onboard GigabitEthernet ports: `GigabitEthernet0/0`, `GigabitEthernet0/1`.

3. **Cisco 2960-24TT Layer 2 Switch**:
   - 24 FastEthernet access ports: `FastEthernet0/1` to `FastEthernet0/24`.
   - 2 GigabitEthernet uplink ports: `GigabitEthernet0/1`, `GigabitEthernet0/2`.

4. **Cisco 3560-24PS Layer 3 Multilayer Switch**:
   - 24 FastEthernet ports + 2 Gigabit uplinks.
   - Supports hardware routing via `ip routing` and SVIs.

5. **PC-PT and Server-PT**:
   - Single NIC: `FastEthernet0`.

### Common Mistakes
- Requesting `GigabitEthernet0/3` on a 2911 router (only ports 0/0, 0/1, 0/2 exist onboard).
- Assuming standard 2960 switch can route IP traffic without an external router.
"""),

    ("34-packet-tracer-cli-modes.md", "Cisco IOS CLI Navigation and Modes", """# Cisco IOS CLI Navigation and Modes

Cisco IOS features a hierarchical command mode structure:

1. **User EXEC Mode** (`Router>`):
   - Basic view-only diagnostic commands.
   - Enter Privileged EXEC: `enable`.

2. **Privileged EXEC Mode** (`Router#`):
   - Detailed troubleshooting, `show` commands, file operations, `ping`, `traceroute`, `write memory`.
   - Enter Global Config: `configure terminal`.

3. **Global Configuration Mode** (`Router(config)#`):
   - System-wide settings: `hostname`, `ip routing`, `vlan`.
   - Sub-modes:
     * Interface: `interface GigabitEthernet0/0` -> `Router(config-if)#`
     * Subinterface: `interface Gi0/0.10` -> `Router(config-subif)#`
     * Line: `line console 0` -> `Router(config-line)#`
     * Routing: `router ospf 1` -> `Router(config-router)#`

Navigation:
- `exit`: Moves up one level.
- `end` or `Ctrl+Z`: Returns directly to Privileged EXEC (`#`).

### Common Mistakes
- Trying to execute `configure terminal` commands from User EXEC mode (`>`).
- Forgetting `do` prefix when running `show` commands from within configuration submodes (e.g. `do show ip route`).
"""),

    ("35-packet-tracer-ptbuilder-tips.md", "Packet Tracer PTBuilder Scripting Guide", """# Packet Tracer PTBuilder Scripting Guide

PTBuilder allows programmatic creation and automated configuration of Packet Tracer topologies using JavaScript.

Key PTBuilder API Functions:
- `addDevice(name, model, x, y)`: Instantiates a device on the canvas at coordinate `(x, y)`.
- `addLink(dev1, port1, dev2, port2, cable)`: Connects two devices using specified cable type (`straight`, `crossover`, `serial`).
- `configureIosDevice(name, cliConfigString)`: Sends CLI configuration script to router or switch terminal.
- `configurePcIp(name, isDhcp, ip, mask, gateway)`: Configures IP desktop settings on PC or Server.

Deployment in Packet Tracer:
1. Open Cisco Packet Tracer.
2. Navigate to **Extensions** -> **Scripting** -> **Configure PT Script Modules** (or PTBuilder Runner).
3. Paste the generated script and click **Run**.

### Common Mistakes
- Attempting to connect a link to a port that is already in use by another device.
- Passing lowercase port abbreviations (`gi0/0`) instead of canonical names (`GigabitEthernet0/0`).
""")
]

# Generate additional high-yield CCNA docs to complete the 80+ document set
EXTRA_TOPICS = [
    ("36-ipv6-basics.md", "IPv6 Addressing and Structure", "IPv6 uses 128-bit addresses represented in hexadecimal. Global unicast addresses start with 2000::/3. Unique local start with FC00::/7. Link-local start with FE80::/10.\n\n```cisco\nRouter(config)# ipv6 unicast-routing\nRouter(config-if)# ipv6 address 2001:db8:acad:1::1/64\n```\n\n### Common Mistakes\n- Forgetting `ipv6 unicast-routing` globally before configuring IPv6 routing protocols."),
    ("37-ipv6-link-local.md", "IPv6 Link-Local Addresses", "IPv6 link-local addresses (FE80::/10) are used for communication on a single local link. Automatically created using EUI-64 or randomly, or statically configured.\n\n```cisco\nRouter(config-if)# ipv6 address fe80::1 link-local\n```\n\n### Common Mistakes\n- Trying to route link-local traffic beyond the local router hop."),
    ("38-cisco-discovery-protocol-cdp.md", "Cisco Discovery Protocol (CDP)", "CDP is a proprietary Layer 2 protocol used to discover directly connected Cisco equipment.\n\n```cisco\nRouter(config)# cdp run\nRouter(config-if)# cdp enable\nRouter# show cdp neighbors detail\n```\n\n### Common Mistakes\n- Leaving CDP enabled on untrusted external interfaces, exposing internal topology to attackers."),
    ("39-link-layer-discovery-protocol-lldp.md", "Link Layer Discovery Protocol (LLDP)", "LLDP (IEEE 802.1AB) is an open-standard vendor-neutral neighbor discovery protocol.\n\n```cisco\nSwitch(config)# lldp run\nSwitch# show lldp neighbors\n```\n\n### Common Mistakes\n- Forgetting that LLDP must be enabled globally with `lldp run` before `show lldp neighbors` works."),
    ("40-ntp-network-time-protocol.md", "Network Time Protocol (NTP)", "NTP synchronizes clocks across network devices, crucial for syslog and security audits.\n\n```cisco\nRouter(config)# ntp server 192.168.1.100\nRouter# show ntp status\n```\n\n### Common Mistakes\n- Mismatched time zones causing log discrepancies between devices."),
    ("41-syslog-logging.md", "Syslog Message Severity Levels", "Syslog defines severity levels 0 (Emergency) to 7 (Debugging). Level 4 is Warnings, 5 is Notifications, 6 is Informational.\n\n```cisco\nRouter(config)# logging host 192.168.1.50\nRouter(config)# logging trap notifications\n```\n\n### Common Mistakes\n- Enabling `debug all` in production environments, crashing router CPU."),
    ("42-snmp-fundamentals.md", "SNMP Protocol and Management", "Simple Network Management Protocol monitors network health via MIBs and OIDs. SNMPv3 adds authentication and encryption.\n\n```cisco\nRouter(config)# snmp-server community public ro\n```\n\n### Common Mistakes\n- Using default community strings like `public` or `private` with read-write access."),
    ("43-password-recovery-router.md", "Cisco Router Password Recovery", "Password recovery changes configuration register to `0x2142` to bypass NVRAM startup-config.\n\n```cisco\nrommon 1> confreg 0x2142\nrommon 2> reset\n```\n\n### Common Mistakes\n- Forgetting to set config-register back to `0x2102` after recovering password."),
    ("44-password-recovery-switch.md", "Cisco Switch Password Recovery", "Password recovery on Catalyst switches involves holding Mode button during power-on and renaming `config.text`.\n\n```cisco\nswitch: rename flash:config.text flash:config.old\nswitch: boot\n```\n\n### Common Mistakes\n- Deleting `config.text` instead of renaming it, losing entire device configuration."),
    ("45-banner-motd.md", "Banner MOTD Security Notices", "Message of the Day (MOTD) banner displays legal warnings before login.\n\n```cisco\nRouter(config)# banner motd # AUTHORIZED ACCESS ONLY #\n```\n\n### Common Mistakes\n- Using a delimiter character inside the banner text, prematurely terminating the banner."),
    ("46-vtp-vlan-trunking-protocol.md", "VLAN Trunking Protocol (VTP)", "VTP synchronizes VLAN databases across switches in a VTP domain. Modes: Server, Client, Transparent, Off.\n\n```cisco\nSwitch(config)# vtp domain ciscodomain\nSwitch(config)# vtp mode transparent\n```\n\n### Common Mistakes\n- Connecting a switch with a higher revision number to an existing network, wiping all VLANs."),
    ("47-static-nat-webserver.md", "Static NAT for Inbound Web Servers", "Static NAT maps one public IP to one internal server IP.\n\n```cisco\nRouter(config)# ip nat inside source static 192.168.1.100 203.0.113.10\n```\n\n### Common Mistakes\n- Forgetting `ip nat inside` and `ip nat outside` on the corresponding interfaces."),
    ("48-dynamic-nat-pools.md", "Dynamic NAT with Public Address Pools", "Translates inside hosts into an available pool of public IPs.\n\n```cisco\nRouter(config)# ip nat pool PUBLIC_POOL 203.0.113.1 203.0.113.10 netmask 255.255.255.0\nRouter(config)# ip nat inside source list 1 pool PUBLIC_POOL\n```\n\n### Common Mistakes\n- Pool exhaustion when concurrent connections exceed pool size."),
    ("49-named-acls.md", "Named Access Control Lists", "Named ACLs allow editing specific sequence numbers and use human-readable identifiers.\n\n```cisco\nRouter(config)# ip access-list extended SECURE_WEB\nRouter(config-ext-nacl)# permit tcp 10.0.0.0 0.255.255.255 any eq 443\n```\n\n### Common Mistakes\n- Forgetting statement sequence numbers when inserting rules between existing lines."),
    ("50-routing-table-ad.md", "Administrative Distance (AD) Comparison", "AD defines trustworthiness of routing sources: Connected (0), Static (1), EIGRP internal (90), OSPF (110), RIP (120), External (170).\n\n```cisco\nRouter# show ip route\n```\n\n### Common Mistakes\n- Wondering why an OSPF route isn't in the table when a static route exists for the same subnet."),
    ("51-metric-vs-ad.md", "Administrative Distance vs Metric", "AD chooses between different routing protocols; Metric chooses between multiple paths within the same protocol.\n\n### Common Mistakes\n- Comparing OSPF cost directly to RIP hop count."),
    ("52-ospf-router-id.md", "OSPF Router ID Determination", "OSPF Router ID order of precedence: 1. Manual `router-id`, 2. Highest IP on active loopback, 3. Highest IP on active physical interface.\n\n```cisco\nRouter(config-router)# router-id 1.1.1.1\n```\n\n### Common Mistakes\n- Changing router-id without running `clear ip ospf process` to apply it."),
    ("53-ospf-dr-bdr.md", "OSPF DR and BDR Election", "Designated Router (DR) and Backup DR (BDR) minimize OSPF adjacencies on multiaccess broadcast networks.\n\n```cisco\nRouter(config-if)# ip ospf priority 255\n```\n\n### Common Mistakes\n- Forgetting that priority 0 prevents a router from ever becoming DR or BDR."),
    ("54-ospf-passive-interface.md", "OSPF Passive Interface", "Suppresses OSPF hello packets on an interface while still advertising its connected subnet into OSPF.\n\n```cisco\nRouter(config-router)# passive-interface GigabitEthernet0/0\n```\n\n### Common Mistakes\n- Setting a passive-interface on a link between two OSPF routers, breaking adjacency."),
    ("55-ospf-default-information-originate.md", "OSPF Default Route Propagation", "Propagates a default gateway route (0.0.0.0/0) to all OSPF neighbors.\n\n```cisco\nRouter(config-router)# default-information originate\n```\n\n### Common Mistakes\n- Forgetting that a default route must already exist in the routing table unless `always` is appended."),
    ("56-spanning-tree-pvst.md", "Per-VLAN Spanning Tree (PVST+)", "Cisco PVST+ maintains a separate STP instance per VLAN, allowing load balancing across trunks.\n\n```cisco\nSwitch(config)# spanning-tree mode pvst\n```\n\n### Common Mistakes\n- High switch CPU load with hundreds of active VLANs under PVST+."),
    ("57-rapid-pvst.md", "Rapid Per-VLAN Spanning Tree (RPVST+)", "RPVST+ (802.1w) provides sub-second convergence using proactive proposal-agreement handshakes.\n\n```cisco\nSwitch(config)# spanning-tree mode rapid-pvst\n```\n\n### Common Mistakes\n- Mixing 802.1D and 802.1w switches causing compatibility fallback delays."),
    ("58-switchport-voice-vlan.md", "Switchport Voice VLAN Configuration", "Transmits IP phone traffic on a tagged Voice VLAN while passing PC traffic on an untagged Data VLAN.\n\n```cisco\nSwitch(config-if)# switchport mode access\nSwitch(config-if)# switchport access vlan 10\nSwitch(config-if)# switchport voice vlan 150\n```\n\n### Common Mistakes\n- Configuring the phone port as a trunk port instead of using `switchport voice vlan`."),
    ("59-dhcp-snooping.md", "DHCP Snooping Security", "DHCP Snooping prevents rogue DHCP servers by categorizing ports as trusted or untrusted.\n\n```cisco\nSwitch(config)# ip dhcp snooping\nSwitch(config)# ip dhcp snooping vlan 10\nSwitch(config-if)# ip dhcp snooping trust\n```\n\n### Common Mistakes\n- Forgetting to trust the uplink port connecting to the legitimate DHCP server."),
    ("60-dynamic-arp-inspection.md", "Dynamic ARP Inspection (DAI)", "DAI validates ARP packets using DHCP snooping binding database to prevent ARP poisoning/spoofing.\n\n```cisco\nSwitch(config)# ip arp inspection vlan 10\n```\n\n### Common Mistakes\n- Enabling DAI without DHCP snooping or static ARP inspection lists."),
    ("61-ip-source-guard.md", "IP Source Guard", "Filters incoming traffic based on DHCP snooping database to prevent IP address spoofing.\n\n```cisco\nSwitch(config-if)# ip verify source\n```\n\n### Common Mistakes\n- Enabling IP Source Guard on trunk ports."),
    ("62-switch-virtual-terminal-vty.md", "Securing VTY Virtual Terminal Lines", "Restricts telnet/SSH access using access-class.\n\n```cisco\nRouter(config)# line vty 0 4\nRouter(config-line)# access-class 10 in\n```\n\n### Common Mistakes\n- Locking yourself out by misconfiguring access-class without permitting management IP."),
    ("63-service-password-encryption.md", "Service Password Encryption", "Encrypts plaintext passwords in running-config with weak Type 7 reversible obfuscation.\n\n```cisco\nRouter(config)# service password-encryption\n```\n\n### Common Mistakes\n- Relying on Type 7 passwords for strong security instead of Type 8 or 9 (PBKDF2/scrypt)."),
    ("64-enable-secret-vs-password.md", "Enable Secret vs Enable Password", "`enable secret` uses secure MD5/SHA-256 hash (Type 5/8/9) and supersedes `enable password`.\n\n```cisco\nRouter(config)# enable secret Cisco123!\n```\n\n### Common Mistakes\n- Setting `enable password` and `enable secret` to the same string, causing an error."),
    ("65-duplex-and-speed-mismatches.md", "Duplex and Speed Mismatches", "Mismatched duplex (Half vs Full) causes late collisions, FCS errors, and packet throughput drops.\n\n```cisco\nSwitch(config-if)# speed auto\nSwitch(config-if)# duplex auto\n```\n\n### Common Mistakes\n- Hardcoding full duplex on one side while leaving auto-negotiation on the other."),
    ("66-traceroute-operation.md", "Traceroute Operation and Troubleshooting", "Traceroute uses incrementing IP TTL values (starting at 1) to identify each Layer 3 hop.\n\n```cisco\nRouter# traceroute 192.168.2.10\n```\n\n### Common Mistakes\n- Confusing asterisks `* * *` with total packet loss; firewalls frequently drop TTL-expired ICMP messages."),
    ("67-interface-status-codes.md", "Deciphering Interface Status Codes", "Understanding combinations: `up/up` (healthy), `down/down` (cable unplugged), `up/down` (keepalive/framing issue), `administratively down` (shutdown).\n\n### Common Mistakes\n- Troubleshooting IP routing when the interface is administratively down."),
    ("68-arp-table-troubleshooting.md", "Address Resolution Protocol (ARP) Diagnostics", "ARP maps IPv4 addresses to Layer 2 MAC addresses.\n\n```cisco\nRouter# show ip arp\nRouter# clear ip arp-cache\n```\n\n### Common Mistakes\n- Assuming switches maintain ARP tables for all traffic (switches maintain MAC address tables; only routers and SVIs maintain ARP tables)."),
    ("69-mac-address-table-learning.md", "Switch MAC Address Learning Process", "Switches populate MAC table by inspecting source MAC of incoming frames and forward using destination MAC.\n\n```cisco\nSwitch# show mac address-table\nSwitch# clear mac address-table dynamic\n```\n\n### Common Mistakes\n- Confusing ARP table (IP to MAC) with MAC table (MAC to switch port)."),
    ("70-broadcast-storm-control.md", "Broadcast Storm Control", "Prevents network degradation from excessive broadcast, multicast, or unicast traffic.\n\n```cisco\nSwitch(config-if)# storm-control broadcast level 20.0\n```\n\n### Common Mistakes\n- Setting threshold too low, blocking legitimate ARP and DHCP broadcasts."),
    ("71-layer3-etherchannel.md", "Routed Layer 3 EtherChannel", "Bundles router or multilayer switch interfaces into a routed link with an IP address.\n\n```cisco\nSwitch(config-if-range)# no switchport\nSwitch(config-if-range)# channel-group 1 mode active\nSwitch(config)# interface port-channel 1\nSwitch(config-if)# no switchport\nSwitch(config-if)# ip address 10.0.0.1 255.255.255.252\n```\n\n### Common Mistakes\n- Forgetting `no switchport` on both member interfaces and the port-channel interface."),
    ("72-dns-configuration-ios.md", "DNS Client Configuration on Cisco IOS", "Enables domain name resolution on Cisco routers.\n\n```cisco\nRouter(config)# ip domain-lookup\nRouter(config)# ip name-server 8.8.8.8 1.1.1.1\n```\n\n### Common Mistakes\n- Typos in commands causing router to hang trying to resolve typo via broadcast DNS when `ip domain-lookup` is enabled."),
    ("73-disable-domain-lookup.md", "Disabling DNS Lookup for Typos", "Prevents CLI freezes when mistyping commands.\n\n```cisco\nRouter(config)# no ip domain-lookup\n```\n\n### Common Mistakes\n- Forgetting to re-enable domain lookup if the router legitimately requires DNS resolution."),
    ("74-logging-synchronous.md", "Logging Synchronous on Console", "Prevents console log messages from disrupting currently typed commands.\n\n```cisco\nRouter(config)# line console 0\nRouter(config-line)# logging synchronous\nRouter(config)# line vty 0 4\nRouter(config-line)# logging synchronous\n```\n\n### Common Mistakes\n- Forgetting to apply `logging synchronous` to both console and VTY lines."),
    ("75-exec-timeout.md", "Console and VTY Exec-Timeout", "Sets session inactivity disconnect timer.\n\n```cisco\nRouter(config-line)# exec-timeout 10 0\n! Disable timeout for lab sessions:\nRouter(config-line)# exec-timeout 0 0\n```\n\n### Common Mistakes\n- Setting `exec-timeout 0 0` in production environments, leaving open terminals accessible."),
    ("76-copy-run-start.md", "Saving Cisco IOS Configurations", "Saves volatile DRAM running-config to non-volatile NVRAM startup-config.\n\n```cisco\nRouter# copy running-config startup-config\n! Shortcut:\nRouter# write memory\n```\n\n### Common Mistakes\n- Reloading or rebooting router before saving configuration, losing all lab changes."),
    ("77-packet-tracer-simulation-mode.md", "Packet Tracer Simulation Mode", "Allows step-by-step frame inspection across OSI model layers (Layer 1 to Layer 7 PDU header details).\n\n### Common Mistakes\n- Forgetting event filters, overwhelming simulation event list with STP and CDP packets."),
    ("78-packet-tracer-cluster-feature.md", "Clustering Subnets in Packet Tracer", "Groups complex topologies into clean hierarchical visual containers.\n\n### Common Mistakes\n- Hiding broken links inside clusters, complicating troubleshooting."),
    ("79-packet-tracer-activity-wizard.md", "Packet Tracer Assessment & Labs", "Packet Tracer Activity Wizard enables instructors to author self-grading lab tasks and test topology states.\n\n### Common Mistakes\n- Locking initial configs with passwords students cannot recover."),
    ("80-packet-tracer-mcp-bridge.md", "Packet Tracer MCP Live Automation Bridge", "Connects external LLM agents and scripts to Cisco Packet Tracer Script Engine via local WebSocket or HTTP bridge.\n\n```json\n{\"command\": \"runScript\", \"script\": \"addDevice('R1', '2911', 200, 200);\"}\n```\n\n### Common Mistakes\n- Running bridge on wrong port or failing to enable Script Modules inside Packet Tracer extensions.")
]

for fname, title, content in EXTRA_TOPICS:
    DOCS.append((fname, title, f"# {title}\n\n{content}\n"))

for fname, title, content in DOCS:
    fpath = os.path.join(KNOWLEDGE_DIR, fname)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

print(f"Successfully generated {len(DOCS)} CCNA knowledge documents in {KNOWLEDGE_DIR}")
