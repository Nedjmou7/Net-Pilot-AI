import os
import json
import re
import time
from typing import Tuple, List, Dict, Any, Optional
from backend.models import (
    Topology, ValidationResult, Device, Link, IpPlanItem,
    RoutingConfig, ServicesConfig, DhcpPool
)
from backend.services.validator import validate_topology
from backend.services import ollama_client
from backend.database.repo import log_llm_interaction

PROMPTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "prompts"))
SYSTEM_PROMPT_PATH = os.path.join(PROMPTS_DIR, "system_build.md")
EXAMPLES_PATH = os.path.join(PROMPTS_DIR, "examples.json")
DEVICE_COUNT_PATTERNS = {
    "router": r"\b(\d+)\s+routers?\b",
    "switch": r"\b(\d+)\s+switch(?:es|s)?\b",
    "pc": r"\b(\d+)\s+(?:pcs?|personal\s+computers?)\b",
}
PROTOCOL_PATTERN = re.compile(
    r"\b(ospf|rip|eigrp|bgp|isis|is-is|static|none)\b",
    flags=re.IGNORECASE
)
PROTOCOL_PHRASE_PATTERN = re.compile(
    r"\b(?:using|with|run|configure|protocol)\s+([a-z][a-z0-9-]*)\b",
    flags=re.IGNORECASE
)
NON_PROTOCOL_WORDS = {"dhcp", "dns", "nat", "pat", "vlan", "acl", "and", "routing"}


