# OSPF Router ID Determination

OSPF Router ID order of precedence: 1. Manual `router-id`, 2. Highest IP on active loopback, 3. Highest IP on active physical interface.

```cisco
Router(config-router)# router-id 1.1.1.1
```

### Common Mistakes
- Changing router-id without running `clear ip ospf process` to apply it.
