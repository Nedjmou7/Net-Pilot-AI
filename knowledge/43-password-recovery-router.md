# Cisco Router Password Recovery

Password recovery changes configuration register to `0x2142` to bypass NVRAM startup-config.

```cisco
rommon 1> confreg 0x2142
rommon 2> reset
```

### Common Mistakes
- Forgetting to set config-register back to `0x2102` after recovering password.
