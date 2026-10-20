# Spanning Tree Protocol (STP & PVST+)

STP (IEEE 802.1D) and Rapid PVST+ (802.1w) prevent Layer 2 bridging loops, broadcast storms, and MAC database corruption in redundant switched topologies.

Root Bridge Election:
Switch with the lowest Bridge ID (Priority + Sys-ID-Extension + MAC Address) becomes Root Bridge. Default priority is 32768.

```cisco
! Set Switch as Primary Root Bridge for VLAN 10 and 20
Switch(config)# spanning-tree vlan 10,20 root primary

! Or configure priority manually (multiples of 4096)
Switch(config)# spanning-tree vlan 10 priority 4096
Switch(config)# spanning-tree mode rapid-pvst
```

Verification:
```cisco
Switch# show spanning-tree
Switch# show spanning-tree vlan 10
```

### Common Mistakes
- Leaving default priority on all switches, resulting in an old access switch with lowest MAC becoming Root Bridge.
- Setting priority to a number not divisible by 4096.
