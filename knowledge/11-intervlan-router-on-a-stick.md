# Inter-VLAN Routing with Router-on-a-Stick

Router-on-a-Stick (ROAS) enables routing between different VLANs using a single physical router interface divided into logical subinterfaces. Each subinterface acts as the default gateway for one VLAN.

Configuration on Cisco 2911 Router:
```cisco
Router(config)# interface GigabitEthernet0/0
Router(config-if)# no shutdown
Router(config-if)# exit

Router(config)# interface GigabitEthernet0/0.10
Router(config-subif)# encapsulation dot1Q 10
Router(config-subif)# ip address 192.168.10.1 255.255.255.0

Router(config)# interface GigabitEthernet0/0.20
Router(config-subif)# encapsulation dot1Q 20
Router(config-subif)# ip address 192.168.20.1 255.255.255.0
```

Switch Port connecting to the Router must be configured as a trunk:
```cisco
Switch(config)# interface GigabitEthernet0/1
Switch(config-if)# switchport mode trunk
```

### Common Mistakes
- Forgetting `no shutdown` on the physical parent interface (`GigabitEthernet0/0`).
- Configuring `ip address` before running `encapsulation dot1Q <vlan_id>`.
- Configuring the switch port connecting to the router as an access port instead of a trunk.
