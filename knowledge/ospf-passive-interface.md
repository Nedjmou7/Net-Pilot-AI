# OSPF Passive Interface Configuration

Configuring an interface as passive prevents OSPF from transmitting Hello packets out of that port, protecting LANs from unauthorized rogue routers and saving CPU/bandwidth, while still advertising the connected subnet into OSPF.

```cisco
Router(config)# router ospf 1
Router(config-router)# passive-interface GigabitEthernet0/0
```

Alternative best practice (passive by default):
```cisco
Router(config)# router ospf 1
Router(config-router)# passive-interface default
Router(config-router)# no passive-interface GigabitEthernet0/1
```

Verification:
```cisco
Router# show ip ospf interface GigabitEthernet0/0
```

### Common Mistakes
- Making a link connecting two routers passive, which prevents neighbor adjacencies from forming.
