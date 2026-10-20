# Address Resolution Protocol (ARP) Diagnostics

ARP maps IPv4 addresses to Layer 2 MAC addresses.

```cisco
Router# show ip arp
Router# clear ip arp-cache
```

### Common Mistakes
- Assuming switches maintain ARP tables for all traffic (switches maintain MAC address tables; only routers and SVIs maintain ARP tables).
