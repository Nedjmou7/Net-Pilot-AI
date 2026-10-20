# Private vs Public IPv4 Addresses

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
