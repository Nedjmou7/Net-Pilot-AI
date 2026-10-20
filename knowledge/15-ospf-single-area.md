# OSPF Single Area Configuration

Open Shortest Path First (OSPF) is an open-standard link-state routing protocol (RFC 2328). It uses Dijkstra's Shortest Path First (SPF) algorithm, has an administrative distance of 110, and uses cost (inverse of bandwidth) as metric.

In single-area OSPF, all routers reside in Area 0 (Backbone Area).

Configuration:
```cisco
Router(config)# router ospf 1
Router(config-router)# router-id 1.1.1.1
Router(config-router)# network 192.168.1.0 0.0.0.255 area 0
Router(config-router)# network 10.0.12.0 0.0.0.3 area 0
Router(config-router)# passive-interface GigabitEthernet0/0
```

Verification Commands:
```cisco
Router# show ip ospf neighbor
Router# show ip ospf interface brief
Router# show ip route ospf
```

### Common Mistakes
- Using a subnet mask instead of a wildcard mask in the `network` command.
- Area ID mismatch between connected neighbors, preventing FULL adjacency state.
