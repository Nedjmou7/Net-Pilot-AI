# Variable Length Subnet Masking (VLSM)

Variable Length Subnet Masking (VLSM) allows multiple subnet masks within the same network space, avoiding IP address wastage. The fundamental rule of VLSM is: always allocate subnets in descending order of size (largest host requirements first).

Example allocating `192.168.1.0/24`:
1. Subnet A (Needs 50 hosts): Needs `/26` (`255.255.255.192`), block `192.168.1.0 - 192.168.1.63`.
2. Subnet B (Needs 25 hosts): Needs `/27` (`255.255.255.224`), block `192.168.1.64 - 192.168.1.95`.
3. Subnet C (WAN point-to-point): Needs `/30` (`255.255.255.252`), block `192.168.1.96 - 192.168.1.99`.

```cisco
Router(config)# interface GigabitEthernet0/0
Router(config-if)# ip address 192.168.1.1 255.255.255.192
Router(config)# interface GigabitEthernet0/1
Router(config-if)# ip address 192.168.1.97 255.255.255.252
```

### Common Mistakes
- Subnetting from the bottom up, creating non-contiguous fragmented gaps.
- Overlapping subnets when dividing a parent block into different prefix sizes.
