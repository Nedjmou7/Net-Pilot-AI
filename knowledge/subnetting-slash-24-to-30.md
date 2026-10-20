# Subnetting from /24 to /30 (Variable Length Subnet Masking)

Variable Length Subnet Masking (VLSM) allows network engineers to divide IP space efficiently based on host requirements rather than classful boundaries.

Subnet breakdown for a class C base (e.g. 192.168.1.0):
- `/24`: 255.255.255.0 -> 256 addresses, 254 usable hosts.
- `/25`: 255.255.255.128 -> 128 addresses, 126 usable hosts.
- `/26`: 255.255.255.192 -> 64 addresses, 62 usable hosts.
- `/27`: 255.255.255.224 -> 32 addresses, 30 usable hosts.
- `/28`: 255.255.255.240 -> 16 addresses, 14 usable hosts.
- `/29`: 255.255.255.248 -> 8 addresses, 6 usable hosts.
- `/30`: 255.255.255.252 -> 4 addresses, 2 usable hosts (ideal for point-to-point router links).

```cisco
! Configuring point-to-point /30 link between R1 and R2
R1(config)# interface GigabitEthernet0/1
R1(config-if)# ip address 10.0.0.1 255.255.255.252
R1(config-if)# no shutdown

R2(config)# interface GigabitEthernet0/0
R2(config-if)# ip address 10.0.0.2 255.255.255.252
R2(config-if)# no shutdown
```

### Common Mistakes
- Assigning network ID (e.g. 10.0.0.0) or broadcast address (10.0.0.3) to an interface.
- Using a /24 mask on point-to-point router links, wasting 252 IP addresses.
- Miscalculating block sizes when borrowing bits from the host portion.
