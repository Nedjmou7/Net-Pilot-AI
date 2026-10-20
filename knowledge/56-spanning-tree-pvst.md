# Per-VLAN Spanning Tree (PVST+)

Cisco PVST+ maintains a separate STP instance per VLAN, allowing load balancing across trunks.

```cisco
Switch(config)# spanning-tree mode pvst
```

### Common Mistakes
- High switch CPU load with hundreds of active VLANs under PVST+.
