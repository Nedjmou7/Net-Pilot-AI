# IPv4 Address Classes and RFC 1918 Private Ranges

IPv4 addresses are 32-bit values divided into four 8-bit octets. Historically, addresses were organized into classes:
- Class A: 1.0.0.0 to 126.255.255.255 (/8 default mask)
- Class B: 128.0.0.0 to 191.255.255.255 (/16 default mask)
- Class C: 192.0.0.0 to 223.255.255.255 (/24 default mask)
- Class D: 224.0.0.0 to 239.255.255.255 (Multicast)
- Class E: 240.0.0.0 to 255.255.255.254 (Experimental)

RFC 1918 defines non-routable private IP address space reserved for internal enterprise networks:
- `10.0.0.0/8` (10.0.0.0 – 10.255.255.255)
- `172.16.0.0/12` (172.16.0.0 – 172.31.255.255)
- `192.168.0.0/16` (192.168.0.0 – 192.168.255.255)

```cisco
Router(config)# interface GigabitEthernet0/0
Router(config-if)# ip address 192.168.1.1 255.255.255.0
Router(config-if)# no shutdown
```

### Common Mistakes
- Using public IP addresses on internal LANs without NAT.
- Confusing Class B private range (172.16.0.0 - 172.31.255.255) with 172.0.0.0.
- Forgetting that 127.0.0.0/8 is reserved for host loopback testing.
