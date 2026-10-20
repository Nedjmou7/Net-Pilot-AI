# APIPA and Loopback Addresses

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
