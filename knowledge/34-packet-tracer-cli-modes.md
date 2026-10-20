# Cisco IOS CLI Navigation and Modes

Cisco IOS features a hierarchical command mode structure:

1. **User EXEC Mode** (`Router>`):
   - Basic view-only diagnostic commands.
   - Enter Privileged EXEC: `enable`.

2. **Privileged EXEC Mode** (`Router#`):
   - Detailed troubleshooting, `show` commands, file operations, `ping`, `traceroute`, `write memory`.
   - Enter Global Config: `configure terminal`.

3. **Global Configuration Mode** (`Router(config)#`):
   - System-wide settings: `hostname`, `ip routing`, `vlan`.
   - Sub-modes:
     * Interface: `interface GigabitEthernet0/0` -> `Router(config-if)#`
     * Subinterface: `interface Gi0/0.10` -> `Router(config-subif)#`
     * Line: `line console 0` -> `Router(config-line)#`
     * Routing: `router ospf 1` -> `Router(config-router)#`

Navigation:
- `exit`: Moves up one level.
- `end` or `Ctrl+Z`: Returns directly to Privileged EXEC (`#`).

### Common Mistakes
- Trying to execute `configure terminal` commands from User EXEC mode (`>`).
- Forgetting `do` prefix when running `show` commands from within configuration submodes (e.g. `do show ip route`).
