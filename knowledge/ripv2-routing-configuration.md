# RIPv2 Distance Vector Routing Configuration

Routing Information Protocol Version 2 (RIPv2) is a distance-vector protocol using hop count as its metric (maximum 15 hops; 16 hops is unreachable). Unlike RIPv1, RIPv2 supports CIDR and VLSM.

```cisco
Router(config)# router rip
Router(config-router)# version 2
Router(config-router)# no auto-summary
Router(config-router)# network 192.168.10.0
Router(config-router)# network 10.0.0.0
Router(config-router)# passive-interface GigabitEthernet0/0
```

Verification:
```cisco
Router# show ip protocols
Router# show ip route rip
```

### Common Mistakes
- Forgetting `no auto-summary`, causing RIPv2 to summarize discontiguous subnets to classful boundaries.
- Forgetting `version 2`, defaulting to RIPv1 which broadcasts without subnet masks.
