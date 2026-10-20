# Named Access Control Lists

Named ACLs allow editing specific sequence numbers and use human-readable identifiers.

```cisco
Router(config)# ip access-list extended SECURE_WEB
Router(config-ext-nacl)# permit tcp 10.0.0.0 0.255.255.255 any eq 443
```

### Common Mistakes
- Forgetting statement sequence numbers when inserting rules between existing lines.
