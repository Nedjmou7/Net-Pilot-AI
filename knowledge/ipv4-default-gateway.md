# Default Gateway Role and Configuration

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
