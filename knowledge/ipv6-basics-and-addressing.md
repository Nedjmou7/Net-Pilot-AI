# IPv6 Addressing and Link-Local Configuration

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
