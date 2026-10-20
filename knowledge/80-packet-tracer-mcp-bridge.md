# Packet Tracer MCP Live Automation Bridge

Connects external LLM agents and scripts to Cisco Packet Tracer Script Engine via local WebSocket or HTTP bridge.

```json
{"command": "runScript", "script": "addDevice('R1', '2911', 200, 200);"}
```

### Common Mistakes
- Running bridge on wrong port or failing to enable Script Modules inside Packet Tracer extensions.
