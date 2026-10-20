# Syslog Message Severity Levels

Syslog defines severity levels 0 (Emergency) to 7 (Debugging). Level 4 is Warnings, 5 is Notifications, 6 is Informational.

```cisco
Router(config)# logging host 192.168.1.50
Router(config)# logging trap notifications
```

### Common Mistakes
- Enabling `debug all` in production environments, crashing router CPU.
