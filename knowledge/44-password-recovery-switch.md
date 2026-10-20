# Cisco Switch Password Recovery

Password recovery on Catalyst switches involves holding Mode button during power-on and renaming `config.text`.

```cisco
switch: rename flash:config.text flash:config.old
switch: boot
```

### Common Mistakes
- Deleting `config.text` instead of renaming it, losing entire device configuration.
