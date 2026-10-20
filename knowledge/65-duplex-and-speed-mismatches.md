# Duplex and Speed Mismatches

Mismatched duplex (Half vs Full) causes late collisions, FCS errors, and packet throughput drops.

```cisco
Switch(config-if)# speed auto
Switch(config-if)# duplex auto
```

### Common Mistakes
- Hardcoding full duplex on one side while leaving auto-negotiation on the other.
