# Password Hashing (Type 7 vs Type 5 MD5 vs Type 8/9)

This document provides a concise CCNA-level reference and operational guide for password hashing (type 7 vs type 5 md5 vs type 8/9) within Cisco enterprise topologies and Cisco Packet Tracer simulations.

### Cisco IOS Configuration

```cisco
! Key command references for Password Hashing (Type 7 vs Type 5 MD5 vs Type 8/9)
Router# configure terminal
Router(config)# enable secret Cisco123!
Router(config)# service password-encryption
Router(config)# end
Router# write memory
```

### Operational Overview & Best Practices
1. Ensure proper physical link state and valid IP connectivity before configuring protocol services.
2. Confirm configuration changes using appropriate show verification commands (`show running-config`, `show ip interface brief`, etc.).
3. Document all IP addresses, VLAN tags, and port assignments in the central topology plan.

### Common Mistakes
- Misconfiguring syntax or forgetting prerequisites before applying commands.
- Neglecting to save the running configuration to NVRAM with `write memory` or `copy running-config startup-config`.
- Mismatched subnet masks or conflicting network settings across interconnected devices.
