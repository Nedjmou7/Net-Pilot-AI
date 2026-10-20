# Static Routing and Default Routes

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
