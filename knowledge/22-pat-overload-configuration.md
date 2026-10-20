# Port Address Translation (PAT) Overload Configuration

PAT (NAT Overload) allows hundreds of internal hosts to access the Internet using a single router public IP interface.

Configuration Steps:
1. Define inside and outside interfaces:
```cisco
Router(config)# interface GigabitEthernet0/0
Router(config-if)# ip nat inside
Router(config)# interface GigabitEthernet0/1
Router(config-if)# ip nat outside
```
2. Define standard ACL matching inside traffic:
```cisco
Router(config)# access-list 1 permit 192.168.0.0 0.0.255.255
```
3. Enable NAT overload on outside interface:
```cisco
Router(config)# ip nat inside source list 1 interface GigabitEthernet0/1 overload
```

Verification:
```cisco
Router# show ip nat translations
Router# show ip nat statistics
Router# clear ip nat translation *
```

### Common Mistakes
- Forgetting `ip nat inside` or `ip nat outside` on the relevant interfaces.
- Wildcard mask error in the permit ACL preventing inside host traffic from matching.
