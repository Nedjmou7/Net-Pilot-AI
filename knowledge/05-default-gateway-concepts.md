# Default Gateway Concepts and Configuration

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
