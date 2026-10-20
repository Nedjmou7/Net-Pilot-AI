# Essential Cisco IOS Show Commands Cheat Sheet

The most critical Cisco IOS diagnostic commands:

1. **Interface Status**:
```cisco
Router# show ip interface brief
Switch# show interfaces status
```

2. **Routing Table**:
```cisco
Router# show ip route
Router# show ip route ospf
Router# show ip route connected
```

3. **VLAN & Trunking**:
```cisco
Switch# show vlan brief
Switch# show interfaces trunk
```

4. **Layer 2 Discovery**:
```cisco
Router# show cdp neighbors
Router# show cdp neighbors detail
```

5. **Running Configuration**:
```cisco
Router# show running-config
Router# show running-config interface GigabitEthernet0/0
```

6. **MAC Address Table**:
```cisco
Switch# show mac address-table
```

### Common Mistakes
- Not filtering show commands with `include` or `section` (e.g. `show running-config | section ospf`).
