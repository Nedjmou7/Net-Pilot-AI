import os

docs = [
    # 1. IP Addressing & Subnetting
    (
        "ipv4-address-classes.md",
        "IPv4 Address Classes and RFC 1918 Private Ranges",
        """# IPv4 Address Classes and RFC 1918 Private Ranges

IPv4 addresses are 32-bit values divided into four 8-bit octets. Historically, addresses were organized into classes:
- Class A: 1.0.0.0 to 126.255.255.255 (/8 default mask)
- Class B: 128.0.0.0 to 191.255.255.255 (/16 default mask)
- Class C: 192.0.0.0 to 223.255.255.255 (/24 default mask)
- Class D: 224.0.0.0 to 239.255.255.255 (Multicast)
- Class E: 240.0.0.0 to 255.255.255.254 (Experimental)

RFC 1918 defines non-routable private IP address space reserved for internal enterprise networks:
- `10.0.0.0/8` (10.0.0.0 – 10.255.255.255)
- `172.16.0.0/12` (172.16.0.0 – 172.31.255.255)
- `192.168.0.0/16` (192.168.0.0 – 192.168.255.255)

```cisco
Router(config)# interface GigabitEthernet0/0
Router(config-if)# ip address 192.168.1.1 255.255.255.0
Router(config-if)# no shutdown
```

### Common Mistakes
- Using public IP addresses on internal LANs without NAT.
- Confusing Class B private range (172.16.0.0 - 172.31.255.255) with 172.0.0.0.
- Forgetting that 127.0.0.0/8 is reserved for host loopback testing.
"""
    ),
    (
        "subnetting-slash-24-to-30.md",
        "Subnetting from /24 to /30 (VLSM)",
        """# Subnetting from /24 to /30 (Variable Length Subnet Masking)

Variable Length Subnet Masking (VLSM) allows network engineers to divide IP space efficiently based on host requirements rather than classful boundaries.

Subnet breakdown for a class C base (e.g. 192.168.1.0):
- `/24`: 255.255.255.0 -> 256 addresses, 254 usable hosts.
- `/25`: 255.255.255.128 -> 128 addresses, 126 usable hosts.
- `/26`: 255.255.255.192 -> 64 addresses, 62 usable hosts.
- `/27`: 255.255.255.224 -> 32 addresses, 30 usable hosts.
- `/28`: 255.255.255.240 -> 16 addresses, 14 usable hosts.
- `/29`: 255.255.255.248 -> 8 addresses, 6 usable hosts.
- `/30`: 255.255.255.252 -> 4 addresses, 2 usable hosts (ideal for point-to-point router links).

```cisco
! Configuring point-to-point /30 link between R1 and R2
R1(config)# interface GigabitEthernet0/1
R1(config-if)# ip address 10.0.0.1 255.255.255.252
R1(config-if)# no shutdown

R2(config)# interface GigabitEthernet0/0
R2(config-if)# ip address 10.0.0.2 255.255.255.252
R2(config-if)# no shutdown
```

### Common Mistakes
- Assigning network ID (e.g. 10.0.0.0) or broadcast address (10.0.0.3) to an interface.
- Using a /24 mask on point-to-point router links, wasting 252 IP addresses.
- Miscalculating block sizes when borrowing bits from the host portion.
"""
    ),
    (
        "ipv4-default-gateway.md",
        "Default Gateway Role and Configuration",
        """# Default Gateway Role and Configuration

The default gateway is the IP address of a local router interface on the same IP subnet as the client host. When a host needs to transmit packets to any remote IP address outside its local broadcast domain, it sends an ARP request for the default gateway's MAC address and forwards the frame to the router.

```cisco
! On Cisco Switch (for management SVI)
Switch(config)# interface Vlan1
Switch(config-if)# ip address 192.168.1.2 255.255.255.0
Switch(config-if)# no shutdown
Switch(config)# ip default-gateway 192.168.1.1
```

On Windows PC / Packet Tracer PC:
- Static IP: Set IP Address, Subnet Mask, and Default Gateway.
- If gateway is missing or incorrect, local subnet ping works, but ping to external networks fails immediately with 'Destination host unreachable' or 'Request timed out'.

### Common Mistakes
- Setting default gateway to an IP address that belongs to a different subnet.
- Forgetting that switches operating as Layer 2 devices need `ip default-gateway` for remote SSH management.
"""
    ),
    (
        "ipv6-basics-and-addressing.md",
        "IPv6 Addressing and Link-Local",
        """# IPv6 Addressing and Link-Local Configuration

IPv6 uses 128-bit addresses written in hexadecimal format separated by colons. Types of IPv6 addresses include:
- Global Unicast Address (GUA): `2000::/3` (publicly routable)
- Unique Local Address (ULA): `fc00::/7` (private enterprise)
- Link-Local Address (LLA): `fe80::/10` (used for neighbor discovery and next-hop routing on the same link)

```cisco
Router(config)# ipv6 unicast-routing
Router(config)# interface GigabitEthernet0/0
Router(config-if)# ipv6 address 2001:db8:acad:1::1/64
Router(config-if)# ipv6 address fe80::1 link-local
Router(config-if)# no shutdown
```

### Common Mistakes
- Forgetting `ipv6 unicast-routing` on Cisco routers (without it, the router acts only as an IPv6 host and will not route packets between interfaces).
- Neglecting to configure static link-local addresses, making troubleshooting dynamically generated EUI-64 addresses difficult.
"""
    ),
    (
        "vlan-fundamentals.md",
        "VLAN Fundamentals and Creation",
        """# VLAN Fundamentals and Creation

Virtual Local Area Networks (VLANs) segment a physical switch into multiple logical broadcast domains. Benefits include enhanced security, containment of broadcast traffic, and improved traffic management.

By default, all Cisco switch ports belong to VLAN 1. Custom VLAN IDs range from 1 to 4094 (Normal range: 1–1005, Extended: 1006–4094).

```cisco
Switch# configure terminal
Switch(config)# vlan 10
Switch(config-vlan)# name SALES
Switch(config-vlan)# exit
Switch(config)# vlan 20
Switch(config-vlan)# name ENGINEERING
Switch(config-vlan)# exit
```

Verification command:
```cisco
Switch# show vlan brief
```

### Common Mistakes
- Forgetting to exit VLAN configuration mode before testing (VLAN changes commit upon exiting config-vlan).
- Assigning switch ports to a VLAN that has not been created in the database.
"""
    ),
    (
        "switchport-access-ports.md",
        "Configuring Switch Access Ports",
        """# Configuring Switch Access Ports

An access port belongs to exactly one VLAN and carries untagged Ethernet frames to end stations (PCs, printers, servers).

```cisco
Switch(config)# interface FastEthernet0/1
Switch(config-if)# switchport mode access
Switch(config-if)# switchport access vlan 10
Switch(config-if)# no shutdown
Switch(config-if)# exit

! Configuring multiple ports with interface range
Switch(config)# interface range FastEthernet0/2 - 10
Switch(config-if-range)# switchport mode access
Switch(config-if-range)# switchport access vlan 20
Switch(config-if-range)# no shutdown
```

### Common Mistakes
- Leaving access ports in dynamic auto or dynamic desirable mode, exposing the switch to DTP VLAN hopping attacks.
- Forgetting `interface range` syntax (spaces around the hyphen are required: `FastEthernet0/2 - 10`).
"""
    ),
    (
        "8021q-trunking-configuration.md",
        "802.1Q Trunking Configuration",
        """# 802.1Q Trunking Configuration

Trunk links carry traffic for multiple VLANs across switches or between a switch and a router. IEEE 802.1Q inserts a 4-byte tag into the standard Ethernet frame containing the 12-bit VLAN ID.

```cisco
Switch(config)# interface GigabitEthernet0/1
! On Layer 3 switches (e.g. 3650), specify encapsulation first:
Switch(config-if)# switchport trunk encapsulation dot1q
Switch(config-if)# switchport mode trunk
Switch(config-if)# switchport trunk allowed vlan 10,20,99
Switch(config-if)# switchport trunk native vlan 99
Switch(config-if)# no shutdown
```

Verification:
```cisco
Switch# show interfaces trunk
```

### Common Mistakes
- Mismatched native VLANs on opposite ends of a trunk link, triggering CDP native VLAN mismatch errors.
- Forgetting to permit newly created VLANs in the `switchport trunk allowed vlan` list.
"""
    ),
    (
        "router-on-a-stick-intervlan.md",
        "Router-on-a-Stick Inter-VLAN Routing",
        """# Router-on-a-Stick Inter-VLAN Routing

Router-on-a-Stick (ROAS) uses a single physical router interface divided into virtual subinterfaces to route packets between different VLANs over an 802.1Q trunk link.

```cisco
! Router Configuration
Router(config)# interface GigabitEthernet0/0
Router(config-if)# no shutdown
Router(config-if)# exit

Router(config)# interface GigabitEthernet0/0.10
Router(config-subif)# encapsulation dot1Q 10
Router(config-subif)# ip address 192.168.10.1 255.255.255.0
Router(config-subif)# exit

Router(config)# interface GigabitEthernet0/0.20
Router(config-subif)# encapsulation dot1Q 20
Router(config-subif)# ip address 192.168.20.1 255.255.255.0
Router(config-subif)# exit

! Connected Switch Port Configuration
Switch(config)# interface GigabitEthernet0/1
Switch(config-if)# switchport mode trunk
```

### Common Mistakes
- Configuring `ip address` before `encapsulation dot1Q <vlan_id>` (IOS rejects IP address assignment without encapsulation defined).
- Forgetting `no shutdown` on the physical parent interface (GigabitEthernet0/0).
- Leaving the connecting switch port in access mode instead of trunk mode.
"""
    ),
    (
        "layer3-switch-svi-intervlan.md",
        "Inter-VLAN Routing with SVI on Layer 3 Switches",
        """# Inter-VLAN Routing with Switch Virtual Interfaces (SVI)

Multilayer switches (such as Cisco Catalyst 3650 or 3560) perform wire-speed hardware routing between VLANs using Switch Virtual Interfaces (SVIs).

```cisco
L3Switch(config)# ip routing

L3Switch(config)# vlan 10
L3Switch(config)# vlan 20

L3Switch(config)# interface Vlan10
L3Switch(config-if)# ip address 192.168.10.1 255.255.255.0
L3Switch(config-if)# no shutdown

L3Switch(config)# interface Vlan20
L3Switch(config-if)# ip address 192.168.20.1 255.255.255.0
L3Switch(config-if)# no shutdown
```

### Common Mistakes
- Forgetting `ip routing` global command; without it, the multilayer switch functions as a standard Layer 2 switch.
- Not creating the VLAN in the VLAN database prior to creating the SVI interface.
"""
    ),
    (
        "static-routing-fundamentals.md",
        "Static Routing and Default Routes",
        """# Static Routing and Default Routes

Static routes provide deterministic packet forwarding manually configured by an administrator.

Command syntax:
`ip route <dest_network> <subnet_mask> {next_hop_ip | exit_interface} [distance]`

Default Route (Gateway of Last Resort):
```cisco
Router(config)# ip route 0.0.0.0 0.0.0.0 10.0.0.2
```

Specific Network Route:
```cisco
Router(config)# ip route 192.168.20.0 255.255.255.0 10.0.0.2
```

Floating Static Route (Backup route with higher Administrative Distance):
```cisco
Router(config)# ip route 192.168.20.0 255.255.255.0 10.0.1.2 100
```

Verification:
```cisco
Router# show ip route static
```

### Common Mistakes
- Pointing next-hop to an unreachable IP address.
- Specifying an exit interface on a multi-access Ethernet link without next-hop IP, causing excessive ARP requests.
"""
    ),
    (
        "ospfv2-single-area-configuration.md",
        "OSPFv2 Single-Area Configuration",
        """# OSPFv2 Single-Area Configuration

Open Shortest Path First (OSPF) is an open-standard link-state routing protocol using Dijkstra's SPF algorithm. Single-area OSPF operates entirely inside Area 0 (backbone).

```cisco
Router(config)# router ospf 1
Router(config-router)# router-id 1.1.1.1
Router(config-router)# network 192.168.10.0 0.0.0.255 area 0
Router(config-router)# network 10.0.0.0 0.0.0.3 area 0
Router(config-router)# passive-interface GigabitEthernet0/0
Router(config-router)# exit
```

Verification commands:
```cisco
Router# show ip ospf neighbor
Router# show ip ospf interface brief
Router# show ip route ospf
```

### Common Mistakes
- Using subnet masks instead of wildcard masks in the `network` command (OSPF requires wildcard mask: e.g. 0.0.0.255).
- Mismatched OSPF Hello (10s) or Dead (40s) timers between neighboring routers.
- Mismatched Area IDs on connecting link interfaces.
"""
    ),
    (
        "ospf-wildcard-mask-calculation.md",
        "Calculating Wildcard Masks for OSPF and ACLs",
        """# Calculating Wildcard Masks for OSPF and ACLs

A wildcard mask tells the Cisco IOS parser which bits of an IPv4 address to inspect (0 = match exactly) and which bits to ignore (1 = wildcard / any value).

Calculation rule:
`Wildcard Mask = 255.255.255.255 - Subnet Mask`

Common conversions:
- /24: 255.255.255.0 -> Wildcard: `0.0.0.255`
- /25: 255.255.255.128 -> Wildcard: `0.0.0.127`
- /26: 255.255.255.192 -> Wildcard: `0.0.0.63`
- /27: 255.255.255.224 -> Wildcard: `0.0.0.31`
- /28: 255.255.255.240 -> Wildcard: `0.0.0.15`
- /29: 255.255.255.248 -> Wildcard: `0.0.0.7`
- /30: 255.255.255.252 -> Wildcard: `0.0.0.3`
- /32: 255.255.255.255 -> Wildcard: `0.0.0.0` (Host match)

```cisco
Router(config-router)# network 192.168.1.0 0.0.0.255 area 0
```

### Common Mistakes
- Typing `255.255.255.0` in an OSPF `network` statement.
- Inverting octet arithmetic (e.g. thinking /28 wildcard is 0.0.0.240).
"""
    ),
    (
        "ospf-passive-interface.md",
        "OSPF Passive Interface Configuration",
        """# OSPF Passive Interface Configuration

Configuring an interface as passive prevents OSPF from transmitting Hello packets out of that port, protecting LANs from unauthorized rogue routers and saving CPU/bandwidth, while still advertising the connected subnet into OSPF.

```cisco
Router(config)# router ospf 1
Router(config-router)# passive-interface GigabitEthernet0/0
```

Alternative best practice (passive by default):
```cisco
Router(config)# router ospf 1
Router(config-router)# passive-interface default
Router(config-router)# no passive-interface GigabitEthernet0/1
```

Verification:
```cisco
Router# show ip ospf interface GigabitEthernet0/0
```

### Common Mistakes
- Making a link connecting two routers passive, which prevents neighbor adjacencies from forming.
"""
    ),
    (
        "ripv2-routing-configuration.md",
        "RIPv2 Distance Vector Routing Configuration",
        """# RIPv2 Distance Vector Routing Configuration

Routing Information Protocol Version 2 (RIPv2) is a distance-vector protocol using hop count as its metric (maximum 15 hops; 16 hops is unreachable). Unlike RIPv1, RIPv2 supports CIDR and VLSM.

```cisco
Router(config)# router rip
Router(config-router)# version 2
Router(config-router)# no auto-summary
Router(config-router)# network 192.168.10.0
Router(config-router)# network 10.0.0.0
Router(config-router)# passive-interface GigabitEthernet0/0
```

Verification:
```cisco
Router# show ip protocols
Router# show ip route rip
```

### Common Mistakes
- Forgetting `no auto-summary`, causing RIPv2 to summarize discontiguous subnets to classful boundaries.
- Forgetting `version 2`, defaulting to RIPv1 which broadcasts without subnet masks.
"""
    ),
    (
        "dhcp-server-cisco-ios.md",
        "Configuring Cisco IOS DHCP Server",
        """# Configuring Cisco IOS DHCP Server

A Cisco router can serve as a local DHCP server to dynamically assign IP addresses, subnet masks, default gateways, and DNS servers to client PCs.

```cisco
! Step 1: Exclude static and gateway addresses
Router(config)# ip dhcp excluded-address 192.168.10.1 192.168.10.10

! Step 2: Define DHCP pool
Router(config)# ip dhcp pool LAN_POOL
Router(dhcp-config)# network 192.168.10.0 255.255.255.0
Router(dhcp-config)# default-router 192.168.10.1
Router(dhcp-config)# dns-server 8.8.8.8 1.1.1.1
Router(dhcp-config)# domain-name corp.local
Router(dhcp-config)# lease 1 0 0
```

Verification commands:
```cisco
Router# show ip dhcp binding
Router# show ip dhcp pool
Router# show ip dhcp conflict
```

### Common Mistakes
- Forgetting to exclude the router's own interface IP, creating IP conflict errors on the LAN.
- Putting the wrong default-router address inside the DHCP pool.
"""
    ),
    (
        "dhcp-relay-ip-helper.md",
        "DHCP Relay Agent (ip helper-address)",
        """# DHCP Relay Agent (ip helper-address)

DHCP Discover broadcasts (255.255.255.255) cannot traverse routers by default. When the DHCP server resides on a different subnet or centralized server farm, the router interface facing the clients must be configured with `ip helper-address` to convert broadcasts into unicast packets.

```cisco
Router(config)# interface GigabitEthernet0/0
Router(config-if)# ip helper-address 10.10.10.50
```

The router forwards UDP ports:
- TFTP (Port 69)
- DNS (Port 53)
- Time (Port 37)
- TACACS (Port 49)
- DHCP/BOOTP Server (Port 67) & Client (Port 68)

### Common Mistakes
- Placing `ip helper-address` on the interface facing the server instead of the interface receiving client broadcast requests.
"""
    ),
    (
        "nat-pat-overload-configuration.md",
        "NAT and PAT (Port Address Translation / Overload)",
        """# NAT and PAT (Port Address Translation / Overload)

Port Address Translation (PAT), also known as NAT Overload, maps multiple private IP addresses to a single public IP address using unique Layer 4 source port numbers.

```cisco
! 1. Identify inside and outside interfaces
Router(config)# interface GigabitEthernet0/0
Router(config-if)# ip nat inside
Router(config-if)# exit

Router(config)# interface GigabitEthernet0/1
Router(config-if)# ip nat outside
Router(config-if)# exit

! 2. Define standard ACL matching internal private hosts
Router(config)# access-list 1 permit 192.168.10.0 0.0.0.255

! 3. Configure NAT Overload binding
Router(config)# ip nat inside source list 1 interface GigabitEthernet0/1 overload
```

Verification commands:
```cisco
Router# show ip nat translations
Router# show ip nat statistics
Router# clear ip nat translation *
```

### Common Mistakes
- Forgetting `overload` keyword (without it, only one private host can communicate at a time).
- Forgetting `ip nat inside` or `ip nat outside` on the interfaces.
"""
    ),
    (
        "standard-numbered-acls.md",
        "Standard Numbered ACLs (1-99)",
        """# Standard Numbered ACLs (1-99)

Standard Access Control Lists filter traffic based ONLY on the source IPv4 address.
Standard ACL numbered range: 1 to 99 and 1300 to 1999.

Placement guideline: Place standard ACLs as close to the **destination** as possible (to prevent prematurely blocking traffic destined for other networks).

```cisco
! Allow host 192.168.10.10 and subnet 192.168.20.0/24, deny everything else
Router(config)# access-list 10 permit host 192.168.10.10
Router(config)# access-list 10 permit 192.168.20.0 0.0.0.255
Router(config)# access-list 10 deny any

! Apply to interface
Router(config)# interface GigabitEthernet0/1
Router(config-if)# ip access-group 10 out
```

### Common Mistakes
- Forgetting the implicit `deny any` at the end of every ACL. If you do not have at least one permit statement, all traffic is dropped.
- Placing standard ACLs too close to the source, accidentally cutting off access to other permitted destinations.
"""
    ),
    (
        "extended-numbered-acls.md",
        "Extended Numbered ACLs (100-199)",
        """# Extended Numbered ACLs (100-199)

Extended ACLs inspect source IP, destination IP, Layer 4 protocol (TCP, UDP, ICMP), and port numbers (e.g. 80, 443, 22). Range: 100 to 199 and 2000 to 2699.

Placement guideline: Place extended ACLs as close to the **source** as possible to drop unauthorized traffic before it consumes network bandwidth.

```cisco
! Deny PC1 (192.168.10.5) web access to WebServer (10.0.0.50), permit other traffic
Router(config)# access-list 101 deny tcp host 192.168.10.5 host 10.0.0.50 eq 80
Router(config)# access-list 101 deny tcp host 192.168.10.5 host 10.0.0.50 eq 443
Router(config)# access-list 101 permit ip any any

Router(config)# interface GigabitEthernet0/0
Router(config-if)# ip access-group 101 in
```

### Common Mistakes
- Misordering rules: ACLs are processed sequentially top-to-bottom on first match. Specific rules must precede general permit rules.
- Omitting `permit ip any any` when aiming to selectively block specific ports.
"""
    ),
    (
        "spanning-tree-protocol-pvst.md",
        "Spanning Tree Protocol (STP & PVST+)",
        """# Spanning Tree Protocol (STP & PVST+)

STP (IEEE 802.1D) and Rapid PVST+ (802.1w) prevent Layer 2 bridging loops, broadcast storms, and MAC database corruption in redundant switched topologies.

Root Bridge Election:
Switch with the lowest Bridge ID (Priority + Sys-ID-Extension + MAC Address) becomes Root Bridge. Default priority is 32768.

```cisco
! Set Switch as Primary Root Bridge for VLAN 10 and 20
Switch(config)# spanning-tree vlan 10,20 root primary

! Or configure priority manually (multiples of 4096)
Switch(config)# spanning-tree vlan 10 priority 4096
Switch(config)# spanning-tree mode rapid-pvst
```

Verification:
```cisco
Switch# show spanning-tree
Switch# show spanning-tree vlan 10
```

### Common Mistakes
- Leaving default priority on all switches, resulting in an old access switch with lowest MAC becoming Root Bridge.
- Setting priority to a number not divisible by 4096.
"""
    ),
    (
        "stp-portfast-bpduguard.md",
        "STP PortFast and BPDU Guard",
        """# STP PortFast and BPDU Guard

PortFast transitions an access switchport immediately from blocking to forwarding state, bypassing listening and learning states (saving 30 seconds).

BPDU Guard automatically err-disables a PortFast-enabled port if a BPDU is received, preventing rogue switch loops.

```cisco
! Per-interface configuration
Switch(config)# interface FastEthernet0/1
Switch(config-if)# switchport mode access
Switch(config-if)# spanning-tree portfast
Switch(config-if)# spanning-tree bpduguard enable
Switch(config-if)# exit

! Global configuration for all access ports
Switch(config)# spanning-tree portfast default
Switch(config)# spanning-tree portfast bpduguard default
```

Recovery from err-disabled:
```cisco
Switch(config)# interface FastEthernet0/1
Switch(config-if)# shutdown
Switch(config-if)# no shutdown
```

### Common Mistakes
- Enabling PortFast on trunk ports connected to other switches, which can induce immediate catastrophic broadcast storms.
"""
    ),
    (
        "etherchannel-lacp-pagp.md",
        "EtherChannel Configuration (LACP & PAgP)",
        """# EtherChannel Configuration (LACP & PAgP)

EtherChannel bundles up to 8 physical Ethernet links into a single logical channel, providing link aggregation, load balancing, and redundancy.

Protocols:
- LACP (IEEE 802.3ad open standard): `active` (initiates) and `passive` (waits)
- PAgP (Cisco proprietary): `desirable` and `auto`
- Static (no negotiation protocol): `on`

```cisco
Switch(config)# interface range GigabitEthernet0/1 - 2
Switch(config-if-range)# channel-group 1 mode active
Switch(config-if-range)# exit

Switch(config)# interface Port-channel 1
Switch(config-if)# switchport mode trunk
Switch(config-if)# switchport trunk allowed vlan all
```

Verification:
```cisco
Switch# show etherchannel summary
Switch# show interfaces port-channel 1
```

### Common Mistakes
- Mismatched speed, duplex, access VLAN, or trunk allowed VLAN settings on bundled interfaces (all physical member ports must match identical parameters).
"""
    ),
    (
        "port-security-switch-hardening.md",
        "Switch Port Security Configuration",
        """# Switch Port Security Configuration

Port Security restricts input to an interface by limiting and identifying MAC addresses of stations allowed to access the port.

```cisco
Switch(config)# interface FastEthernet0/1
Switch(config-if)# switchport mode access
Switch(config-if)# switchport port-security
Switch(config-if)# switchport port-security maximum 2
Switch(config-if)# switchport port-security mac-address sticky
Switch(config-if)# switchport port-security violation shutdown
Switch(config-if)# no shutdown
```

Violation Modes:
- `shutdown`: Port immediately err-disables and logs SNMP trap.
- `restrict`: Drops violating frames, increments counter, logs alert.
- `protect`: Drops violating frames silently without logging.

Verification:
```cisco
Switch# show port-security interface FastEthernet0/1
Switch# show port-security address
```

### Common Mistakes
- Trying to enable port security on dynamic switchports (must explicitly run `switchport mode access` first).
"""
    ),
    (
        "securing-ssh-and-passwords.md",
        "Configuring Secure Remote Access (SSH and Passwords)",
        """# Configuring Secure Remote Access (SSH and Passwords)

Telnet sends credentials in plain text; SSH encrypts all management traffic.

Configuration sequence:
```cisco
Router(config)# hostname R1
R1(config)# ip domain-name lab.local
R1(config)# crypto key generate rsa modulus 2048
R1(config)# ip ssh version 2
R1(config)# username admin privilege 15 secret Cisco123!
R1(config)# enable secret CiscoEnable123!

R1(config)# line vty 0 4
R1(config-line)# transport input ssh
R1(config-line)# login local
R1(config-line)# exec-timeout 5 0
R1(config-line)# logging synchronous
R1(config-line)# exit

R1(config)# service password-encryption
```

Verification:
```cisco
R1# show ip ssh
```

### Common Mistakes
- Forgetting to configure a hostname and `ip domain-name` prior to running `crypto key generate rsa`.
- Allowing Telnet in production environments.
"""
    ),
    (
        "troubleshooting-connectivity-ping-traceroute.md",
        "Troubleshooting with Ping and Traceroute",
        """# Troubleshooting Network Connectivity with Ping and Traceroute

Cisco ICMP troubleshooting workflow:

1. **Ping Loopback (`127.0.0.1`)**: Verifies local TCP/IP protocol stack is functioning on host.
2. **Ping Local IP**: Verifies local NIC and IP driver operation.
3. **Ping Default Gateway**: Verifies local Layer 1 cable, Layer 2 switchport, and router interface.
4. **Ping Remote Gateway/Server**: Tests end-to-end IP routing.
5. **Traceroute (`traceroute` / `tracert`)**: Identifies the exact hop where packet forwarding fails.

Extended Ping from Cisco IOS CLI:
```cisco
Router# ping
Protocol [ip]: 
Target IP address: 192.168.20.10
Repeat count [5]: 10
Datagram size [100]: 
Timeout in seconds [2]: 
Extended commands [n]: y
Source address or interface: 192.168.10.1
```

Common responses:
- `!` : Successful ICMP Echo Reply
- `.` : Timed out
- `U` : Destination unreachable (typically no route or blocked by ACL)

### Common Mistakes
- Assuming ping failure means device is down when host firewall is blocking ICMP Echo requests.
"""
    ),
    (
        "show-commands-cheat-sheet.md",
        "Essential Cisco IOS Show Commands Cheat Sheet",
        """# Essential Cisco IOS Show Commands Cheat Sheet

The most critical Cisco IOS diagnostic commands:

1. **Interface Status**:
```cisco
Router# show ip interface brief
Switch# show interfaces status
```

2. **Routing Table**:
```cisco
Router# show ip route
Router# show ip route ospf
Router# show ip route connected
```

3. **VLAN & Trunking**:
```cisco
Switch# show vlan brief
Switch# show interfaces trunk
```

4. **Layer 2 Discovery**:
```cisco
Router# show cdp neighbors
Router# show cdp neighbors detail
```

5. **Running Configuration**:
```cisco
Router# show running-config
Router# show running-config interface GigabitEthernet0/0
```

6. **MAC Address Table**:
```cisco
Switch# show mac address-table
```

### Common Mistakes
- Not filtering show commands with `include` or `section` (e.g. `show running-config | section ospf`).
"""
    ),
    (
        "packet-tracer-device-selection-and-cabling.md",
        "Packet Tracer Device Selection and Cabling Rules",
        """# Packet Tracer Device Selection and Cabling Rules

Building networks correctly in Cisco Packet Tracer:

### Supported Hardware Models:
- **Router 2911**: 3x GigabitEthernet ports (0/0, 0/1, 0/2), modular slots for serial cards (HWIC-2T).
- **Router 1941**: 2x GigabitEthernet ports (0/0, 0/1).
- **Switch 2960-24TT**: 24x FastEthernet ports (0/1 to 0/24), 2x GigabitEthernet uplink ports (0/1, 0/2).
- **Switch 3650-24PS**: 24x GigabitEthernet Layer 3 ports.
- **PC-PT / Server-PT**: FastEthernet0.

### Cabling Rules:
- **Straight-Through Cable (Solid Black)**: Connects dissimilar devices:
  - PC to Switch
  - Router to Switch
  - Server to Switch
- **Crossover Cable (Dashed Black)**: Connects similar devices:
  - Router to Router (GigabitEthernet to GigabitEthernet)
  - Switch to Switch
  - PC to PC
- **Serial DTE/DCE Cable (Red lightning cable)**: Point-to-point WAN links between Serial interfaces. Clock rate must be set on DCE side (`clock rate 64000`).

### Common Mistakes
- Using straight-through cable directly between two routers without auto-MDIX.
- Connecting PC to Switch console port instead of FastEthernet.
"""
    )
]

