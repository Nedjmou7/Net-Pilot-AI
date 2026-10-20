# EtherChannel Configuration (LACP & PAgP)

EtherChannel bundles up to 8 physical Ethernet links into a single logical channel, providing link aggregation, load balancing, and redundancy.

Protocols:
- LACP (IEEE 802.3ad open standard): `active` (initiates) and `passive` (waits)
- PAgP (Cisco proprietary): `desirable` and `auto`
- Static (no negotiation protocol): `on`

```cisco
Switch(config)# interface range GigabitEthernet0/1 - 2
Switch(config-if-range)# channel-group 1 mode active
Switch(config-if-range)# exit

Switch(config)# interface Port-channel 1
Switch(config-if)# switchport mode trunk
Switch(config-if)# switchport trunk allowed vlan all
```

Verification:
```cisco
Switch# show etherchannel summary
Switch# show interfaces port-channel 1
```

### Common Mistakes
- Mismatched speed, duplex, access VLAN, or trunk allowed VLAN settings on bundled interfaces (all physical member ports must match identical parameters).
