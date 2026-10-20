# Packet Tracer Cable Types and Connections

Connecting network devices requires matching the physical cable type to the MDI/MDIX specification:

1. **Straight-Through Cable (Solid Black Line in PT)**:
   - Connects unlike devices:
     * Switch to Router
     * Switch to PC / Server
     * Hub to PC

2. **Crossover Cable (Dashed Black Line in PT)**:
   - Connects like devices:
     * Switch to Switch
     * Router to Router (GigabitEthernet)
     * PC to PC
     * PC to Router (both use MDI pinouts!)

3. **Serial DTE/DCE Cable (Red Lightning Bolt in PT)**:
   - Connects router serial WAN interfaces (HWIC-2T).
   - The DCE end provides clock rate: `clock rate 64000`.

4. **Console Cable (Light Blue Line)**:
   - Connects PC RS-232 serial port to Router/Switch Console port.

### Common Mistakes
- Connecting a PC directly to a Router Ethernet port using a straight-through cable in Packet Tracer (must use crossover cable).
- Forgetting `clock rate` on the DCE serial interface in Packet Tracer.
