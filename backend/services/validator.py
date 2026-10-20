import ipaddress
import re
from typing import Dict, List, Set, Any
from backend.models import Topology, ValidationResult

# Allowed port patterns per known model
ALLOWED_PORTS: Dict[str, List[str]] = {
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
        "Serial0/0/0", "Serial0/0/1"
    ],
    "2960-24TT": [
        *[f"FastEthernet0/{i}" for i in range(1, 25)],
        "GigabitEthernet0/1", "GigabitEthernet0/2"
    ],
    "3650-24PS": [
        *[f"GigabitEthernet1/0/{i}" for i in range(1, 25)],
        *[f"GigabitEthernet1/1/{i}" for i in range(1, 5)]
    ],
    "PC-PT": ["FastEthernet0"],
    "Server-PT": ["FastEthernet0", "GigabitEthernet0"],
    "Laptop-PT": ["FastEthernet0"]
}


def normalize_port_name(port: str) -> str:
    """Normalize common port abbreviations to canonical Cisco names."""
    p = port.strip()
    p = re.sub(r'^(?:GigabitEthernet|GigEth|GigE|Gig|Gi|G)(\d.*)$', r'GigabitEthernet\1', p, flags=re.IGNORECASE)
    p = re.sub(r'^(?:FastEthernet|FastEth|Fa|FE|F)(\d.*)$', r'FastEthernet\1', p, flags=re.IGNORECASE)
    p = re.sub(r'^(?:Serial|Se|S)(\d.*)$', r'Serial\1', p, flags=re.IGNORECASE)
    return p


