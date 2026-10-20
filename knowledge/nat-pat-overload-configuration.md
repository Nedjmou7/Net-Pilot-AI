# NAT and PAT (Port Address Translation / Overload)

Port Address Translation (PAT), also known as NAT Overload, maps multiple private IP addresses to a single public IP address using unique Layer 4 source port numbers.

```cisco
! 1. Identify inside and outside interfaces
Router(config)# interface GigabitEthernet0/0
Router(config-if)# ip nat inside
Router(config-if)# exit

Router(config)# interface GigabitEthernet0/1
Router(config-if)# ip nat outside
Router(config-if)# exit

! 2. Define standard ACL matching internal private hosts
Router(config)# access-list 1 permit 192.168.10.0 0.0.0.255

! 3. Configure NAT Overload binding
Router(config)# ip nat inside source list 1 interface GigabitEthernet0/1 overload
```

Verification commands:
```cisco
Router# show ip nat translations
Router# show ip nat statistics
Router# clear ip nat translation *
```

### Common Mistakes
- Forgetting `overload` keyword (without it, only one private host can communicate at a time).
- Forgetting `ip nat inside` or `ip nat outside` on the interfaces.
