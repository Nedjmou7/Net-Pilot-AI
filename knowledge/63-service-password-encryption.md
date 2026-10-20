# Service Password Encryption

Encrypts plaintext passwords in running-config with weak Type 7 reversible obfuscation.

```cisco
Router(config)# service password-encryption
```

### Common Mistakes
- Relying on Type 7 passwords for strong security instead of Type 8 or 9 (PBKDF2/scrypt).
