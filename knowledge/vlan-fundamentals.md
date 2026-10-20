# VLAN Fundamentals and Creation

Virtual Local Area Networks (VLANs) segment a physical switch into multiple logical broadcast domains. Benefits include enhanced security, containment of broadcast traffic, and improved traffic management.

By default, all Cisco switch ports belong to VLAN 1. Custom VLAN IDs range from 1 to 4094 (Normal range: 1–1005, Extended: 1006–4094).

```cisco
Switch# configure terminal
Switch(config)# vlan 10
Switch(config-vlan)# name SALES
Switch(config-vlan)# exit
Switch(config)# vlan 20
Switch(config-vlan)# name ENGINEERING
Switch(config-vlan)# exit
```

Verification command:
```cisco
Switch# show vlan brief
```

### Common Mistakes
- Forgetting to exit VLAN configuration mode before testing (VLAN changes commit upon exiting config-vlan).
- Assigning switch ports to a VLAN that has not been created in the database.
