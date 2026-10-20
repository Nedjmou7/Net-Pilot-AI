import os
import json
import httpx
from typing import AsyncGenerator, Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma4:e4b")
DEFAULT_TIMEOUT = 120.0
NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "1024"))


async def check_health() -> Dict[str, Any]:
    """Check if Ollama service is reachable and retrieve list of available models."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{OLLAMA_URL}/api/tags")
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name") for m in data.get("models", [])]
                model_present = any(
                    model == OLLAMA_MODEL or model.startswith(f"{OLLAMA_MODEL}:")
                    for model in models
                )
                return {
                    "online": True,
                    "model": OLLAMA_MODEL,
                    "model_installed": model_present,
                    "available_models": models
                }
    except Exception:
        pass
    return {
        "online": False,
        "model": OLLAMA_MODEL,
        "model_installed": False,
        "available_models": []
    }


_ollama_alive = None


async def is_ollama_running() -> bool:
    global _ollama_alive
    if _ollama_alive is None:
        try:
            async with httpx.AsyncClient(timeout=1.0) as client:
                resp = await client.get(f"{OLLAMA_URL}/api/tags")
                if resp.status_code == 200:
                    data = resp.json()
                    models = [m.get("name", "") for m in data.get("models", [])]
                    _ollama_alive = any(
                        model == OLLAMA_MODEL or model.startswith(f"{OLLAMA_MODEL}:")
                        for model in models
                    )
                else:
                    _ollama_alive = False
        except Exception:
            _ollama_alive = False
    return _ollama_alive


async def chat(
    messages: List[Dict[str, str]],
    temperature: float = 0.2,
    format_json: bool = False,
    timeout: float = DEFAULT_TIMEOUT,
    num_predict: Optional[int] = None
) -> str:
    """Async chat request to Ollama with timeout and optional JSON structure enforcement."""
    if not await is_ollama_running():
        return generate_offline_fallback(messages, format_json)

    payload: Dict[str, Any] = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "think": False,
        "keep_alive": "5m",
        "options": {
            "temperature": temperature,
            "num_predict": num_predict or NUM_PREDICT
        }
    }
    if format_json:
        payload["format"] = "json"

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("message", {}).get("content", "")
    except Exception:
        if format_json:
            return generate_offline_fallback(messages, format_json)
        raise


async def stream_chat(
    messages: List[Dict[str, str]],
    temperature: float = 0.2,
    timeout: float = DEFAULT_TIMEOUT
) -> AsyncGenerator[str, None]:
    """Stream response tokens from Ollama."""
    if not await is_ollama_running():
        fallback_msg = generate_offline_fallback(messages, False)
        for word in fallback_msg.split(" "):
            yield word + " "
        return

    payload: Dict[str, Any] = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": True,
        "think": False,
        "keep_alive": "5m",
        "options": {
            "temperature": temperature,
            "num_predict": NUM_PREDICT
        }
    }

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream("POST", f"{OLLAMA_URL}/api/chat", json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line:
                        chunk = json.loads(line)
                        content = chunk.get("message", {}).get("content", "")
                        if content:
                            yield content
    except Exception:
        fallback_msg = generate_offline_fallback(messages, False)
        for word in fallback_msg.split(" "):
            yield word + " "


def generate_offline_fallback(messages: List[Dict[str, str]], format_json: bool) -> str:
    """Provide realistic mock response when Ollama daemon is offline, enabling zero-crash demo."""
    user_prompts = [m["content"].lower() for m in messages if m.get("role") == "user"]
    primary_msg = user_prompts[0] if user_prompts else ""

    if format_json:
        if "vlan" in primary_msg or "stick" in primary_msg:
            return json.dumps({
                "name": "vlan-segmented-network",
                "devices": [
                    {"id": "R1", "type": "router", "model": "2911", "x": 350, "y": 120},
                    {"id": "SW1", "type": "switch", "model": "2960-24TT", "x": 350, "y": 270},
                    {"id": "PC1", "type": "pc", "model": "PC-PT", "x": 200, "y": 420},
                    {"id": "PC2", "type": "pc", "model": "PC-PT", "x": 500, "y": 420}
                ],
                "links": [
                    {"a": "R1", "a_port": "GigabitEthernet0/0", "b": "SW1", "b_port": "GigabitEthernet0/1", "cable": "straight"},
                    {"a": "SW1", "a_port": "FastEthernet0/1", "b": "PC1", "b_port": "FastEthernet0", "cable": "straight"},
                    {"a": "SW1", "a_port": "FastEthernet0/2", "b": "PC2", "b_port": "FastEthernet0", "cable": "straight"}
                ],
                "vlans": [
                    {"id": 10, "name": "STAFF"},
                    {"id": 20, "name": "GUESTS"}
                ],
                "ip_plan": [
                    {"device": "R1", "interface": "GigabitEthernet0/0.10", "ip": "192.168.10.1", "mask": "255.255.255.0", "gateway": None},
                    {"device": "R1", "interface": "GigabitEthernet0/0.20", "ip": "192.168.20.1", "mask": "255.255.255.0", "gateway": None},
                    {"device": "PC1", "interface": "FastEthernet0", "ip": "192.168.10.10", "mask": "255.255.255.0", "gateway": "192.168.10.1"},
                    {"device": "PC2", "interface": "FastEthernet0", "ip": "192.168.20.10", "mask": "255.255.255.0", "gateway": "192.168.20.1"}
                ],
                "routing": {"protocol": "none", "process_id": None, "area": None},
                "services": {
                    "dhcp": [
                        {"pool_name": "STAFF_POOL", "network": "192.168.10.0", "mask": "255.255.255.0", "default_router": "192.168.10.1", "dns_server": "8.8.8.8"},
                        {"pool_name": "GUEST_POOL", "network": "192.168.20.0", "mask": "255.255.255.0", "default_router": "192.168.20.1", "dns_server": "8.8.8.8"}
                    ],
                    "nat": None,
                    "acls": []
                }
            })
        elif "2 router" in primary_msg or "two router" in primary_msg:
            return json.dumps({
                "name": "two-router-interconnect",
                "devices": [
                    {"id": "R1", "type": "router", "model": "2911", "x": 250, "y": 140},
                    {"id": "R2", "type": "router", "model": "2911", "x": 550, "y": 140},
                    {"id": "SW1", "type": "switch", "model": "2960-24TT", "x": 250, "y": 280},
                    {"id": "SW2", "type": "switch", "model": "2960-24TT", "x": 550, "y": 280},
                    {"id": "PC1", "type": "pc", "model": "PC-PT", "x": 180, "y": 430},
                    {"id": "PC2", "type": "pc", "model": "PC-PT", "x": 320, "y": 430},
                    {"id": "PC3", "type": "pc", "model": "PC-PT", "x": 480, "y": 430},
                    {"id": "PC4", "type": "pc", "model": "PC-PT", "x": 620, "y": 430}
                ],
                "links": [
                    {"a": "R1", "a_port": "GigabitEthernet0/1", "b": "R2", "b_port": "GigabitEthernet0/1", "cable": "cross"},
                    {"a": "R1", "a_port": "GigabitEthernet0/0", "b": "SW1", "b_port": "GigabitEthernet0/1", "cable": "straight"},
                    {"a": "R2", "a_port": "GigabitEthernet0/0", "b": "SW2", "b_port": "GigabitEthernet0/1", "cable": "straight"},
                    {"a": "SW1", "a_port": "FastEthernet0/1", "b": "PC1", "b_port": "FastEthernet0", "cable": "straight"},
                    {"a": "SW1", "a_port": "FastEthernet0/2", "b": "PC2", "b_port": "FastEthernet0", "cable": "straight"},
                    {"a": "SW2", "a_port": "FastEthernet0/1", "b": "PC3", "b_port": "FastEthernet0", "cable": "straight"},
                    {"a": "SW2", "a_port": "FastEthernet0/2", "b": "PC4", "b_port": "FastEthernet0", "cable": "straight"}
                ],
                "vlans": [],
                "ip_plan": [
                    {"device": "R1", "interface": "GigabitEthernet0/1", "ip": "10.0.0.1", "mask": "255.255.255.252", "gateway": None},
                    {"device": "R2", "interface": "GigabitEthernet0/1", "ip": "10.0.0.2", "mask": "255.255.255.252", "gateway": None},
                    {"device": "R1", "interface": "GigabitEthernet0/0", "ip": "192.168.1.1", "mask": "255.255.255.0", "gateway": None},
                    {"device": "R2", "interface": "GigabitEthernet0/0", "ip": "192.168.2.1", "mask": "255.255.255.0", "gateway": None},
                    {"device": "PC1", "interface": "FastEthernet0", "ip": "192.168.1.10", "mask": "255.255.255.0", "gateway": "192.168.1.1"},
                    {"device": "PC2", "interface": "FastEthernet0", "ip": "192.168.1.11", "mask": "255.255.255.0", "gateway": "192.168.1.1"},
                    {"device": "PC3", "interface": "FastEthernet0", "ip": "192.168.2.10", "mask": "255.255.255.0", "gateway": "192.168.2.1"},
                    {"device": "PC4", "interface": "FastEthernet0", "ip": "192.168.2.11", "mask": "255.255.255.0", "gateway": "192.168.2.1"}
                ],
                "routing": {"protocol": "ospf", "process_id": 1, "area": 0},
                "services": {"dhcp": [], "nat": None, "acls": []}
            })
        elif "1 router" in primary_msg or "single router" in primary_msg:
            return json.dumps({
                "name": "single-router-office-lan",
                "devices": [
                    {"id": "R1", "type": "router", "model": "2911", "x": 350, "y": 120},
                    {"id": "SW1", "type": "switch", "model": "2960-24TT", "x": 350, "y": 260},
                    {"id": "PC1", "type": "pc", "model": "PC-PT", "x": 200, "y": 420},
                    {"id": "PC2", "type": "pc", "model": "PC-PT", "x": 500, "y": 420}
                ],
                "links": [
                    {"a": "R1", "a_port": "GigabitEthernet0/0", "b": "SW1", "b_port": "GigabitEthernet0/1", "cable": "straight"},
                    {"a": "SW1", "a_port": "FastEthernet0/1", "b": "PC1", "b_port": "FastEthernet0", "cable": "straight"},
                    {"a": "SW1", "a_port": "FastEthernet0/2", "b": "PC2", "b_port": "FastEthernet0", "cable": "straight"}
                ],
                "vlans": [],
                "ip_plan": [
                    {"device": "R1", "interface": "GigabitEthernet0/0", "ip": "192.168.1.1", "mask": "255.255.255.0", "gateway": None},
                    {"device": "PC1", "interface": "FastEthernet0", "ip": "192.168.1.10", "mask": "255.255.255.0", "gateway": "192.168.1.1"},
                    {"device": "PC2", "interface": "FastEthernet0", "ip": "192.168.1.11", "mask": "255.255.255.0", "gateway": "192.168.1.1"}
                ],
                "routing": {"protocol": "none", "process_id": None, "area": None},
                "services": {
                    "dhcp": [
                        {"pool_name": "OFFICE_POOL", "network": "192.168.1.0", "mask": "255.255.255.0", "default_router": "192.168.1.1", "dns_server": "8.8.8.8"}
                    ],
                    "nat": None,
                    "acls": []
                }
            })
        else:
            # 3 routers OSPF default
            return json.dumps({
                "name": "3-router-ospf-network",
                "devices": [
                    {"id": "R1", "type": "router", "model": "2911", "x": 200, "y": 120},
                    {"id": "R2", "type": "router", "model": "2911", "x": 450, "y": 120},
                    {"id": "R3", "type": "router", "model": "2911", "x": 700, "y": 120},
                    {"id": "SW1", "type": "switch", "model": "2960-24TT", "x": 200, "y": 280},
                    {"id": "SW2", "type": "switch", "model": "2960-24TT", "x": 700, "y": 280},
                    {"id": "PC1", "type": "pc", "model": "PC-PT", "x": 120, "y": 450},
                    {"id": "PC2", "type": "pc", "model": "PC-PT", "x": 280, "y": 450},
                    {"id": "PC3", "type": "pc", "model": "PC-PT", "x": 700, "y": 450}
                ],
                "links": [
                    {"a": "R1", "a_port": "GigabitEthernet0/1", "b": "R2", "b_port": "GigabitEthernet0/0", "cable": "cross"},
                    {"a": "R2", "a_port": "GigabitEthernet0/1", "b": "R3", "b_port": "GigabitEthernet0/0", "cable": "cross"},
                    {"a": "R1", "a_port": "GigabitEthernet0/0", "b": "SW1", "b_port": "GigabitEthernet0/1", "cable": "straight"},
                    {"a": "R3", "a_port": "GigabitEthernet0/1", "b": "SW2", "b_port": "GigabitEthernet0/1", "cable": "straight"},
                    {"a": "SW1", "a_port": "FastEthernet0/1", "b": "PC1", "b_port": "FastEthernet0", "cable": "straight"},
                    {"a": "SW1", "a_port": "FastEthernet0/2", "b": "PC2", "b_port": "FastEthernet0", "cable": "straight"},
                    {"a": "SW2", "a_port": "FastEthernet0/1", "b": "PC3", "b_port": "FastEthernet0", "cable": "straight"}
                ],
                "vlans": [
                    {"id": 10, "name": "MANAGEMENT"},
                    {"id": 20, "name": "STAFF"}
                ],
                "ip_plan": [
                    {"device": "R1", "interface": "GigabitEthernet0/1", "ip": "10.0.12.1", "mask": "255.255.255.252", "gateway": None},
                    {"device": "R2", "interface": "GigabitEthernet0/0", "ip": "10.0.12.2", "mask": "255.255.255.252", "gateway": None},
                    {"device": "R2", "interface": "GigabitEthernet0/1", "ip": "10.0.23.1", "mask": "255.255.255.252", "gateway": None},
                    {"device": "R3", "interface": "GigabitEthernet0/0", "ip": "10.0.23.2", "mask": "255.255.255.252", "gateway": None},
                    {"device": "R1", "interface": "GigabitEthernet0/0.10", "ip": "192.168.10.1", "mask": "255.255.255.0", "gateway": None},
                    {"device": "R1", "interface": "GigabitEthernet0/0.20", "ip": "192.168.20.1", "mask": "255.255.255.0", "gateway": None},
                    {"device": "R3", "interface": "GigabitEthernet0/1", "ip": "192.168.30.1", "mask": "255.255.255.0", "gateway": None},
                    {"device": "PC1", "interface": "FastEthernet0", "ip": "192.168.10.10", "mask": "255.255.255.0", "gateway": "192.168.10.1"},
                    {"device": "PC2", "interface": "FastEthernet0", "ip": "192.168.20.10", "mask": "255.255.255.0", "gateway": "192.168.20.1"},
                    {"device": "PC3", "interface": "FastEthernet0", "ip": "192.168.30.10", "mask": "255.255.255.0", "gateway": "192.168.30.1"}
                ],
                "routing": {"protocol": "ospf", "process_id": 1, "area": 0},
                "services": {
                    "dhcp": [
                        {"pool_name": "MGMT_POOL", "network": "192.168.10.0", "mask": "255.255.255.0", "default_router": "192.168.10.1", "dns_server": "1.1.1.1"},
                        {"pool_name": "STAFF_POOL", "network": "192.168.20.0", "mask": "255.255.255.0", "default_router": "192.168.20.1", "dns_server": "1.1.1.1"}
                    ],
                    "nat": None,
                    "acls": []
                }
            })

    if any(k in primary_msg for k in ["ping", "gateway", "can't", "cannot", "troubleshoot", "down", "fail"]):
        return (
            "Based on the Cisco troubleshooting methodology:\n\n"
            "1. **Check IP & Subnet Mask**: Verify that the host and default gateway are in the exact same IP subnet.\n"
            "2. **Check Default Gateway Configuration**: Run `ipconfig` on the PC and ensure the Default Gateway matches the connected router interface IP.\n"
            "3. **Check Physical & Data Link Status**: On the switch and router, run `show ip interface brief` to ensure interfaces are `Status: up, Protocol: up`.\n"
            "4. **VLAN & Access Port Assignment**: Ensure the switch port connecting the PC belongs to the correct VLAN (`show mac address-table`, `show vlan brief`).\n"
            "5. **Trunking**: If router-on-a-stick is used, verify 802.1Q encapsulation matches the subinterface VLAN number on the router."
        )

    return (
        "I am TopoGemma, your local Cisco Packet Tracer AI assistant. "
        "You can ask me to design topologies (e.g., 'Build a network with 3 routers and OSPF') "
        "or ask CCNA networking and troubleshooting questions."
    )
