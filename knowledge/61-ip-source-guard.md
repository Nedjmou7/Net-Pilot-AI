# IP Source Guard

Filters incoming traffic based on DHCP snooping database to prevent IP address spoofing.

```cisco
Switch(config-if)# ip verify source
```

### Common Mistakes
- Enabling IP Source Guard on trunk ports.
