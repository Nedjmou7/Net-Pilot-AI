# OSPF Default Route Propagation

Propagates a default gateway route (0.0.0.0/0) to all OSPF neighbors.

```cisco
Router(config-router)# default-information originate
```

### Common Mistakes
- Forgetting that a default route must already exist in the routing table unless `always` is appended.
