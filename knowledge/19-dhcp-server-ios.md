# Cisco IOS DHCP Server Configuration

Cisco IOS routers can serve as dynamic DHCP servers for LAN clients, distributing IP addresses, subnet masks, default gateways, and DNS servers.

Configuration:
```cisco
Router(config)# ip dhcp excluded-address 192.168.10.1 192.168.10.10
Router(config)# ip dhcp pool LAN_POOL_10
Router(dhcp-config)# network 192.168.10.0 255.255.255.0
Router(dhcp-config)# default-router 192.168.10.1
Router(dhcp-config)# dns-server 8.8.8.8
Router(dhcp-config)# domain-name company.local
Router(dhcp-config)# lease 7
```

Verification:
```cisco
Router# show ip dhcp binding
Router# show ip dhcp pool
Router# show ip dhcp conflict
```

### Common Mistakes
- Forgetting `ip dhcp excluded-address` for the router's own interface IP, creating duplicate IP conflicts.
- Typo in `default-router` pointing hosts to an unroutable IP address.
