# IPv4 Addressing and Classes

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
