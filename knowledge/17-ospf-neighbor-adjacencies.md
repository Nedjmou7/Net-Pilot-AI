# OSPF Neighbor Adjacency States

Two OSPF routers progress through seven formal states to become fully adjacent:
1. **Down**: No OSPF hello packets received.
2. **Init**: Hello received, but router does not see its own router ID in neighbor's hello.
3. **2-Way**: Bidirectional communication established (DR/BDR election happens here on broadcast networks).
4. **ExStart**: Master/Slave relationship negotiated and initial sequence number chosen.
5. **Exchange**: Database Description (DBD) packets exchanged.
6. **Loading**: Link State Requests (LSR) and Link State Updates (LSU) synchronize the LSDB.
7. **Full**: Routers have identical LSDBs; adjacency is fully established.

Neighbor Requirements:
- Same Area ID
- Same Subnet and Subnet Mask
- Matching Hello (10s) and Dead (40s) timers
- Matching Authentication credentials
- Matching MTU size

### Common Mistakes
- Mismatched MTU causing routers to stick in `EXSTART` or `EXCHANGE` state.
- Mismatched hello/dead intervals preventing neighbor discovery.
