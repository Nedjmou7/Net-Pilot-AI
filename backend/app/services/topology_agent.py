import os
import json
import time
import re
import logging
from typing import Tuple, Optional, Dict, Any
from app.models import Topology, ValidationResult
from app.services.ollama_client import ollama_client
from app.services.validator import validate_topology
from app.repository import save_llm_log

logger = logging.getLogger("topogemma.topology_agent")

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
PROMPTS_DIR = os.path.join(ROOT_DIR, "prompts")

def load_system_prompt() -> str:
    path = os.path.join(PROMPTS_DIR, "system_build.md")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return "You are TopoGemma, a Cisco network assistant. Output valid topology JSON only."

def load_examples() -> list:
    path = os.path.join(PROMPTS_DIR, "examples.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []

def extract_json_object(text: str) -> Optional[dict]:
    """Robustly extract and parse a JSON object from raw LLM text."""
    text = text.strip()
    # Strip markdown code blocks if present
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    # Try direct parse
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    # Try regex finding outer braces { ... }
    match = re.search(r"(\{.*\})", text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(1))
            if isinstance(data, dict):
                return data
        except Exception:
            pass

    return None

def get_fallback_topology(user_message: str) -> Topology:
    """Deterministic fallback if Ollama model is offline or download in progress."""
    msg = user_message.lower()
    examples = load_examples()
    if "ospf" in msg or "3 router" in msg or "router" in msg:
        for ex in examples:
            if "ospf" in ex.get("user", "").lower():
                return Topology.model_validate(ex["assistant"])
    if "vlan" in msg:
        for ex in examples:
            if "vlan" in ex.get("user", "").lower():
                return Topology.model_validate(ex["assistant"])
    if examples:
        return Topology.model_validate(examples[-1]["assistant"])

    # Default 2-router fallback
    return Topology(
        name="demo-fallback",
        devices=[
            {"id": "R1", "type": "router", "model": "2911", "x": 250, "y": 150},
            {"id": "SW1", "type": "switch", "model": "2960-24TT", "x": 250, "y": 300},
            {"id": "PC1", "type": "pc", "model": "PC-PT", "x": 250, "y": 450}
        ],
        links=[
            {"a": "R1", "a_port": "GigabitEthernet0/0", "b": "SW1", "b_port": "GigabitEthernet0/1", "cable": "straight"},
            {"a": "SW1", "a_port": "FastEthernet0/1", "b": "PC1", "b_port": "FastEthernet0", "cable": "straight"}
        ],
        ip_plan=[
            {"device": "R1", "interface": "GigabitEthernet0/0", "ip": "192.168.1.1", "mask": "255.255.255.0"},
            {"device": "PC1", "interface": "FastEthernet0", "ip": "192.168.1.50", "mask": "255.255.255.0", "gateway": "192.168.1.1"}
        ]
    )

async def build_topology(user_message: str) -> Tuple[Topology, ValidationResult]:
    """Generates a topology from user prompt, with up to 3 validation retries."""
    system_prompt = load_system_prompt()
    examples = load_examples()

    messages = [{"role": "system", "content": system_prompt}]
    for ex in examples[:3]:  # Top 3 few-shots
        messages.append({"role": "user", "content": ex["user"]})
        messages.append({"role": "assistant", "content": json.dumps(ex["assistant"])})

    messages.append({"role": "user", "content": user_message})

    max_retries = 3
    last_error = ""

    for attempt in range(max_retries):
        t0 = time.time()
        try:
            res = await ollama_client.chat(messages=messages, format_json=True, temperature=0.2)
            latency_ms = int((time.time() - t0) * 1000)
            raw_reply = res.get("message", {}).get("content", "").strip()

            parsed_dict = extract_json_object(raw_reply)
            if not parsed_dict:
                last_error = f"Model did not output valid JSON. Raw output: {raw_reply[:150]}"
                save_llm_log(
                    prompt=json.dumps(messages),
                    response=raw_reply,
                    model=ollama_client.model,
                    latency_ms=latency_ms,
                    valid_json=False
                )
                messages.append({"role": "assistant", "content": raw_reply})
                messages.append({
                    "role": "user",
                    "content": f"Your output was not valid JSON. Error: {last_error}. Please output ONLY a valid JSON object starting with {{ and ending with }}."
                })
                continue

            # Validate against Pydantic model
            try:
                topo = Topology.model_validate(parsed_dict)
            except Exception as pe:
                last_error = f"Schema validation error: {str(pe)}"
                save_llm_log(
                    prompt=json.dumps(messages),
                    response=raw_reply,
                    model=ollama_client.model,
                    latency_ms=latency_ms,
                    valid_json=False
                )
                messages.append({"role": "assistant", "content": raw_reply})
                messages.append({
                    "role": "user",
                    "content": f"The topology does not match the schema: {last_error}. Fix all fields and return valid JSON only."
                })
                continue

            # Validate with pure-Python validator
            val_result = validate_topology(topo)
            save_llm_log(
                prompt=json.dumps(messages),
                response=raw_reply,
                model=ollama_client.model,
                latency_ms=latency_ms,
                valid_json=val_result.is_valid
            )

            if val_result.is_valid:
                return topo, val_result

            # If validator found errors, retry with error message
            last_error = "; ".join(val_result.errors)
            messages.append({"role": "assistant", "content": raw_reply})
            messages.append({
                "role": "user",
                "content": f"The topology has networking validation errors: {last_error}. Fix these issues and return ONLY the corrected JSON object."
            })

        except Exception as e:
            logger.warning(f"Ollama call failed or model unavailable on attempt {attempt+1}: {e}")
            break

    # If all attempts failed or Ollama was unreachable, use high-quality deterministic fallback
    logger.info("Using deterministic fallback topology")
    fallback = get_fallback_topology(user_message)
    val = validate_topology(fallback)
    if last_error:
        val.warnings.append(f"Offline generator used fallback due to: {last_error}")
    return fallback, val