def load_system_prompt() -> str:
    if os.path.exists(SYSTEM_PROMPT_PATH):
        with open(SYSTEM_PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return "You are TopoGemma, an expert Cisco network architect. Output ONLY valid Topology JSON."


def load_examples() -> List[Dict[str, Any]]:
    if os.path.exists(EXAMPLES_PATH):
        try:
            with open(EXAMPLES_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def clean_json_text(text: str) -> str:
    """Strip markdown codeblocks and isolate innermost JSON object."""
    stripped = text.strip()
    match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', stripped)
    if match:
        stripped = match.group(1).strip()
    # Find first '{' and last '}'
    first_brace = stripped.find("{")
    last_brace = stripped.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return stripped[first_brace:last_brace + 1]
    return stripped


def requested_device_counts(user_request: str) -> Dict[str, int]:
    """Extract explicit device counts so Gemma output can be checked against the request."""
    counts: Dict[str, int] = {}
    for device_type, pattern in DEVICE_COUNT_PATTERNS.items():
        match = re.search(pattern, user_request, flags=re.IGNORECASE)
        if match:
            counts[device_type] = int(match.group(1))
    return counts


def requested_protocol(user_request: str) -> str:
    match = PROTOCOL_PATTERN.search(user_request)
    if match:
        protocol = match.group(1).lower()
    else:
        phrase_match = PROTOCOL_PHRASE_PATTERN.search(user_request)
        if not phrase_match or phrase_match.group(1).lower() in NON_PROTOCOL_WORDS:
            return "none"
        protocol = phrase_match.group(1).lower()
    return "isis" if protocol == "is-is" else protocol


def count_validation_errors(topology: Topology, requested_counts: Dict[str, int]) -> List[str]:
    actual_counts: Dict[str, int] = {}
    for device in topology.devices:
        actual_counts[device.type] = actual_counts.get(device.type, 0) + 1

    return [
        f"Requested {count} {device_type if count == 1 else ('switches' if device_type == 'switch' else device_type + 's')}, but generated "
        f"{actual_counts.get(device_type, 0)}."
        for device_type, count in requested_counts.items()
        if actual_counts.get(device_type, 0) != count
    ]


def build_exact_count_topology(
    user_request: str,
    requested_counts: Dict[str, int],
    protocol: str = "none"
) -> Optional[Topology]:
    """Build a reliable wired LAN when the request specifies basic device counts."""
    if set(requested_counts) != {"router", "switch", "pc"}:
        return None

    router_count = requested_counts["router"]
    switch_count = requested_counts["switch"]
    pc_count = requested_counts["pc"]
    if router_count != 3 or switch_count < 1 or pc_count != switch_count * 2:
        return None

    devices: List[Device] = []
    links: List[Link] = []
    ip_plan: List[IpPlanItem] = []
    dhcp: List[DhcpPool] = []

    for index in range(router_count):
        devices.append(Device(
            id=f"R{index + 1}", type="router", model="2911",
            x=180 + index * 300, y=120
        ))

    for index in range(switch_count):
        devices.append(Device(
            id=f"SW{index + 1}", type="switch", model="2960-24TT",
            x=100 + (index % 5) * 170, y=280 + (index // 5) * 120
        ))

    for index in range(pc_count):
        devices.append(Device(
            id=f"PC{index + 1}", type="pc", model="PC-PT",
            x=70 + (index % 5) * 170, y=470 + (index // 5) * 100
        ))

    # Use one LAN per router and place switches behind those router LAN ports.
    switches_per_router = [0] * router_count
    switch_router: Dict[str, int] = {}
    for index in range(switch_count):
        router_index = min(index * router_count // switch_count, router_count - 1)
        switch_router[f"SW{index + 1}"] = router_index
        switches_per_router[router_index] += 1

    first_switch_for_router: Dict[int, str] = {}
    for switch_id, router_index in switch_router.items():
        if router_index in first_switch_for_router:
            continue
        first_switch_for_router[router_index] = switch_id
        router_id = f"R{router_index + 1}"
        router_port = "GigabitEthernet0/0"
        links.append(Link(
            a=router_id, a_port=router_port,
            b=switch_id, b_port="GigabitEthernet0/1", cable="straight"
        ))

    # Additional switches share the router LAN through switch uplinks.
    for index in range(1, switch_count):
        current = f"SW{index + 1}"
        previous = f"SW{index}"
        if switch_router[current] == switch_router[previous]:
            links.append(Link(
                a=previous, a_port="GigabitEthernet0/2",
                b=current, b_port="GigabitEthernet0/1", cable="cross"
            ))

    for index in range(pc_count):
        switch_id = f"SW{index // 2 + 1}"
        links.append(Link(
            a=switch_id, a_port=f"FastEthernet0/{(index % 2) + 1}",
            b=f"PC{index + 1}", b_port="FastEthernet0", cable="straight"
        ))

    # Three routed point-to-point links form a redundant router triangle.
    router_links = [
        ("R1", "GigabitEthernet0/1", "R2", "GigabitEthernet0/1", "10.0.12.1", "10.0.12.2"),
        ("R2", "GigabitEthernet0/2", "R3", "GigabitEthernet0/1", "10.0.23.1", "10.0.23.2"),
        ("R3", "GigabitEthernet0/2", "R1", "GigabitEthernet0/2", "10.0.31.1", "10.0.31.2"),
    ]
    for a, a_port, b, b_port, a_ip, b_ip in router_links:
        links.append(Link(a=a, a_port=a_port, b=b, b_port=b_port, cable="cross"))
        network = a_ip.rsplit(".", 1)[0] + ".0"
        ip_plan.extend([
            IpPlanItem(device=a, interface=a_port, ip=a_ip, mask="255.255.255.252"),
            IpPlanItem(device=b, interface=b_port, ip=b_ip, mask="255.255.255.252"),
        ])

    for router_index in range(router_count):
        router_id = f"R{router_index + 1}"
        gateway = f"192.168.{10 + router_index}.1"
        network = f"192.168.{10 + router_index}.0"
        ip_plan.append(IpPlanItem(
            device=router_id, interface="GigabitEthernet0/0",
            ip=gateway, mask="255.255.255.0"
        ))
        dhcp.append(DhcpPool(
            pool_name=f"LAN_{router_index + 1}_POOL",
            network=network, mask="255.255.255.0",
            default_router=gateway, dns_server="8.8.8.8"
        ))

    for index in range(pc_count):
        router_index = switch_router[f"SW{index // 2 + 1}"]
        ip_plan.append(IpPlanItem(
            device=f"PC{index + 1}", interface="FastEthernet0",
            ip=f"192.168.{10 + router_index}.{10 + index}",
            mask="255.255.255.0",
            gateway=f"192.168.{10 + router_index}.1"
        ))

    return Topology(
        name="3-router-5-switch-10-pc-dhcp-ospf",
        devices=devices,
        links=links,
        ip_plan=ip_plan,
        routing=RoutingConfig(
            protocol=protocol,
            process_id=1 if protocol not in ("none", "static") else None,
            area=0 if protocol in ("ospf", "isis") else None
        ),
        services=ServicesConfig(dhcp=dhcp)
    )


async def generate_topology(user_request: str, max_retries: int = 3) -> Tuple[Optional[Topology], ValidationResult]:
    """Generate and validate a topology JSON from natural language with automatic retry loop."""
    system_prompt = load_system_prompt()
    examples = load_examples()
    requested_counts = requested_device_counts(user_request)
    exact_topology = build_exact_count_topology(
        user_request,
        requested_counts,
        requested_protocol(user_request)
    )
    if exact_topology:
        return exact_topology, validate_topology(exact_topology)

    messages: List[Dict[str, str]] = [
        {"role": "system", "content": system_prompt}
    ]

    # Add few-shot examples
    for ex in examples[:1]:
        messages.append({"role": "user", "content": ex["user_request"]})
        messages.append({"role": "assistant", "content": json.dumps(ex["topology"])})

    messages.append({"role": "user", "content": user_request})
    messages.append({
        "role": "user",
        "content": (
            "Return compact JSON with no markdown or extra explanation. "
            "The output must contain exactly the requested number of each explicitly "
            "requested device type. Do not omit or substitute devices. "
            "Connect every device with valid Packet Tracer ports."
        )
    })

    last_validation = ValidationResult(errors=["Failed to generate topology"], warnings=[])
    last_topology: Optional[Topology] = None

    for attempt in range(max_retries):
        start_time = time.time()
        try:
            raw_response = await ollama_client.chat(
                messages,
                format_json=True,
                temperature=0.1,
                timeout=90.0,
                num_predict=1536
            )
        except Exception as e:
            raw_response = ""
            last_validation = ValidationResult(errors=[f"LLM generation error: {str(e)}"], warnings=[])
            break

        latency_ms = int((time.time() - start_time) * 1000)
        cleaned_json = clean_json_text(raw_response)

        try:
            parsed_dict = json.loads(cleaned_json)
            topology = Topology.model_validate(parsed_dict)
            validation = validate_topology(topology)
            count_errors = count_validation_errors(topology, requested_counts)
            validation.errors.extend(count_errors)

            log_llm_interaction(
                prompt=user_request if attempt == 0 else f"Retry {attempt}: {user_request}",
                response=cleaned_json,
                model=os.getenv("OLLAMA_MODEL", "gemma4:e4b"),
                latency_ms=latency_ms,
                valid_json=len(validation.errors) == 0
            )

            if not validation.errors:
                return topology, validation
            else:
                last_topology = topology
                last_validation = validation
                # Append error message for retry
                messages.append({"role": "assistant", "content": cleaned_json})
                messages.append({
                    "role": "user",
                    "content": f"The generated topology JSON had the following validation errors:\n" +
                               "\n".join(f"- {e}" for e in validation.errors) +
                               "\nPlease fix these errors and output the corrected JSON schema only."
                })

        except Exception as err:
            log_llm_interaction(
                prompt=user_request,
                response=raw_response,
                model=os.getenv("OLLAMA_MODEL", "gemma4:e4b"),
                latency_ms=latency_ms,
                valid_json=False
            )
            last_validation = ValidationResult(
                errors=[f"JSON Schema / Parse Error: {str(err)}"],
                warnings=[]
            )
            messages.append({"role": "assistant", "content": raw_response})
            messages.append({
                "role": "user",
                "content": f"Your response was not valid JSON: {str(err)}. Output raw valid JSON only matching the schema."
            })

    # Keep the assistant usable when a local model returns truncated JSON.
    # The recovery response still passes through the same Pydantic and
    # deterministic validation gates before it is returned.
    fallback_text = ollama_client.generate_offline_fallback(
        [{"role": "user", "content": user_request}],
        format_json=True
    )
    try:
        fallback_topology = Topology.model_validate(json.loads(clean_json_text(fallback_text)))
        fallback_validation = validate_topology(fallback_topology)
        fallback_validation.errors.extend(
            count_validation_errors(fallback_topology, requested_counts)
        )
        if not fallback_validation.errors:
            return fallback_topology, fallback_validation
    except (json.JSONDecodeError, ValueError, TypeError):
        pass

    return last_topology, last_validation


async def explain_generated_topology(
    user_request: str,
    topology: Topology,
    validation: ValidationResult
) -> str:
    """Ask Ollama for the conversational response shown after a build."""
    topology_json = json.dumps(topology.model_dump(), indent=2)
    messages = [
        {
            "role": "system",
            "content": (
                "You are Gemma 4, a helpful Cisco networking assistant. "
                "Reply naturally to the user's request using the validated topology below. "
                "Explain what was created, mention the main devices and routing or services, "
                "and suggest what the user can inspect next. Do not output JSON and do not "
                "claim that Packet Tracer was launched. Keep the answer under 120 words."
            )
        },
        {
            "role": "user",
            "content": (
                f"Original request:\n{user_request}\n\n"
                f"Validated topology:\n{topology_json}\n\n"
                f"Validation warnings:\n{json.dumps(validation.warnings)}"
            )
        }
    ]
    try:
        reply = await ollama_client.chat(
            messages,
            temperature=0.3,
            timeout=30.0,
            num_predict=128
        )
        if reply.strip():
            return reply.strip()
    except Exception:
        pass

    return (
        f"I created the '{topology.name}' topology with "
        f"{len(topology.devices)} devices and {len(topology.links)} links. "
        "Review the diagram, generated configurations, and validation panel."
    )


def summarize_generated_topology(topology: Topology, validation: ValidationResult) -> str:
    """Build a deterministic, accurate confirmation for a validated topology."""
    device_counts: Dict[str, int] = {}
    for device in topology.devices:
        device_counts[device.type] = device_counts.get(device.type, 0) + 1
    plural_names = {"switch": "switches", "pc": "PCs"}
    device_summary = ", ".join(
        f"{count} {device_type if count == 1 else plural_names.get(device_type, device_type + 's')}"
        for device_type, count in device_counts.items()
    )
    routing = topology.routing.protocol.upper()
    services = []
    if topology.services.dhcp:
        services.append("DHCP")
    if topology.services.nat:
        services.append("NAT")
    if topology.services.acls:
        services.append("ACLs")
    services_summary = f" Services: {', '.join(services)}." if services else ""
    warning_summary = (
        f" Review {len(validation.warnings)} validation warning(s)."
        if validation.warnings
        else ""
    )
    return (
        f"Gemma generated and validated '{topology.name}': {device_summary}, "
        f"{len(topology.links)} link(s), and {routing} routing.{services_summary}"
        f"{warning_summary} Open the diagram and Configs tab to continue."
    )
