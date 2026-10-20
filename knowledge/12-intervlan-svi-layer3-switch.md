# Inter-VLAN Routing with SVI on Layer 3 Switch

A Switch Virtual Interface (SVI) is a routed virtual interface representing a VLAN on a multilayer switch (such as Cisco Catalyst 3560). SVIs provide hardware-accelerated wire-speed inter-VLAN routing without traffic traversing an external router.

Configuration Steps:
1. Enable IP routing globally: `ip routing`
2. Create the VLANs: `vlan 10`, `vlan 20`
3. Configure SVIs with default gateway IP addresses:

```cisco
Switch(config)# ip routing
Switch(config)# vlan 10
Switch(config)# vlan 20

Switch(config)# interface Vlan 10
Switch(config-if)# ip address 192.168.10.1 255.255.255.0
Switch(config-if)# no shutdown

Switch(config)# interface Vlan 20
Switch(config-if)# ip address 192.168.20.1 255.255.255.0
Switch(config-if)# no shutdown
```

### Common Mistakes
- Omitting `ip routing` on the multilayer switch; without it, the switch behaves as a pure Layer 2 bridge.
- An SVI stays down/down unless at least one active switch port in that VLAN is up.
