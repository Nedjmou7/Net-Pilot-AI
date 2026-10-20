# Routed Layer 3 EtherChannel

Bundles router or multilayer switch interfaces into a routed link with an IP address.

```cisco
Switch(config-if-range)# no switchport
Switch(config-if-range)# channel-group 1 mode active
Switch(config)# interface port-channel 1
Switch(config-if)# no switchport
Switch(config-if)# ip address 10.0.0.1 255.255.255.252
```

### Common Mistakes
- Forgetting `no switchport` on both member interfaces and the port-channel interface.
