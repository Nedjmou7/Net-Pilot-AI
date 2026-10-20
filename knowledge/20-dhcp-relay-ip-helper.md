# DHCP Relay and IP Helper-Address

DHCP client requests are broadcast packets (`255.255.255.255`). Routers drop broadcast packets by default. When the centralized DHCP server is located on a different subnet or across a WAN, the router interface facing the clients must be configured with `ip helper-address` to relay broadcast requests as unicast packets to the DHCP server.

Configuration:
```cisco
Router(config)# interface GigabitEthernet0/0
Router(config-if)# ip helper-address 10.1.1.50
```

When using Router-on-a-Stick:
```cisco
Router(config)# interface GigabitEthernet0/0.10
Router(config-subif)# ip helper-address 10.1.1.50
```

### Common Mistakes
- Applying `ip helper-address` on the interface facing the server instead of the interface facing the client broadcast domain.
- Forgetting to route traffic between the client subnet and the DHCP server.
