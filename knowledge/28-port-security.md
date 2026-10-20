# Switch Port Security

Port Security restricts input to an interface by limiting the MAC addresses permitted to send traffic through that switch port.

Violation Modes:
- **Shutdown**: Port enters `err-disable` state immediately; sends SNMP trap and syslog message. (Default)
- **Restrict**: Drops frames from unauthorized MACs; increments violation counter and logs syslog message.
- **Protect**: Drops frames from unauthorized MACs silently without logging.

Configuration:
```cisco
Switch(config)# interface FastEthernet0/1
Switch(config-if)# switchport mode access
Switch(config-if)# switchport port-security
Switch(config-if)# switchport port-security maximum 2
Switch(config-if)# switchport port-security mac-address sticky
Switch(config-if)# switchport port-security violation shutdown
```

### Common Mistakes
- Trying to enable port security on dynamic switchports; port MUST be in static access mode (`switchport mode access`).
- Forgetting `switchport port-security` before setting maximum or sticky commands.
