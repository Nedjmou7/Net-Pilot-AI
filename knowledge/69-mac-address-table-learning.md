# Switch MAC Address Learning Process

Switches populate MAC table by inspecting source MAC of incoming frames and forward using destination MAC.

```cisco
Switch# show mac address-table
Switch# clear mac address-table dynamic
```

### Common Mistakes
- Confusing ARP table (IP to MAC) with MAC table (MAC to switch port).
