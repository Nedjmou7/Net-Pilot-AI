# OSPF DR and BDR Election

Designated Router (DR) and Backup DR (BDR) minimize OSPF adjacencies on multiaccess broadcast networks.

```cisco
Router(config-if)# ip ospf priority 255
```

### Common Mistakes
- Forgetting that priority 0 prevents a router from ever becoming DR or BDR.
