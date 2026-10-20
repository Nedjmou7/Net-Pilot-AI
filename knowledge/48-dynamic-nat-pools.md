# Dynamic NAT with Public Address Pools

Translates inside hosts into an available pool of public IPs.

```cisco
Router(config)# ip nat pool PUBLIC_POOL 203.0.113.1 203.0.113.10 netmask 255.255.255.0
Router(config)# ip nat inside source list 1 pool PUBLIC_POOL
```

### Common Mistakes
- Pool exhaustion when concurrent connections exceed pool size.
