# Static NAT for Inbound Web Servers

Static NAT maps one public IP to one internal server IP.

```cisco
Router(config)# ip nat inside source static 192.168.1.100 203.0.113.10
```

### Common Mistakes
- Forgetting `ip nat inside` and `ip nat outside` on the corresponding interfaces.
