# Extended Numbered ACLs (100-199)

Extended ACLs inspect source IP, destination IP, Layer 4 protocol (TCP, UDP, ICMP), and port numbers (e.g. 80, 443, 22). Range: 100 to 199 and 2000 to 2699.

Placement guideline: Place extended ACLs as close to the **source** as possible to drop unauthorized traffic before it consumes network bandwidth.

```cisco
! Deny PC1 (192.168.10.5) web access to WebServer (10.0.0.50), permit other traffic
Router(config)# access-list 101 deny tcp host 192.168.10.5 host 10.0.0.50 eq 80
Router(config)# access-list 101 deny tcp host 192.168.10.5 host 10.0.0.50 eq 443
Router(config)# access-list 101 permit ip any any

Router(config)# interface GigabitEthernet0/0
Router(config-if)# ip access-group 101 in
```

### Common Mistakes
- Misordering rules: ACLs are processed sequentially top-to-bottom on first match. Specific rules must precede general permit rules.
- Omitting `permit ip any any` when aiming to selectively block specific ports.
