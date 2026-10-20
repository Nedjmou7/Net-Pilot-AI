# Rapid Per-VLAN Spanning Tree (RPVST+)

RPVST+ (802.1w) provides sub-second convergence using proactive proposal-agreement handshakes.

```cisco
Switch(config)# spanning-tree mode rapid-pvst
```

### Common Mistakes
- Mixing 802.1D and 802.1w switches causing compatibility fallback delays.
