# NAT and PAT Concepts

Network Address Translation (NAT) translates private RFC 1918 IPv4 addresses into globally routable public IPv4 addresses.

Types of NAT:
1. **Static NAT**: One-to-one mapping between an internal private IP and an external public IP. Typically used for hosting internal web servers.
2. **Dynamic NAT**: Many-to-many mapping from a pool of public IPs on a first-come, first-served basis.
3. **Port Address Translation (PAT / NAT Overload)**: Many-to-one mapping that translates multiple private IPs to a single public IP using unique source layer 4 port numbers (TCP/UDP).

Terminology:
- **Inside Local**: Private IP of an inside host.
- **Inside Global**: Public IP representing the inside host to the outside.
- **Outside Local**: Outside destination IP as known internally.
- **Outside Global**: Real public IP assigned to the outside destination.

### Common Mistakes
- Confusing inside and outside interfaces.
- Failing to include the `overload` keyword when sharing a single public IP address among multiple hosts.
