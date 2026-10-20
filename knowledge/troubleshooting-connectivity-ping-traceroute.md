# Troubleshooting Network Connectivity with Ping and Traceroute

Cisco ICMP troubleshooting workflow:

1. **Ping Loopback (`127.0.0.1`)**: Verifies local TCP/IP protocol stack is functioning on host.
2. **Ping Local IP**: Verifies local NIC and IP driver operation.
3. **Ping Default Gateway**: Verifies local Layer 1 cable, Layer 2 switchport, and router interface.
4. **Ping Remote Gateway/Server**: Tests end-to-end IP routing.
5. **Traceroute (`traceroute` / `tracert`)**: Identifies the exact hop where packet forwarding fails.

Extended Ping from Cisco IOS CLI:
```cisco
Router# ping
Protocol [ip]: 
Target IP address: 192.168.20.10
Repeat count [5]: 10
Datagram size [100]: 
Timeout in seconds [2]: 
Extended commands [n]: y
Source address or interface: 192.168.10.1
```

Common responses:
- `!` : Successful ICMP Echo Reply
- `.` : Timed out
- `U` : Destination unreachable (typically no route or blocked by ACL)

### Common Mistakes
- Assuming ping failure means device is down when host firewall is blocking ICMP Echo requests.
