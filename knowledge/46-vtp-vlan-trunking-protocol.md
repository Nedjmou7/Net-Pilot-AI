# VLAN Trunking Protocol (VTP)

VTP synchronizes VLAN databases across switches in a VTP domain. Modes: Server, Client, Transparent, Off.

```cisco
Switch(config)# vtp domain ciscodomain
Switch(config)# vtp mode transparent
```

### Common Mistakes
- Connecting a switch with a higher revision number to an existing network, wiping all VLANs.
