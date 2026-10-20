# Inter-VLAN Routing with Switch Virtual Interfaces (SVI)

Multilayer switches (such as Cisco Catalyst 3650 or 3560) perform wire-speed hardware routing between VLANs using Switch Virtual Interfaces (SVIs).

```cisco
L3Switch(config)# ip routing

L3Switch(config)# vlan 10
L3Switch(config)# vlan 20

L3Switch(config)# interface Vlan10
L3Switch(config-if)# ip address 192.168.10.1 255.255.255.0
L3Switch(config-if)# no shutdown

L3Switch(config)# interface Vlan20
L3Switch(config-if)# ip address 192.168.20.1 255.255.255.0
L3Switch(config-if)# no shutdown
```

### Common Mistakes
- Forgetting `ip routing` global command; without it, the multilayer switch functions as a standard Layer 2 switch.
- Not creating the VLAN in the VLAN database prior to creating the SVI interface.
