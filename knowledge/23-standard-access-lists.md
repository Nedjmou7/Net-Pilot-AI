# Standard Access Control Lists (ACL)

Standard ACLs filter traffic based solely on the source IPv4 address.
- Numbered range: `1` to `99` and `1300` to `1999`.
- Placement Rule: Place standard ACLs **as close to the destination as possible** to avoid inadvertently blocking legitimate traffic to other destinations.
- Implicit Deny: Every ACL ends with an invisible `deny any` statement.

Configuration:
```cisco
Router(config)# access-list 10 permit 192.168.10.0 0.0.0.255
Router(config)# access-list 10 deny any
Router(config)# interface GigabitEthernet0/1
Router(config-if)# ip access-group 10 out
```

Named Standard ACL:
```cisco
Router(config)# ip access-list standard BLOCK_GUESTS
Router(config-std-nacl)# permit 192.168.1.50
Router(config-std-nacl)# deny 192.168.1.0 0.0.0.255
Router(config-std-nacl)# permit any
```

### Common Mistakes
- Placing a standard ACL close to the source, inadvertently blocking the source from reaching ALL networks.
- Forgetting the implicit `deny any` at the end of the ACL, blocking more traffic than intended.
