# Dynamic ARP Inspection (DAI)

DAI validates ARP packets using DHCP snooping binding database to prevent ARP poisoning/spoofing.

```cisco
Switch(config)# ip arp inspection vlan 10
```

### Common Mistakes
- Enabling DAI without DHCP snooping or static ARP inspection lists.
