# Packet Tracer Device Selection and Cabling Rules

Building networks correctly in Cisco Packet Tracer:

### Supported Hardware Models:
- **Router 2911**: 3x GigabitEthernet ports (0/0, 0/1, 0/2), modular slots for serial cards (HWIC-2T).
- **Router 1941**: 2x GigabitEthernet ports (0/0, 0/1).
- **Switch 2960-24TT**: 24x FastEthernet ports (0/1 to 0/24), 2x GigabitEthernet uplink ports (0/1, 0/2).
- **Switch 3650-24PS**: 24x GigabitEthernet Layer 3 ports.
- **PC-PT / Server-PT**: FastEthernet0.

### Cabling Rules:
- **Straight-Through Cable (Solid Black)**: Connects dissimilar devices:
  - PC to Switch
  - Router to Switch
  - Server to Switch
- **Crossover Cable (Dashed Black)**: Connects similar devices:
  - Router to Router (GigabitEthernet to GigabitEthernet)
  - Switch to Switch
  - PC to PC
- **Serial DTE/DCE Cable (Red lightning cable)**: Point-to-point WAN links between Serial interfaces. Clock rate must be set on DCE side (`clock rate 64000`).

### Common Mistakes
- Using straight-through cable directly between two routers without auto-MDIX.
- Connecting PC to Switch console port instead of FastEthernet.
