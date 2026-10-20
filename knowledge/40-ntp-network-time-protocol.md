# Network Time Protocol (NTP)

NTP synchronizes clocks across network devices, crucial for syslog and security audits.

```cisco
Router(config)# ntp server 192.168.1.100
Router# show ntp status
```

### Common Mistakes
- Mismatched time zones causing log discrepancies between devices.
