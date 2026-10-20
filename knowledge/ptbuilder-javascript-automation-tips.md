# PTBuilder JavaScript Automation API Guide

> This is an external PTBuilder/bridge API used by NetBuilder. Cisco Packet Tracer
> does not natively implement `addDevice`, `addLink`, or `configureIosDevice`, and
> the generated JavaScript cannot be imported as a `.pkt` project. In standard
> Packet Tracer, create the devices and links manually, then paste the generated
> IOS configurations from the IOS Configs tab into each device CLI.

This document provides a concise CCNA-level reference and operational guide for ptbuilder javascript automation api guide within Cisco enterprise topologies and Cisco Packet Tracer simulations.

### Cisco IOS Configuration

```cisco
! Key command references for PTBuilder JavaScript Automation API Guide
Router# configure terminal
Router(config)# addDevice(id, model, x, y)
Router(config)# configureIosDevice(id, config)
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
