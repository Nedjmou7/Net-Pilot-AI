# Switchport Voice VLAN Configuration

Transmits IP phone traffic on a tagged Voice VLAN while passing PC traffic on an untagged Data VLAN.

```cisco
Switch(config-if)# switchport mode access
Switch(config-if)# switchport access vlan 10
Switch(config-if)# switchport voice vlan 150
```

### Common Mistakes
- Configuring the phone port as a trunk port instead of using `switchport voice vlan`.
