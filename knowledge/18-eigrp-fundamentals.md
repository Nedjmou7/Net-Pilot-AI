# EIGRP Protocol and Configuration

Enhanced Interior Gateway Routing Protocol (EIGRP) is an advanced distance-vector routing protocol developed by Cisco. It uses the Diffusing Update Algorithm (DUAL) for fast loop-free convergence.

Key Attributes:
- Administrative Distance: 90 (Internal), 170 (External).
- Composite Metric: Bandwidth and Delay (`K1=1, K3=1`).
- Multicast Address: `224.0.0.10`.
- Successor: The best primary path placed in routing table.
- Feasible Successor (FS): A backup path that meets the Feasibility Condition (`Reported Distance < Feasible Distance`).

Configuration:
```cisco
Router(config)# router eigrp 100
Router(config-router)# no auto-summary
Router(config-router)# network 192.168.1.0 0.0.0.255
Router(config-router)# network 10.0.0.0 0.0.0.3
Router(config-router)# passive-interface GigabitEthernet0/0
```

### Common Mistakes
- Autonomous system (AS) number mismatch between routers (`router eigrp 100` vs `200`).
- Forgetting `no auto-summary` on older Cisco IOS versions.
