# Calculating Wildcard Masks for OSPF and ACLs

A wildcard mask tells the Cisco IOS parser which bits of an IPv4 address to inspect (0 = match exactly) and which bits to ignore (1 = wildcard / any value).

Calculation rule:
`Wildcard Mask = 255.255.255.255 - Subnet Mask`

Common conversions:
- /24: 255.255.255.0 -> Wildcard: `0.0.0.255`
- /25: 255.255.255.128 -> Wildcard: `0.0.0.127`
- /26: 255.255.255.192 -> Wildcard: `0.0.0.63`
- /27: 255.255.255.224 -> Wildcard: `0.0.0.31`
- /28: 255.255.255.240 -> Wildcard: `0.0.0.15`
- /29: 255.255.255.248 -> Wildcard: `0.0.0.7`
- /30: 255.255.255.252 -> Wildcard: `0.0.0.3`
- /32: 255.255.255.255 -> Wildcard: `0.0.0.0` (Host match)

```cisco
Router(config-router)# network 192.168.1.0 0.0.0.255 area 0
```

### Common Mistakes
- Typing `255.255.255.0` in an OSPF `network` statement.
- Inverting octet arithmetic (e.g. thinking /28 wildcard is 0.0.0.240).
