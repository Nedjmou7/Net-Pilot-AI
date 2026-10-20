# Static Routing and Default Routes

Static routes provide deterministic packet forwarding manually configured by an administrator.

Command syntax:
`ip route <dest_network> <subnet_mask> {next_hop_ip | exit_interface} [distance]`

Default Route (Gateway of Last Resort):
```cisco
Router(config)# ip route 0.0.0.0 0.0.0.0 10.0.0.2
```

Specific Network Route:
```cisco
Router(config)# ip route 192.168.20.0 255.255.255.0 10.0.0.2
```

Floating Static Route (Backup route with higher Administrative Distance):
```cisco
Router(config)# ip route 192.168.20.0 255.255.255.0 10.0.1.2 100
```

Verification:
```cisco
Router# show ip route static
```

### Common Mistakes
- Pointing next-hop to an unreachable IP address.
- Specifying an exit interface on a multi-access Ethernet link without next-hop IP, causing excessive ARP requests.
