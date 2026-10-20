# Router-on-a-Stick Inter-VLAN Routing

Router-on-a-Stick (ROAS) uses a single physical router interface divided into virtual subinterfaces to route packets between different VLANs over an 802.1Q trunk link.

```cisco
! Router Configuration
Router(config)# interface GigabitEthernet0/0
Router(config-if)# no shutdown
Router(config-if)# exit

Router(config)# interface GigabitEthernet0/0.10
Router(config-subif)# encapsulation dot1Q 10
Router(config-subif)# ip address 192.168.10.1 255.255.255.0
Router(config-subif)# exit

Router(config)# interface GigabitEthernet0/0.20
Router(config-subif)# encapsulation dot1Q 20
Router(config-subif)# ip address 192.168.20.1 255.255.255.0
Router(config-subif)# exit

! Connected Switch Port Configuration
Switch(config)# interface GigabitEthernet0/1
Switch(config-if)# switchport mode trunk
```

### Common Mistakes
- Configuring `ip address` before `encapsulation dot1Q <vlan_id>` (IOS rejects IP address assignment without encapsulation defined).
- Forgetting `no shutdown` on the physical parent interface (GigabitEthernet0/0).
- Leaving the connecting switch port in access mode instead of trunk mode.
