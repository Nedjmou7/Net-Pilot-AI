import ipaddress
import re
from typing import Dict, List, Set, Tuple
from app.models import Topology, ValidationResult

VALID_PORTS = {
    "2911": [
        "GigabitEthernet0/0", "GigabitEthernet0/1", "GigabitEthernet0/2",
        "Serial0/0/0", "Serial0/0/1", "Serial0/1/0", "Serial0/1/1"
    ],
    "1941": [
        "GigabitEthernet0/0", "GigabitEthernet0/1",
        "Serial0/0/0", "Serial0/0/1"
    ],
    "2811": [
        "FastEthernet0/0", "FastEthernet0/1",
        "Serial0/0/0", "Serial0/0/1", "Serial0/1/0", "Serial0/1/1"
    ],
    "2960-24TT": [
        *[f"FastEthernet0/{i}" for i in range(1, 25)],
        "GigabitEthernet0/1", "GigabitEthernet0/2"
    ],
    "3560-24PS": [
        *[f"FastEthernet0/{i}" for i in range(1, 25)],
        "GigabitEthernet0/1", "GigabitEthernet0/2"
    ],
    "PC-PT": ["FastEthernet0"],
    "Server-PT": ["FastEthernet0"]
}

def normalize_port(port: str) -> str:
    """Normalize common port abbreviations to full Cisco port names."""
    p = port.strip()
    if re.match(r"^Gi?\s*(\d.*)$", p, re.IGNORECASE):
        m = re.match(r"^Gi?\s*(\d.*)$", p, re.IGNORECASE)
        return f"GigabitEthernet{m.group(1)}"
    if re.match(r"^Fa?\s*(\d.*)$", p, re.IGNORECASE):
        m = re.match(r"^Fa?\s*(\d.*)$", p, re.IGNORECASE)
        return f"FastEthernet{m.group(1)}"
    if re.match(r"^Se?\s*(\d.*)$", p, re.IGNORECASE):
        m = re.match(r"^Se?\s*(\d.*)$", p, re.IGNORECASE)
        return f"Serial{m.group(1)}"
    return p

def get_base_port(port: str) -> str:
    """Extract physical port name from subinterface (e.g. Gi0/0.10 -> Gi0/0)."""
    return port.split(".")[0]

