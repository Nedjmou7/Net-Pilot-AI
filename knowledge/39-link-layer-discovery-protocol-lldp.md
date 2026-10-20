# Link Layer Discovery Protocol (LLDP)

LLDP (IEEE 802.1AB) is an open-standard vendor-neutral neighbor discovery protocol.

```cisco
Switch(config)# lldp run
Switch# show lldp neighbors
```

### Common Mistakes
- Forgetting that LLDP must be enabled globally with `lldp run` before `show lldp neighbors` works.
