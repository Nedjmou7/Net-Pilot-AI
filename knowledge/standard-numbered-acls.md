# Standard Numbered ACLs (1-99)

Standard Access Control Lists filter traffic based ONLY on the source IPv4 address.
Standard ACL numbered range: 1 to 99 and 1300 to 1999.

Placement guideline: Place standard ACLs as close to the **destination** as possible (to prevent prematurely blocking traffic destined for other networks).

```cisco
! Allow host 192.168.10.10 and subnet 192.168.20.0/24, deny everything else
Router(config)# access-list 10 permit host 192.168.10.10
Router(config)# access-list 10 permit 192.168.20.0 0.0.0.255
Router(config)# access-list 10 deny any

! Apply to interface
Router(config)# interface GigabitEthernet0/1
Router(config-if)# ip access-group 10 out
```

### Common Mistakes
- Forgetting the implicit `deny any` at the end of every ACL. If you do not have at least one permit statement, all traffic is dropped.
- Placing standard ACLs too close to the source, accidentally cutting off access to other permitted destinations.
