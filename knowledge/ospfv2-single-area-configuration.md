# OSPFv2 Single-Area Configuration

Open Shortest Path First (OSPF) is an open-standard link-state routing protocol using Dijkstra's SPF algorithm. Single-area OSPF operates entirely inside Area 0 (backbone).

```cisco
Router(config)# router ospf 1
Router(config-router)# router-id 1.1.1.1
Router(config-router)# network 192.168.10.0 0.0.0.255 area 0
Router(config-router)# network 10.0.0.0 0.0.0.3 area 0
Router(config-router)# passive-interface GigabitEthernet0/0
Router(config-router)# exit
```

Verification commands:
```cisco
Router# show ip ospf neighbor
Router# show ip ospf interface brief
Router# show ip route ospf
```

### Common Mistakes
- Using subnet masks instead of wildcard masks in the `network` command (OSPF requires wildcard mask: e.g. 0.0.0.255).
- Mismatched OSPF Hello (10s) or Dead (40s) timers between neighboring routers.
- Mismatched Area IDs on connecting link interfaces.
