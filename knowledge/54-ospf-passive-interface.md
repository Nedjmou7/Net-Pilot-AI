# OSPF Passive Interface

Suppresses OSPF hello packets on an interface while still advertising its connected subnet into OSPF.

```cisco
Router(config-router)# passive-interface GigabitEthernet0/0
```

### Common Mistakes
- Setting a passive-interface on a link between two OSPF routers, breaking adjacency.
