# EtherChannel (Link Aggregation) Configuration

EtherChannel bundles up to 8 physical Ethernet links into a single logical channel (Port-Channel), providing link redundancy and aggregated bandwidth.

Protocols:
1. **LACP (IEEE 802.3ad - Open Standard)**:
   - Modes: `active` (initiates negotiation), `passive` (waits for partner).
2. **PAgP (Cisco Proprietary)**:
   - Modes: `desirable` (initiates), `auto` (waits).
3. **Static (Manual)**:
   - Mode: `on` (no negotiation).

LACP Configuration:
```cisco
Switch(config)# interface range GigabitEthernet0/1 - 2
Switch(config-if-range)# channel-group 1 mode active
Switch(config-if-range)# exit

Switch(config)# interface port-channel 1
Switch(config-if)# switchport mode trunk
Switch(config-if)# switchport trunk allowed vlan 10,20
```

### Common Mistakes
- Mismatched duplex, speed, or VLAN settings across physical member interfaces.
- Combining `passive` with `passive` or `auto` with `auto`, preventing channel negotiation.
