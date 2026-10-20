# Native VLAN Concepts and Security

In 802.1Q trunking, the Native VLAN carries untagged frames across the trunk link. By default, the native VLAN is VLAN 1. When an 802.1Q trunk receives an untagged frame, it forwards it to the native VLAN.

Security Best Practices:
1. Never use default VLAN 1 as the native VLAN.
2. Change the native VLAN to an unused, dedicated non-routed VLAN ID (e.g. VLAN 999).
3. The native VLAN must match on both ends of the trunk link; mismatch causes CDP native VLAN mismatch errors and cross-VLAN traffic leakage.

```cisco
Switch(config)# vlan 999
Switch(config-vlan)# name NATIVE_UNUSED
Switch(config)# interface GigabitEthernet0/1
Switch(config-if)# switchport trunk native vlan 999
```

### Common Mistakes
- Configuring different native VLANs on the two ends of a trunk link, triggering `%CDP-4-NATIVE_VLAN_MISMATCH`.
- Assigning host access ports to the native VLAN.