def validate_topology(topology: Topology) -> ValidationResult:
    errors: List[str] = []
    warnings: List[str] = []

    # 1. Device checks
    device_map: Dict[str, Any] = {}
    seen_ids: Set[str] = set()

    if not topology.devices:
        errors.append("Topology contains no devices.")
        return ValidationResult(errors=errors, warnings=warnings)

    for dev in topology.devices:
        dev_id = dev.id.strip()
        if not dev_id:
            errors.append("Found device with empty or whitespace ID.")
            continue
        if dev_id in seen_ids:
            errors.append(f"Duplicate device ID found: '{dev_id}'. Device IDs must be unique.")
        seen_ids.add(dev_id)
        device_map[dev_id] = dev

    # 2. Link & Port checks
    used_ports: Dict[str, Set[str]] = {d_id: set() for d_id in device_map}

    for idx, link in enumerate(topology.links):
        a_id = link.a.strip()
        b_id = link.b.strip()
        a_port = normalize_port_name(link.a_port)
        b_port = normalize_port_name(link.b_port)

        # Check endpoints exist
        if a_id not in device_map:
            errors.append(f"Link #{idx + 1} references non-existent device '{a_id}'.")
            continue
        if b_id not in device_map:
            errors.append(f"Link #{idx + 1} references non-existent device '{b_id}'.")
            continue
        if a_id == b_id:
            errors.append(f"Link #{idx + 1} connects device '{a_id}' to itself on ports '{a_port}' and '{b_port}'.")
            continue

        dev_a = device_map[a_id]
        dev_b = device_map[b_id]

        # Check valid port for model A
        allowed_a = ALLOWED_PORTS.get(dev_a.model)
        if allowed_a and a_port not in allowed_a:
            errors.append(f"Invalid port '{a_port}' for device '{a_id}' (model {dev_a.model}). Allowed: {', '.join(allowed_a[:6])}...")

        # Check valid port for model B
        allowed_b = ALLOWED_PORTS.get(dev_b.model)
        if allowed_b and b_port not in allowed_b:
            errors.append(f"Invalid port '{b_port}' for device '{b_id}' (model {dev_b.model}). Allowed: {', '.join(allowed_b[:6])}...")

        # Port reuse check
        if a_port in used_ports[a_id]:
            errors.append(f"Port '{a_port}' on device '{a_id}' is used in multiple links.")
        else:
            used_ports[a_id].add(a_port)

        if b_port in used_ports[b_id]:
            errors.append(f"Port '{b_port}' on device '{b_id}' is used in multiple links.")
        else:
            used_ports[b_id].add(b_port)

        # Cable type sanity check
        if (dev_a.type == "router" and dev_b.type == "router") or (dev_a.type == "switch" and dev_b.type == "switch"):
            if link.cable == "straight":
                warnings.append(f"Link between {dev_a.type} '{a_id}' and {dev_b.type} '{b_id}' typically uses a crossover or serial cable, but 'straight' was specified.")
        elif (dev_a.type in ("pc", "server") and dev_b.type == "switch") or (dev_a.type == "router" and dev_b.type == "switch"):
            if link.cable == "cross":
                warnings.append(f"Link between '{a_id}' and '{b_id}' usually uses a straight-through cable.")

    # 3. VLAN checks
    vlan_ids: Set[int] = set()
    for vlan in topology.vlans:
        if vlan.id in vlan_ids:
            errors.append(f"Duplicate VLAN ID found: {vlan.id}. VLAN IDs must be unique.")
        vlan_ids.add(vlan.id)

    # 4. IP Plan checks
    assigned_ips: Dict[str, str] = {}
    assigned_interfaces: Set[tuple[str, str]] = set()
    planned_networks: List[tuple[ipaddress.IPv4Network, str]] = []
    subnet_map: Dict[str, List[Dict[str, Any]]] = {}

    for item in topology.ip_plan:
        dev_id = item.device.strip()
        if dev_id not in device_map:
            errors.append(f"IP plan assigns address to non-existent device '{dev_id}'.")
            continue

        raw_iface = normalize_port_name(item.interface)
        interface_key = (dev_id, raw_iface)
        if interface_key in assigned_interfaces:
            errors.append(f"Interface '{raw_iface}' on device '{dev_id}' has multiple IP plan entries.")
        assigned_interfaces.add(interface_key)

        # Check subinterface / VLAN reference
        if "." in raw_iface:
            base_port, sub_id_str = raw_iface.split(".", 1)
            try:
                sub_vlan = int(sub_id_str)
                if sub_vlan not in vlan_ids:
                    warnings.append(f"Subinterface '{raw_iface}' on '{dev_id}' uses VLAN {sub_vlan}, which is not defined in the 'vlans' list.")
                interface_port = base_port
            except ValueError:
                errors.append(f"Invalid subinterface format '{raw_iface}' on device '{dev_id}'.")
                interface_port = raw_iface
        else:
            interface_port = raw_iface

        # Validate physical IP-plan interfaces against the device model. SVIs are
        # logical interfaces and therefore do not appear in ALLOWED_PORTS.
        allowed_interfaces = ALLOWED_PORTS.get(device_map[dev_id].model)
        if allowed_interfaces and not interface_port.startswith("Vlan") and interface_port not in allowed_interfaces:
            errors.append(
                f"Invalid interface '{raw_iface}' for device '{dev_id}' "
                f"(model {device_map[dev_id].model})."
            )

        # Validate IP and Mask
        try:
            net = ipaddress.IPv4Network(f"{item.ip}/{item.mask}", strict=False)
            addr = ipaddress.IPv4Address(item.ip)

            # Check network/broadcast host address
            if addr == net.network_address and net.prefixlen < 31:
                warnings.append(f"IP '{item.ip}' on '{dev_id}' is the network address of {net}.")
            if addr == net.broadcast_address and net.prefixlen < 31:
                warnings.append(f"IP '{item.ip}' on '{dev_id}' is the broadcast address of {net}.")

            # Duplicate IP check
            if item.ip in assigned_ips:
                errors.append(f"Duplicate IP '{item.ip}' assigned to both '{assigned_ips[item.ip]}' and '{dev_id}'.")
            else:
                assigned_ips[item.ip] = dev_id

            # Group by network
            net_str = str(net)
            if net_str not in subnet_map:
                subnet_map[net_str] = []
            subnet_map[net_str].append({"device": dev_id, "ip": item.ip, "gateway": item.gateway, "interface": raw_iface})
            planned_networks.append((net, f"{dev_id} {raw_iface}"))

            # Gateway check
            if item.gateway:
                try:
                    gw_addr = ipaddress.IPv4Address(item.gateway)
                    if gw_addr not in net:
                        errors.append(f"Gateway '{item.gateway}' for '{dev_id}' ({item.ip}) is outside subnet {net}.")
                except ValueError:
                    errors.append(f"Invalid gateway IP format '{item.gateway}' on '{dev_id}'.")

        except ValueError as e:
            errors.append(f"Invalid IP/mask '{item.ip}/{item.mask}' on device '{dev_id}': {str(e)}")

    # A topology may assign multiple addresses to the same subnet, but distinct
    # subnets must not overlap because that creates ambiguous routing.
    for index, (network, first_owner) in enumerate(planned_networks):
        for other_network, second_owner in planned_networks[index + 1:]:
            if network != other_network and network.overlaps(other_network):
                errors.append(
                    f"Overlapping subnets detected: {network} ({first_owner}) "
                    f"overlaps {other_network} ({second_owner})."
                )

    # Check hosts have gateways pointing to an existing router in that subnet
    for net_str, members in subnet_map.items():
        router_ips = {m["ip"] for m in members if device_map[m["device"]].type == "router"}
        for m in members:
            dev_type = device_map[m["device"]].type
            if dev_type in ("pc", "server"):
                if not m["gateway"]:
                    warnings.append(f"{dev_type.upper()} '{m['device']}' has no default gateway configured.")
                elif router_ips and m["gateway"] not in router_ips:
                    warnings.append(f"Gateway '{m['gateway']}' on '{m['device']}' does not match any configured router interface in subnet {net_str} ({', '.join(router_ips)}).")

    # 5. Routing checks
    routing = topology.routing
    protocol = routing.protocol.strip().lower()
    if protocol not in ("none", "static", "ospf", "rip"):
        warnings.append(
            f"Routing protocol '{routing.protocol}' is not natively generated by the IOS builder; "
            "review the generated protocol instructions before deployment."
        )
    if protocol in ("ospf", "rip"):
        # Ensure there is at least one router
        routers = [d for d in topology.devices if d.type == "router"]
        if not routers:
            warnings.append(f"Routing protocol '{routing.protocol.upper()}' is configured, but no routers exist in topology.")
        if protocol == "ospf":
            if routing.process_id is None:
                warnings.append("OSPF is specified without a process_id (defaulting to 1).")
            if routing.area is None:
                warnings.append("OSPF is specified without an area (defaulting to 0).")

    # 6. Isolated devices check
    connected_devices = {l.a for l in topology.links} | {l.b for l in topology.links}
    for dev in topology.devices:
        if dev.id not in connected_devices and len(topology.devices) > 1:
            warnings.append(f"Device '{dev.id}' is isolated with no links.")

    return ValidationResult(errors=errors, warnings=warnings)
