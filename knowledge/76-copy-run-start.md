# Saving Cisco IOS Configurations

Saves volatile DRAM running-config to non-volatile NVRAM startup-config.

```cisco
Router# copy running-config startup-config
! Shortcut:
Router# write memory
```

### Common Mistakes
- Reloading or rebooting router before saving configuration, losing all lab changes.
