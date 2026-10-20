# Packet Tracer Supported Device Models

TopoGemma supports standard Cisco models in Packet Tracer:

1. **Cisco 2911 Integrated Services Router**:
   - 3 Onboard GigabitEthernet ports: `GigabitEthernet0/0`, `GigabitEthernet0/1`, `GigabitEthernet0/2`.
   - Expansion slots for HWIC-2T serial modules.

2. **Cisco 1941 Router**:
   - 2 Onboard GigabitEthernet ports: `GigabitEthernet0/0`, `GigabitEthernet0/1`.

3. **Cisco 2960-24TT Layer 2 Switch**:
   - 24 FastEthernet access ports: `FastEthernet0/1` to `FastEthernet0/24`.
   - 2 GigabitEthernet uplink ports: `GigabitEthernet0/1`, `GigabitEthernet0/2`.

4. **Cisco 3560-24PS Layer 3 Multilayer Switch**:
   - 24 FastEthernet ports + 2 Gigabit uplinks.
   - Supports hardware routing via `ip routing` and SVIs.

5. **PC-PT and Server-PT**:
   - Single NIC: `FastEthernet0`.

### Common Mistakes
- Requesting `GigabitEthernet0/3` on a 2911 router (only ports 0/0, 0/1, 0/2 exist onboard).
- Assuming standard 2960 switch can route IP traffic without an external router.
