# IPv6 Link-Local Addresses

IPv6 link-local addresses (FE80::/10) are used for communication on a single local link. Automatically created using EUI-64 or randomly, or statically configured.

```cisco
Router(config-if)# ipv6 address fe80::1 link-local
```

### Common Mistakes
- Trying to route link-local traffic beyond the local router hop.
