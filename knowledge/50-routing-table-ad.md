# Administrative Distance (AD) Comparison

AD defines trustworthiness of routing sources: Connected (0), Static (1), EIGRP internal (90), OSPF (110), RIP (120), External (170).

```cisco
Router# show ip route
```

### Common Mistakes
- Wondering why an OSPF route isn't in the table when a static route exists for the same subnet.
