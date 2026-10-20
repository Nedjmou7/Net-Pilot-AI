# Routing Information Protocol (RIPv2)

RIPv2 is a distance-vector routing protocol that uses hop count as its metric (maximum 15 hops; 16 hops is considered unreachable). RIPv2 sends multicast updates to `224.0.0.9` every 30 seconds and supports VLSM and classless routing.

Configuration:
```cisco
Router(config)# router rip
Router(config-router)# version 2
Router(config-router)# no auto-summary
Router(config-router)# network 192.168.1.0
Router(config-router)# network 10.0.0.0
Router(config-router)# passive-interface GigabitEthernet0/0
```

Verification:
```cisco
Router# show ip route rip
Router# show ip protocols
```

### Common Mistakes
- Forgetting `no auto-summary`, which causes RIP to summarize networks to their classful boundaries.
- Forgetting `version 2`, leaving the router in RIPv1 broadcast mode.
