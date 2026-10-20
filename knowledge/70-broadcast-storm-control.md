# Broadcast Storm Control

Prevents network degradation from excessive broadcast, multicast, or unicast traffic.

```cisco
Switch(config-if)# storm-control broadcast level 20.0
```

### Common Mistakes
- Setting threshold too low, blocking legitimate ARP and DHCP broadcasts.
