# Disabling DNS Lookup for Typos

Prevents CLI freezes when mistyping commands.

```cisco
Router(config)# no ip domain-lookup
```

### Common Mistakes
- Forgetting to re-enable domain lookup if the router legitimately requires DNS resolution.
