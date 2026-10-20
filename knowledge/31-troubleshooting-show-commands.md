# Essential Cisco IOS Show Commands

The following `show` commands form the foundation of CCNA network diagnostics:

1. Interface Verification:
```cisco
Router# show ip interface brief
```
Checks IP assignments and Status/Protocol states (`up/up` is functional; `up/down` indicates layer 2 framing/clocking fault; `administratively down` indicates `shutdown` command).

2. Routing Table:
```cisco
Router# show ip route
```
Inspect codes: `C` (Connected), `S` (Static), `O` (OSPF), `D` (EIGRP), `R` (RIP). Verify presence of destination network or `0.0.0.0/0`.

3. CDP Neighbors (Layer 2 discovery):
```cisco
Router# show cdp neighbors
Router# show cdp neighbors detail
```
Discovers directly connected Cisco devices, remote port names, and IP addresses.

4. Switch MAC Table:
```cisco
Switch# show mac address-table
```

### Common Mistakes
- Overlooking the difference between status `down` and `administratively down`.
- Forgetting to check `show ip route` before assuming physical link or cable failure.
