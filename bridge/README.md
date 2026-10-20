# NetBuilder PTBuilder Bridge

This local receiver listens on port `39000`, accepts the script sent by the
NetBuilder **Push to PT** action, validates the expected PTBuilder calls, and
saves each script under `bridge/inbox/`.

It does **not** modify Cisco Packet Tracer. Standard Packet Tracer does not
provide a supported public API for creating devices or writing `.pkt` files.

Start it from the project root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn bridge.server:app --host 127.0.0.1 --port 39000
```

Check it:

```powershell
Invoke-RestMethod http://127.0.0.1:39000/health
```
