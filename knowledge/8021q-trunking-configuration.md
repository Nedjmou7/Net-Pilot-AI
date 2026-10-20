# 802.1Q Trunking Configuration

Trunk links carry traffic for multiple VLANs across switches or between a switch and a router. IEEE 802.1Q inserts a 4-byte tag into the standard Ethernet frame containing the 12-bit VLAN ID.

```cisco
Switch(config)# interface GigabitEthernet0/1
! On Layer 3 switches (e.g. 3650), specify encapsulation first:
Switch(config-if)# switchport trunk encapsulation dot1q
Switch(config-if)# switchport mode trunk
Switch(config-if)# switchport trunk allowed vlan 10,20,99
Switch(config-if)# switchport trunk native vlan 99
Switch(config-if)# no shutdown
```

Verification:
```cisco
Switch# show interfaces trunk
```

### Common Mistakes
- Mismatched native VLANs on opposite ends of a trunk link, triggering CDP native VLAN mismatch errors.
- Forgetting to permit newly created VLANs in the `switchport trunk allowed vlan` list.
