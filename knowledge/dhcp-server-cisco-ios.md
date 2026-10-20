# Configuring Cisco IOS DHCP Server

A Cisco router can serve as a local DHCP server to dynamically assign IP addresses, subnet masks, default gateways, and DNS servers to client PCs.

```cisco
! Step 1: Exclude static and gateway addresses
Router(config)# ip dhcp excluded-address 192.168.10.1 192.168.10.10

! Step 2: Define DHCP pool
Router(config)# ip dhcp pool LAN_POOL
Router(dhcp-config)# network 192.168.10.0 255.255.255.0
Router(dhcp-config)# default-router 192.168.10.1
Router(dhcp-config)# dns-server 8.8.8.8 1.1.1.1
Router(dhcp-config)# domain-name corp.local
Router(dhcp-config)# lease 1 0 0
```

Verification commands:
```cisco
Router# show ip dhcp binding
Router# show ip dhcp pool
Router# show ip dhcp conflict
```

### Common Mistakes
- Forgetting to exclude the router's own interface IP, creating IP conflict errors on the LAN.
- Putting the wrong default-router address inside the DHCP pool.