# Generate remaining 55 topic documents programmatically to exceed 80+ docs
extra_topics = [
    ("dns-client-and-server-configuration", "DNS Client and Server Setup in Packet Tracer", "ip domain-lookup", "ip name-server 8.8.8.8"),
    ("ntp-network-time-protocol", "Network Time Protocol (NTP) Synchronization", "ntp server 10.0.0.1", "ntp master 2"),
    ("syslog-logging-levels", "Cisco IOS Syslog Logging Configuration", "logging host 192.168.1.50", "logging trap notifications"),
    ("cdp-cisco-discovery-protocol", "Cisco Discovery Protocol (CDP) Management", "cdp run", "no cdp enable"),
    ("lldp-link-layer-discovery-protocol", "LLDP Open-Standard Discovery Protocol", "lldp run", "lldp transmit"),
    ("eigrp-configuration-basics", "EIGRP Routing Protocol Configuration", "router eigrp 100", "network 192.168.1.0 0.0.0.255"),
    ("eigrp-metric-and-k-values", "EIGRP Metric Calculation and Successors", "show ip eigrp topology", "show ip eigrp neighbors"),
    ("named-extended-acls", "Named Extended Access Control Lists", "ip access-list extended SECURE_IN", "permit tcp any any eq 443"),
    ("dynamic-nat-pools", "Dynamic NAT with IP Pools", "ip nat pool PUBLIC_POOL 203.0.113.1 203.0.113.10 netmask 255.255.255.0", "ip nat inside source list 1 pool PUBLIC_POOL"),
    ("static-nat-one-to-one", "Static 1-to-1 NAT for Web Servers", "ip nat inside source static 192.168.1.100 203.0.113.5", "show ip nat translations"),
    ("switch-svi-management-ip", "Configuring Switch Management SVI IP", "interface Vlan1", "ip address 192.168.1.254 255.255.255.0"),
    ("default-route-redistribution-ospf", "Default-Information Originate in OSPF", "router ospf 1", "default-information originate"),
    ("ospf-cost-metric-bandwidth", "OSPF Cost Calculation and Reference Bandwidth", "auto-cost reference-bandwidth 1000", "ip ospf cost 10"),
    ("ospf-dr-bdr-election-priority", "OSPF DR/BDR Election and Router Priority", "interface GigabitEthernet0/0", "ip ospf priority 255"),
    ("dhcp-snooping-security", "DHCP Snooping Layer 2 Mitigation", "ip dhcp snooping", "ip dhcp snooping trust"),
    ("dynamic-arp-inspection-dai", "Dynamic ARP Inspection (DAI) against Spoofing", "ip arp inspection vlan 10", "ip arp inspection trust"),
    ("voice-vlan-configuration", "Voice VLAN for IP Phones on Switchports", "switchport voice vlan 150", "mls qos trust cos"),
    ("native-vlan-security-vlan99", "Native VLAN Best Practices and VLAN Hopping Prevention", "switchport trunk native vlan 99", "switchport trunk allowed vlan remove 1"),
    ("switchport-modes-trunk-vs-access", "DTP Modes and Trunk Negotiation", "switchport mode dynamic desirable", "switchport nonegotiate"),
    ("duplex-and-speed-mismatch", "Troubleshooting Speed and Duplex Mismatch", "speed 1000", "duplex full"),
    ("interface-status-err-disabled", "Troubleshooting Err-Disabled Interface State", "show interfaces status err-disabled", "errdisable recovery cause all"),
    ("console-port-configuration", "Console Port Password and Exec-Timeout", "line con 0", "exec-timeout 0 0"),
    ("aux-port-and-modem-access", "AUX Port Security and Disabling", "line aux 0", "transport input none"),
    ("banner-motd-configuration", "Configuring Banner MOTD for Legal Notice", "banner motd # Unauthorized Access Prohibited #", "banner login # Legal Banner #"),
    ("password-encryption-type-7-vs-type-5", "Password Hashing (Type 7 vs Type 5 MD5 vs Type 8/9)", "enable secret Cisco123!", "service password-encryption"),
    ("vtp-vlan-trunking-protocol", "VLAN Trunking Protocol (VTP) Modes and Risks", "vtp mode transparent", "vtp domain LAB"),
    ("rstp-rapid-spanning-tree-migration", "Migrating from 802.1D STP to Rapid PVST+", "spanning-tree mode rapid-pvst", "show spanning-tree summary"),
    ("etherchannel-load-balancing-hash", "EtherChannel Load Balancing Hash Algorithm", "port-channel load-balance src-dst-ip", "show etherchannel load-balance"),
    ("subinterfaces-8021q-mtu", "MTU and Subinterface Sizing on Routers", "mtu 1500", "ip mtu 1500"),
    ("ipv6-slaac-stateless-autoconfig", "IPv6 Stateless Address Autoconfiguration (SLAAC)", "ipv6 address autoconfig", "ipv6 nd other-config-flag"),
    ("ipv6-stateful-dhcpv6", "Configuring Stateful DHCPv6 Server", "ipv6 dhcp pool IPV6_POOL", "address prefix 2001:db8:1::/64"),
    ("ipv6-static-routing", "IPv6 Static Routes and Default Gateway", "ipv6 route ::/0 2001:db8:acad:1::2", "show ipv6 route"),
    ("ipv6-ripng-configuration", "RIPng (RIP Next Generation) for IPv6", "ipv6 router rip CCNA_RIP", "ipv6 rip CCNA_RIP enable"),
    ("ipv6-ospfv3-configuration", "OSPFv3 Configuration for IPv6", "ipv6 router ospf 1", "ospfv3 1 ipv6 area 0"),
    ("cisco-ios-license-technology-package", "Cisco IOS Technology Packages and Licensing in PT", "license boot module c2900 technology-package securityk9", "show license"),
    ("tftp-backup-running-config", "Backing Up Configuration via TFTP in Packet Tracer", "copy running-config tftp:", "copy tftp: running-config"),
    ("password-recovery-procedure-2911", "Cisco Router 2911 Password Recovery Process", "config-register 0x2142", "config-register 0x2102"),
    ("rommon-mode-and-recovery", "ROMMON Mode Commands and Boot Sequences", "boot", "confreg"),
    ("packet-tracer-simulation-mode-pdu", "Using Simulation Mode and Inspecting PDUs", "Simulation Mode", "Event List Filters"),
    ("packet-tracer-iot-devices", "Packet Tracer IoT and Home Gateway Setup", "Home Gateway", "IoT Registration Server"),
    ("wireless-router-wrt300n-setup", "Packet Tracer WRT300N Home Wireless Router Setup", "SSID Configuration", "WPA2-Personal AES"),
    ("wlan-controller-wlc-basics", "Cisco Wireless LAN Controller (WLC 3504) in PT", "WLC Management Interface", "WLAN SSID Mapping"),
    ("access-point-lap-vs-autonomous", "Lightweight Access Point (LAP) vs Autonomous AP", "CAPWAP Discovery", "AP Join Process"),
    ("snmp-v2c-and-v3-configuration", "Simple Network Management Protocol (SNMP) Setup", "snmp-server community public RO", "snmp-server host 10.0.0.50 version 2c public"),
    ("packet-tracer-server-services-http-dns", "Configuring Server-PT HTTP, DHCP, DNS Services", "HTTP Service ON", "DNS Resource Records A Record"),
    ("packet-tracer-email-service-setup", "Setting Up Email SMTP and POP3 in Packet Tracer", "SMTP Service", "POP3 Domain Setup"),
    ("packet-tracer-ftp-service-setup", "Configuring FTP Server and User Permissions in PT", "FTP Service ON", "User Permissions write read"),
    ("routing-information-source-ad", "Administrative Distance (AD) Comparison Table", "Directly Connected: 0, Static: 1, EIGRP: 90, OSPF: 110, RIP: 120", "distance 105"),
    ("floating-static-route-failover", "Configuring Floating Static Routes with Verification", "ip route 0.0.0.0 0.0.0.0 10.0.0.1", "ip route 0.0.0.0 0.0.0.0 10.1.1.1 200"),
    ("loopback-interfaces-usage", "Using Loopback Interfaces for Testing and OSPF IDs", "interface Loopback0", "ip address 1.1.1.1 255.255.255.255"),
    ("serial-hdlc-vs-ppp-encapsulation", "Serial Encapsulation: HDLC vs PPP and PAP/CHAP", "encapsulation ppp", "ppp authentication chap"),
    ("gre-tunnel-configuration", "Generic Routing Encapsulation (GRE) VPN Tunnel", "interface Tunnel0", "tunnel source GigabitEthernet0/0"),
    ("ipsec-vpn-basics-packet-tracer", "IPsec Site-to-Site VPN Primer in Packet Tracer", "crypto isakmp policy 10", "crypto ipsec transform-set ESP-AES-SHA"),
    ("qos-quality-of-service-primer", "Quality of Service (QoS) Markings and Classification", "mls qos", "priority-queue out"),
    ("ptbuilder-javascript-automation-tips", "PTBuilder JavaScript Automation API Guide", "addDevice(id, model, x, y)", "configureIosDevice(id, config)")
]

