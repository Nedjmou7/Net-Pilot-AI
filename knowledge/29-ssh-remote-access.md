# Configuring Secure Shell (SSH) Remote Management

Telnet transmits management credentials in plaintext. Secure Shell (SSH) encrypts all session communication using cryptographic keys.

Cisco IOS SSH Prerequisites:
1. Hostname must not be the default `Router` or `Switch`.
2. IP domain name must be configured.
3. RSA crypto key pair generated (minimum 1024 bits for SSHv2).
4. Local user account with password or secret.
5. VTY lines set to accept SSH.

Configuration:
```cisco
Router(config)# hostname R1
R1(config)# ip domain-name cisco.lab
R1(config)# crypto key generate rsa modulus 2048
R1(config)# ip ssh version 2
R1(config)# username admin privilege 15 secret Cisco123!
R1(config)# line vty 0 4
R1(config-line)# login local
R1(config-line)# transport input ssh
R1(config-line)# exit
```

### Common Mistakes
- Attempting `crypto key generate rsa` with default hostname `Router`, which fails.
- Leaving `transport input telnet` or omitting `login local` on VTY lines.
