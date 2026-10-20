# Configuring Secure Remote Access (SSH and Passwords)

Telnet sends credentials in plain text; SSH encrypts all management traffic.

Configuration sequence:
```cisco
Router(config)# hostname R1
R1(config)# ip domain-name lab.local
R1(config)# crypto key generate rsa modulus 2048
R1(config)# ip ssh version 2
R1(config)# username admin privilege 15 secret Cisco123!
R1(config)# enable secret CiscoEnable123!

R1(config)# line vty 0 4
R1(config-line)# transport input ssh
R1(config-line)# login local
R1(config-line)# exec-timeout 5 0
R1(config-line)# logging synchronous
R1(config-line)# exit

R1(config)# service password-encryption
```

Verification:
```cisco
R1# show ip ssh
```

### Common Mistakes
- Forgetting to configure a hostname and `ip domain-name` prior to running `crypto key generate rsa`.
- Allowing Telnet in production environments.
