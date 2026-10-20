import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


BRIDGE_DIR = Path(__file__).resolve().parent
INBOX_DIR = BRIDGE_DIR / "inbox"
INBOX_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="NetBuilder PTBuilder Bridge",
    description="Receives PTBuilder scripts for local inspection.",
    version="1.0.0",
)


class RunRequest(BaseModel):
    script: str = Field(..., min_length=1)


def validate_script(script: str) -> list[str]:
    required_calls = (
        "addDevice(",
        "addLink(",
        "configureIosDevice(",
        "configurePcIp(",
    )
    return [call for call in required_calls if call not in script]


def save_script(script: str) -> Path:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = INBOX_DIR / f"topogemma_build_{timestamp}.js"
    path.write_text(script, encoding="utf-8")
    return path


@app.get("/health")
async def health() -> Dict[str, Any]:
    return {
        "online": True,
        "bridge": "netbuilder-receiver",
        "deployment_supported": False,
        "inbox": str(INBOX_DIR),
    }


@app.post("/run")
async def run(request: RunRequest) -> Dict[str, Any]:
    missing = validate_script(request.script)
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported or incomplete PTBuilder script; missing: {', '.join(missing)}",
        )

    saved_path = save_script(request.script)
    device_count = len(re.findall(r"\baddDevice\(", request.script))
    link_count = len(re.findall(r"\baddLink\(", request.script))
    return {
        "success": True,
        "deployed": False,
        "message": (
            "Script received and saved by the local bridge. "
            "Cisco Packet Tracer was not modified because it has no supported "
            "public deployment API."
        ),
        "script_path": str(saved_path),
        "device_count": device_count,
        "link_count": link_count,
    }


@app.get("/")
async def root() -> Dict[str, str]:
    return {"service": "NetBuilder PTBuilder Bridge", "status": "online"}
