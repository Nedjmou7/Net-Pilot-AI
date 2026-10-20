# VLAN Fundamentals and Benefits

A Virtual Local Area Network (VLAN) is a logical grouping of switch ports that creates isolated broadcast domains at Layer 2. By default, all switch ports belong to VLAN 1 (the default administrative VLAN).

Benefits of VLANs:
- **Security**: Isolates sensitive departments (e.g. Finance, HR).
- **Cost Reduction**: Reuses existing physical switch infrastructure.
- **Broadcast Control**: Reduces broadcast traffic storm impact.
- **Improved Performance**: Smaller broadcast domains increase CPU efficiency.

```cisco
Switch# configure terminal
Switch(config)# vlan 10
Switch(config-vlan)# name MANAGEMENT
Switch(config-vlan)# vlan 20
Switch(config-vlan)# name SALES
Switch(config-vlan)# exit
```

### Common Mistakes
- Creating access ports assigned to a VLAN without first creating the VLAN in global configuration mode.
- Changing or deleting VLAN 1, which cannot be renamed or deleted.
