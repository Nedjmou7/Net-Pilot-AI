# Packet Tracer PTBuilder Scripting Guide

PTBuilder allows programmatic creation and automated configuration of Packet Tracer topologies using JavaScript.

Key PTBuilder API Functions:
- `addDevice(name, model, x, y)`: Instantiates a device on the canvas at coordinate `(x, y)`.
- `addLink(dev1, port1, dev2, port2, cable)`: Connects two devices using specified cable type (`straight`, `crossover`, `serial`).
- `configureIosDevice(name, cliConfigString)`: Sends CLI configuration script to router or switch terminal.
- `configurePcIp(name, isDhcp, ip, mask, gateway)`: Configures IP desktop settings on PC or Server.

Deployment in Packet Tracer:
1. Open Cisco Packet Tracer.
2. Navigate to **Extensions** -> **Scripting** -> **Configure PT Script Modules** (or PTBuilder Runner).
3. Paste the generated script and click **Run**.

### Common Mistakes
- Attempting to connect a link to a port that is already in use by another device.
- Passing lowercase port abbreviations (`gi0/0`) instead of canonical names (`GigabitEthernet0/0`).
