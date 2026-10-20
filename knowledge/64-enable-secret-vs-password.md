# Enable Secret vs Enable Password

`enable secret` uses secure MD5/SHA-256 hash (Type 5/8/9) and supersedes `enable password`.

```cisco
Router(config)# enable secret Cisco123!
```

### Common Mistakes
- Setting `enable password` and `enable secret` to the same string, causing an error.
