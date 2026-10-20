# Extended Access Control Lists (ACL)

Extended ACLs filter traffic based on source IP, destination IP, protocol (IP, TCP, UDP, ICMP), and port numbers (HTTP 80, HTTPS 443, DNS 53, SSH 22).
- Numbered range: `100` to `199` and `2000` to `2699`.
- Placement Rule: Place extended ACLs **as close to the source as possible** to prevent unwanted traffic from traversing network bandwidth.

Configuration Example:
Allow subnet `192.168.10.0/24` to access web servers (`80, 443`), but block ping (ICMP) and all other traffic:
```cisco
Router(config)# access-list 101 permit tcp 192.168.10.0 0.0.0.255 any eq 80
Router(config)# access-list 101 permit tcp 192.168.10.0 0.0.0.255 any eq 443
Router(config)# access-list 101 deny icmp 192.168.10.0 0.0.0.255 any
Router(config)# access-list 101 permit ip any any

Router(config)# interface GigabitEthernet0/0
Router(config-if)# ip access-group 101 in
```

### Common Mistakes
- Applying the ACL in the wrong direction (`in` instead of `out`, or vice versa).
- Specifying source and destination ports in the wrong order.
