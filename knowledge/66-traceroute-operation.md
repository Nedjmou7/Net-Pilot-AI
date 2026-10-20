# Traceroute Operation and Troubleshooting

Traceroute uses incrementing IP TTL values (starting at 1) to identify each Layer 3 hop.

```cisco
Router# traceroute 192.168.2.10
```

### Common Mistakes
- Confusing asterisks `* * *` with total packet loss; firewalls frequently drop TTL-expired ICMP messages.
