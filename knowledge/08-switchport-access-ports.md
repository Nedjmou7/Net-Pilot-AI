# Switch Access Port Configuration

Access ports connect end devices (PCs, printers, servers) to a single VLAN. Traffic leaving an access port toward a PC is untagged (standard 802.3 Ethernet frame without 802.1Q header).

```cisco
Switch(config)# interface FastEthernet0/1
Switch(config-if)# switchport mode access
Switch(config-if)# switchport access vlan 10
Switch(config-if)# spanning-tree portfast
Switch(config-if)# no shutdown
```

To configure multiple ports simultaneously:
```cisco
Switch(config)# interface range FastEthernet0/1 - 10
Switch(config-if-range)# switchport mode access
Switch(config-if-range)# switchport access vlan 10
```

### Common Mistakes
- Leaving ports in dynamic desirable or dynamic auto modes, which can allow rogue VLAN trunking attacks.
- Forgetting `spanning-tree portfast` on end-host ports, causing DHCP timeouts due to STP 30-second listening/learning delays.