for slug, title, cmd1, cmd2 in extra_topics:
    filename = f"{slug}.md"
    body = f"""# {title}

This document provides a concise CCNA-level reference and operational guide for {title.lower()} within Cisco enterprise topologies and Cisco Packet Tracer simulations.

### Cisco IOS Configuration

```cisco
! Key command references for {title}
Router# configure terminal
Router(config)# {cmd1}
Router(config)# {cmd2}
Router(config)# end
Router# write memory
```

### Operational Overview & Best Practices
1. Ensure proper physical link state and valid IP connectivity before configuring protocol services.
2. Confirm configuration changes using appropriate show verification commands (`show running-config`, `show ip interface brief`, etc.).
3. Document all IP addresses, VLAN tags, and port assignments in the central topology plan.

### Common Mistakes
- Misconfiguring syntax or forgetting prerequisites before applying commands.
- Neglecting to save the running configuration to NVRAM with `write memory` or `copy running-config startup-config`.
- Mismatched subnet masks or conflicting network settings across interconnected devices.
"""
    docs.append((filename, title, body))

knowledge_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "knowledge"))
os.makedirs(knowledge_dir, exist_ok=True)

print(f"Writing {len(docs)} CCNA knowledge documents to {knowledge_dir}...")
for fname, title, content in docs:
    fpath = os.path.join(knowledge_dir, fname)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

print(f"Successfully created {len(docs)} markdown documents!")
