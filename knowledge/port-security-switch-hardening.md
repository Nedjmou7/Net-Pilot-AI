# Switch Port Security Configuration

Port Security restricts input to an interface by limiting and identifying MAC addresses of stations allowed to access the port.

```cisco
Switch(config)# interface FastEthernet0/1
Switch(config-if)# switchport mode access
Switch(config-if)# switchport port-security
Switch(config-if)# switchport port-security maximum 2
Switch(config-if)# switchport port-security mac-address sticky
Switch(config-if)# switchport port-security violation shutdown
Switch(config-if)# no shutdown
```

Violation Modes:
- `shutdown`: Port immediately err-disables and logs SNMP trap.
- `restrict`: Drops violating frames, increments counter, logs alert.
- `protect`: Drops violating frames silently without logging.

Verification:
```cisco
Switch# show port-security interface FastEthernet0/1
Switch# show port-security address
```

### Common Mistakes
- Trying to enable port security on dynamic switchports (must explicitly run `switchport mode access` first).
