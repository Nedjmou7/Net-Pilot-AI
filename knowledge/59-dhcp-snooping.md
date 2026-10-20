# DHCP Snooping Security

DHCP Snooping prevents rogue DHCP servers by categorizing ports as trusted or untrusted.

```cisco
Switch(config)# ip dhcp snooping
Switch(config)# ip dhcp snooping vlan 10
Switch(config-if)# ip dhcp snooping trust
```

### Common Mistakes
- Forgetting to trust the uplink port connecting to the legitimate DHCP server.
