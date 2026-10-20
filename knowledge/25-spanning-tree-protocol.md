# Spanning Tree Protocol (STP) and Election

STP (IEEE 802.1D) prevents Layer 2 switching loops and broadcast storms in networks with redundant physical links by logically placing redundant switch ports into a blocking state.

Root Bridge Election:
1. Lowest Bridge Priority (Default: `32768`).
2. If priority tied: Lowest MAC Address wins.

Port Roles:
- **Root Port (RP)**: Lowest cost path toward the Root Bridge (one per non-root switch).
- **Designated Port (DP)**: Lowest cost path on a segment (forwards traffic; all ports on Root Bridge are DPs).
- **Blocking / Alternate Port**: Discards frames to prevent loops.

Configuration:
```cisco
Switch(config)# spanning-tree vlan 1 priority 4096
! Or using root primary macro:
Switch(config)# spanning-tree vlan 1 root primary
```

### Common Mistakes
- Leaving default priority on all switches, allowing an old unmanaged access switch to become the root bridge.
- Confusing bridge priority increments: must be multiples of 4096.
