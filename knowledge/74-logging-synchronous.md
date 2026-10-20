# Logging Synchronous on Console

Prevents console log messages from disrupting currently typed commands.

```cisco
Router(config)# line console 0
Router(config-line)# logging synchronous
Router(config)# line vty 0 4
Router(config-line)# logging synchronous
```

### Common Mistakes
- Forgetting to apply `logging synchronous` to both console and VTY lines.
