# DHCP Relay Agent (ip helper-address)

DHCP Discover broadcasts (255.255.255.255) cannot traverse routers by default. When the DHCP server resides on a different subnet or centralized server farm, the router interface facing the clients must be configured with `ip helper-address` to convert broadcasts into unicast packets.

```cisco
Router(config)# interface GigabitEthernet0/0
Router(config-if)# ip helper-address 10.10.10.50
```

The router forwards UDP ports:
- TFTP (Port 69)
- DNS (Port 53)
- Time (Port 37)
- TACACS (Port 49)
- DHCP/BOOTP Server (Port 67) & Client (Port 68)

### Common Mistakes
- Placing `ip helper-address` on the interface facing the server instead of the interface receiving client broadcast requests.
