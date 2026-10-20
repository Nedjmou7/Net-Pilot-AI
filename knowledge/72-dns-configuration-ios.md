# DNS Client Configuration on Cisco IOS

Enables domain name resolution on Cisco routers.

```cisco
Router(config)# ip domain-lookup
Router(config)# ip name-server 8.8.8.8 1.1.1.1
```

### Common Mistakes
- Typos in commands causing router to hang trying to resolve typo via broadcast DNS when `ip domain-lookup` is enabled.
