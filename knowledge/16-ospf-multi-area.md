# OSPF Multi-Area Architecture

Multi-area OSPF reduces SPF calculations, restricts routing update propagation, and shrinks routing table sizes through summarization.

Key Concepts:
- **Area 0 (Backbone)**: Core transit area; all other areas must connect directly to Area 0.
- **Area Border Router (ABR)**: Router with interfaces in Area 0 and one or more non-backbone areas.
- **Autonomous System Boundary Router (ASBR)**: Router that redistributes routes from external sources (e.g. BGP, RIP, static) into OSPF.

Configuration on ABR:
```cisco
Router(config)# router ospf 1
Router(config-router)# router-id 2.2.2.2
Router(config-router)# network 10.0.1.0 0.0.0.3 area 0
Router(config-router)# network 192.168.10.0 0.0.0.255 area 1
```

### Common Mistakes
- Creating disconnected non-backbone areas that do not connect to Area 0.
- Forgetting to summarize routes on ABR using `area <id> range <network> <mask>`.
