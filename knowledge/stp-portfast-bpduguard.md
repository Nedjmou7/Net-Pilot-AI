# STP PortFast and BPDU Guard

PortFast transitions an access switchport immediately from blocking to forwarding state, bypassing listening and learning states (saving 30 seconds).

BPDU Guard automatically err-disables a PortFast-enabled port if a BPDU is received, preventing rogue switch loops.

```cisco
! Per-interface configuration
Switch(config)# interface FastEthernet0/1
Switch(config-if)# switchport mode access
Switch(config-if)# spanning-tree portfast
Switch(config-if)# spanning-tree bpduguard enable
Switch(config-if)# exit

! Global configuration for all access ports
Switch(config)# spanning-tree portfast default
Switch(config)# spanning-tree portfast bpduguard default
```

Recovery from err-disabled:
```cisco
Switch(config)# interface FastEthernet0/1
Switch(config-if)# shutdown
Switch(config-if)# no shutdown
```

### Common Mistakes
- Enabling PortFast on trunk ports connected to other switches, which can induce immediate catastrophic broadcast storms.