def validate_topology(topology: Topology) -> ValidationResult:
    errors: List[str] = []
    warnings: List[str] = []

    # 1. Device validation
    device_map: Dict[str, dict] = {}
    seen_device_ids: Set[str] = set()

    if not topology.devices:
        errors.append("Topology contains no devices.")
        return ValidationResult(errors=errors, warnings=warnings, is_valid=False)

    for dev in topology.devices:
        dev_id = dev.id.strip()
        if not dev_id:
            errors.append("Found a device with an empty ID.")
            continue
        if dev_id in seen_device_ids:
            errors.append(f"Duplicate device ID found: '{dev_id}'. Device IDs must be unique.")
        seen_device_ids.add(dev_id)
        device_map[dev_id] = {
            "type": dev.type,
            "model": dev.model,
            "allowed_ports": VALID_PORTS.get(dev.model, None)
        }
        if dev.model not in VALID_PORTS:
            warnings.append(f"Device '{dev_id}' uses unverified model '{dev.model}'.")

    # 2. Link validation
    used_ports: Dict[Tuple[str, str], int] = {}

    for idx, link in enumerate(topology.links):
        dev_a = link.a.strip()
        dev_b = link.b.strip()
        port_a = normalize_port(link.a_port)
        port_b = normalize_port(link.b_port)

        if dev_a not in device_map:
            errors.append(f"Link #{idx+1} references non-existent device '{dev_a}'.")
        if dev_b not in device_map:
            errors.append(f"Link #{idx+1} references non-existent device '{dev_b}'.")

        if dev_a == dev_b:
            errors.append(f"Device '{dev_a}' cannot be linked to itself.")

        # Check port validity on device A
        if dev_a in device_map:
            allowed_a = device_map[dev_a]["allowed_ports"]
            if allowed_a and port_a not in allowed_a:
                errors.append(f"Port '{port_a}' is invalid for model '{device_map[dev_a]['model']}' on device '{dev_a}'.")
            key_a = (dev_a, port_a)
            if key_a in used_ports:
                errors.append(f"Port '{port_a}' on device '{dev_a}' is already used by another link.")
            used_ports[key_a] = idx

        # Check port validity on device B
        if dev_b in device_map:
            allowed_b = device_map[dev_b]["allowed_ports"]
            if allowed_b and port_b not in allowed_b:
                errors.append(f"Port '{port_b}' is invalid for model '{device_map[dev_b]['model']}' on device '{dev_b}'.")
            key_b = (dev_b, port_b)
            if key_b in used_ports:
                errors.append(f"Port '{port_b}' on device '{dev_b}' is already used by another link.")
            used_ports[key_b] = idx

    # 3. VLAN validation
    vlan_ids = set()
    vlan_names = set()
    for v in topology.vlans:
        if v.id in vlan_ids:
            errors.append(f"Duplicate VLAN ID '{v.id}'.")
        vlan_ids.add(v.id)
        if v.name in vlan_names:
            warnings.append(f"Multiple VLANs share the name '{v.name}'.")
        vlan_names.add(v.name)

    # 4. IP Plan validation
    ip_records = []
    seen_ips: Dict[str, str] = {}
    assigned_subnets: List[Tuple[ipaddress.IPv4Network, str, str]] = []
    router_interface_ips: Dict[str, Dict[str, ipaddress.IPv4Interface]] = {}

    for plan in topology.ip_plan:
        dev_id = plan.device.strip()
        port = normalize_port(plan.interface)
        base_p = get_base_port(port)

        if dev_id not in device_map:
            errors.append(f"IP Plan references non-existent device '{dev_id}'.")
            continue

        # Check subinterface VLAN reference
        if "." in port:
            try:
                sub_id = int(port.split(".")[1])
                if vlan_ids and sub_id not in vlan_ids:
                    warnings.append(f"Subinterface '{port}' on '{dev_id}' uses tag {sub_id} which is not declared in topology.vlans.")
            except ValueError:
                pass

        # Validate IP and mask
        try:
            iface = ipaddress.IPv4Interface(f"{plan.ip.strip()}/{plan.mask.strip()}")
            ip_obj = iface.ip
            net_obj = iface.network
        except Exception as e:
            errors.append(f"Invalid IP/mask '{plan.ip}/{plan.mask}' on device '{dev_id}' port '{port}': {str(e)}")
            continue

        # Check duplicate IP
        ip_str = str(ip_obj)
        if ip_str in seen_ips:
            errors.append(f"Duplicate IP address '{ip_str}' on '{dev_id}' ({port}); already assigned to '{seen_ips[ip_str]}'.")
        else:
            seen_ips[ip_str] = f"{dev_id}:{port}"

        # Record for router/gateway check
        if device_map[dev_id]["type"] in ["router", "switch"]:
            if dev_id not in router_interface_ips:
                router_interface_ips[dev_id] = {}
            router_interface_ips[dev_id][port] = iface

        ip_records.append({
            "device": dev_id,
            "port": port,
            "ip": ip_obj,
            "network": net_obj,
            "gateway": plan.gateway.strip() if plan.gateway else None
        })
        assigned_subnets.append((net_obj, dev_id, port))

    # Gateway and Subnet validation for PCs and Servers
    for rec in ip_records:
        dev_type = device_map[rec["device"]]["type"]
        if dev_type in ["pc", "server"]:
            gw = rec["gateway"]
            if not gw:
                warnings.append(f"{dev_type.upper()} '{rec['device']}' has no default gateway configured.")
            else:
                try:
                    gw_ip = ipaddress.IPv4Address(gw)
                    if gw_ip not in rec["network"]:
                        errors.append(
                            f"Gateway '{gw}' for '{rec['device']}' is not in the same subnet "
                            f"({rec['network']}) as its IP '{rec['ip']}'."
                        )
                    # Verify gateway exists on some router/switch interface
                    gw_found = any(
                        gw_ip == iface.ip
                        for r_dev in router_interface_ips.values()
                        for iface in r_dev.values()
                    )
                    if not gw_found:
                        warnings.append(f"Gateway '{gw}' for '{rec['device']}' does not match any configured router IP.")
                except Exception as e:
                    errors.append(f"Invalid default gateway '{gw}' on '{rec['device']}': {str(e)}")

    # 5. Routing coverage check
    if topology.routing.protocol in ["ospf", "rip", "eigrp"]:
        for dev_id, r_ports in router_interface_ips.items():
            if device_map[dev_id]["type"] == "router" and not r_ports:
                warnings.append(f"Router '{dev_id}' has no IP interfaces configured for routing protocol {topology.routing.protocol.upper()}.")

    # 6. Check DHCP configuration consistency
    for dhcp in topology.services.dhcp:
        try:
            dhcp_net = ipaddress.IPv4Network(f"{dhcp.network.strip()}/{dhcp.mask.strip()}", strict=False)
            if dhcp.default_router:
                gw_ip = ipaddress.IPv4Address(dhcp.default_router.strip())
                if gw_ip not in dhcp_net:
                    errors.append(f"DHCP pool '{dhcp.pool_name}' default-router '{dhcp.default_router}' is not in network '{dhcp_net}'.")
        except Exception as e:
            errors.append(f"Invalid DHCP network/mask for pool '{dhcp.pool_name}': {str(e)}")

    return ValidationResult(
        errors=errors,
        warnings=warnings,
        is_valid=(len(errors) == 0)
    )
