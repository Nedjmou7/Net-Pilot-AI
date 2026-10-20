# Securing VTY Virtual Terminal Lines

Restricts telnet/SSH access using access-class.

```cisco
Router(config)# line vty 0 4
Router(config-line)# access-class 10 in
```

### Common Mistakes
- Locking yourself out by misconfiguring access-class without permitting management IP.
