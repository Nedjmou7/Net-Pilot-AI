# IPv6 Addressing and Structure

IPv6 uses 128-bit addresses represented in hexadecimal. Global unicast addresses start with 2000::/3. Unique local start with FC00::/7. Link-local start with FE80::/10.

```cisco
Router(config)# ipv6 unicast-routing
Router(config-if)# ipv6 address 2001:db8:acad:1::1/64
```

### Common Mistakes
- Forgetting `ipv6 unicast-routing` globally before configuring IPv6 routing protocols.
