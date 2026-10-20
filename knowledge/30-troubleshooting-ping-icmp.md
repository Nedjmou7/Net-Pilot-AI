# Ping Diagnostics and ICMP Troubleshooting

The `ping` command uses ICMP Echo Request (Type 8) and ICMP Echo Reply (Type 0) to test Layer 3 reachability.

Cisco IOS Ping Characters:
- `!`: Successful Echo Reply received.
- `.`: Timed out waiting for reply (often ARP delay or routing black hole).
- `U`: Destination Unreachable ICMP packet returned by router.
- `Q`: Source quench (device congested).
- `M`: Could not fragment.

Extended Ping:
```cisco
Router# ping
Target IP address: 192.168.2.10
Repeat count [5]: 10
Datagram size [100]: 1500
Source address or interface: 10.0.12.1
```

Step-by-step Troubleshooting Path:
1. Ping `127.0.0.1` (verifies local TCP/IP protocol stack).
2. Ping local device IP address (verifies NIC hardware).
3. Ping default gateway IP (verifies local LAN and switch connectivity).
4. Ping remote router IP (verifies routing table and WAN links).
5. Ping remote host or server.

### Common Mistakes
- Panicking on the first `.` of a 5-packet ping: the first packet is often dropped while the switch/router resolves ARP.
- Forgetting that host personal firewalls (Windows Defender) drop ICMP requests by default.
