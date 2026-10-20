# Console and VTY Exec-Timeout

Sets session inactivity disconnect timer.

```cisco
Router(config-line)# exec-timeout 10 0
! Disable timeout for lab sessions:
Router(config-line)# exec-timeout 0 0
```

### Common Mistakes
- Setting `exec-timeout 0 0` in production environments, leaving open terminals accessible.
