# SNMP Protocol and Management

Simple Network Management Protocol monitors network health via MIBs and OIDs. SNMPv3 adds authentication and encryption.

```cisco
Router(config)# snmp-server community public ro
```

### Common Mistakes
- Using default community strings like `public` or `private` with read-write access.
