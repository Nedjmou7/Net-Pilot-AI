# Cisco Discovery Protocol (CDP)

CDP is a proprietary Layer 2 protocol used to discover directly connected Cisco equipment.

```cisco
Router(config)# cdp run
Router(config-if)# cdp enable
Router# show cdp neighbors detail
```

### Common Mistakes
- Leaving CDP enabled on untrusted external interfaces, exposing internal topology to attackers.
