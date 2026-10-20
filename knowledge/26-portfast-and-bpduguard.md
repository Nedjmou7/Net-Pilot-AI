# STP PortFast and BPDU Guard

By default, an STP port takes 30 to 50 seconds to reach forwarding state (Listening 15s -> Learning 15s -> Forwarding). For end-user devices (PCs, servers), this delay causes DHCP discovery timeouts.

- **PortFast**: Immediately transitions an access port from blocking to forwarding, bypassing listening and learning states.
- **BPDU Guard**: Shuts down a PortFast-enabled port (places into `err-disable`) if a BPDU packet is received, protecting against rogue switches connected to access ports.

Configuration:
```cisco
Switch(config)# interface FastEthernet0/1
Switch(config-if)# switchport mode access
Switch(config-if)# spanning-tree portfast
Switch(config-if)# spanning-tree bpduguard enable
```

Globally:
```cisco
Switch(config)# spanning-tree portfast default
Switch(config)# spanning-tree portfast bpduguard default
```

### Common Mistakes
- Enabling PortFast on switch-to-switch trunk links, causing catastrophic bridging loops.
- Not knowing how to recover an `err-disabled` port (`shutdown` followed by `no shutdown`).
