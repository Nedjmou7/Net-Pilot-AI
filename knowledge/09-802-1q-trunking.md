# IEEE 802.1Q Trunking Protocol

A trunk link carries traffic for multiple VLANs over a single physical cable between switches, or between a switch and a router. IEEE 802.1Q inserts a 4-byte tag into the standard Ethernet frame:
- Tag Protocol Identifier (TPID): `0x8100` (16 bits)
- Priority Code Point (PCP): 3 bits (QoS CoS)
- Drop Eligible Indicator (DEI): 1 bit
- VLAN Identifier (VID): 12 bits (supports VLANs 1 to 4094)

```cisco
Switch(config)# interface GigabitEthernet0/1
Switch(config-if)# switchport mode trunk
Switch(config-if)# switchport trunk allowed vlan 10,20,30
Switch(config-if)# no shutdown
```

On Layer 3 switches (e.g. Cisco 3560):
```cisco
Switch(config-if)# switchport trunk encapsulation dot1q
Switch(config-if)# switchport mode trunk
```

### Common Mistakes
- Missing `switchport trunk encapsulation dot1q` on Catalyst 3560 switches before running `switchport mode trunk`.
- Restricting allowed VLANs on one side of a trunk while forgetting the other side.
