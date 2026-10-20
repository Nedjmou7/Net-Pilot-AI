# Configuring Switch Access Ports

An access port belongs to exactly one VLAN and carries untagged Ethernet frames to end stations (PCs, printers, servers).

```cisco
Switch(config)# interface FastEthernet0/1
Switch(config-if)# switchport mode access
Switch(config-if)# switchport access vlan 10
Switch(config-if)# no shutdown
Switch(config-if)# exit

! Configuring multiple ports with interface range
Switch(config)# interface range FastEthernet0/2 - 10
Switch(config-if-range)# switchport mode access
Switch(config-if-range)# switchport access vlan 20
Switch(config-if-range)# no shutdown
```

### Common Mistakes
- Leaving access ports in dynamic auto or dynamic desirable mode, exposing the switch to DTP VLAN hopping attacks.
- Forgetting `interface range` syntax (spaces around the hyphen are required: `FastEthernet0/2 - 10`).
