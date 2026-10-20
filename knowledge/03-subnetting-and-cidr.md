# Subnetting and CIDR Notation

Classless Inter-Domain Routing (CIDR) eliminates rigid class boundaries by allowing arbitrary prefix lengths denoted with a slash (`/`). Subnetting borrows bits from the host portion of an address and assigns them to the network prefix.

Key Formulas:
- Number of Subnets = `2^s` (where `s` is borrowed subnet bits)
- Usable Hosts per Subnet = `2^h - 2` (where `h` is remaining host bits)
- Common Prefix Masks:
  * `/24` = `255.255.255.0` (254 hosts)
  * `/25` = `255.255.255.128` (126 hosts)
  * `/26` = `255.255.255.192` (62 hosts)
  * `/27` = `255.255.255.224` (30 hosts)
  * `/28` = `255.255.255.240` (14 hosts)
  * `/29` = `255.255.255.248` (6 hosts)
  * `/30` = `255.255.255.252` (2 hosts, ideal for point-to-point router links)

```cisco
Router(config)# interface GigabitEthernet0/1
Router(config-if)# ip address 10.0.0.1 255.255.255.252
Router(config-if)# no shutdown
```

### Common Mistakes
- Forgetting to subtract 2 for the network ID and broadcast address when calculating required host capacity.
- Miscalculating the magic number increment (`256 - mask_octet`), causing subnets to overlap.
