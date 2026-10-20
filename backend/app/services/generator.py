import os
import ipaddress
from typing import Dict, List, Any
from jinja2 import Environment, FileSystemLoader
from app.models import Topology, GenerateResponse

# Setup Jinja2 environment pointing to backend/templates
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "..", "templates"))
jinja_env = Environment(loader=FileSystemLoader(TEMPLATES_DIR), trim_blocks=True, lstrip_blocks=True)

def subnet_mask_to_wildcard(mask_str: str) -> str:
    """Convert subnet mask (e.g. 255.255.255.0) to wildcard mask (0.0.0.255)."""
    try:
        octets = [int(x) for x in mask_str.strip().split(".")]
        wildcard_octets = [str(255 - o) for o in octets]
        return ".".join(wildcard_octets)
    except Exception:
        return "0.0.0.255"

def generate_artifacts(topology: Topology) -> GenerateResponse:
    device_lookup = {d.id: d for d in topology.devices}
    cli_configs: Dict[str, str] = {}

    # Map links by device
    device_links: Dict[str, List[dict]] = {d.id: [] for d in topology.devices}
    for l in topology.links:
        if l.a in device_links:
            device_links[l.a].append({"local_port": l.a_port, "remote_dev": l.b, "remote_port": l.b_port})
        if l.b in device_links:
            device_links[l.b].append({"local_port": l.b_port, "remote_dev": l.a, "remote_port": l.a_port})

    # Map IP plans by device
    device_ips: Dict[str, List[dict]] = {d.id: [] for d in topology.devices}
    for plan in topology.ip_plan:
        if plan.device in device_ips:
            device_ips[plan.device].append(plan.model_dump())

    # 1. Generate CLI configs for Routers
    router_template = jinja_env.get_template("ios_router.j2")
    for dev in topology.devices:
        if dev.type == "router":
            interfaces = []
            routing_networks = []
            seen_networks = set()

            # Physical and subinterfaces from ip_plan
            plans = device_ips.get(dev.id, [])
            for p in plans:
                port_name = p["interface"]
                is_sub = "." in port_name
                vlan_id = None
                if is_sub:
                    try:
                        vlan_id = int(port_name.split(".")[1])
                    except ValueError:
                        vlan_id = 10

                interfaces.append({
                    "name": port_name,
                    "is_subinterface": is_sub,
                    "vlan_id": vlan_id,
                    "ip": p["ip"],
                    "mask": p["mask"]
                })

                # Calculate network for routing
                try:
                    net = ipaddress.IPv4Network(f"{p['ip']}/{p['mask']}", strict=False)
                    net_str = str(net.network_address)
                    if net_str not in seen_networks:
                        seen_networks.add(net_str)
                        routing_networks.append({
                            "network": net_str,
                            "mask": p["mask"],
                            "wildcard": subnet_mask_to_wildcard(p["mask"])
                        })
                except Exception:
                    pass

            config = router_template.render(
                device=dev,
                interfaces=interfaces,
                routing=topology.routing,
                routing_networks=routing_networks,
                services=topology.services
            )
            cli_configs[dev.id] = config.strip()

    # 2. Generate CLI configs for Switches
    switch_template = jinja_env.get_template("ios_switch.j2")
    for dev in topology.devices:
        if dev.type == "switch":
            ports = []
            links = device_links.get(dev.id, [])
            for link in links:
                remote_dev_id = link["remote_dev"]
                remote_dev = device_lookup.get(remote_dev_id)
                local_port = link["local_port"]

                # If connected to router or another switch -> trunk
                if remote_dev and remote_dev.type in ["router", "switch"]:
                    ports.append({
                        "name": local_port,
                        "mode": "trunk",
                        "vlan_id": None
                    })
                else:
                    # Access port connected to PC or Server
                    # Check if PC has an assigned VLAN via subnets
                    vlan_id = None
                    if topology.vlans:
                        vlan_id = topology.vlans[0].id
                    ports.append({
                        "name": local_port,
                        "mode": "access",
                        "vlan_id": vlan_id
                    })

            # Management SVI if switch has an IP in ip_plan
            management_svi = None
            plans = device_ips.get(dev.id, [])
            if plans:
                first_plan = plans[0]
                management_svi = {
                    "vlan_id": 1,
                    "ip": first_plan["ip"],
                    "mask": first_plan["mask"],
                    "gateway": first_plan.get("gateway")
                }

            config = switch_template.render(
                device=dev,
                vlans=topology.vlans,
                ports=ports,
                management_svi=management_svi
            )
            cli_configs[dev.id] = config.strip()

    # 3. Prepare End Devices info for PTBuilder script
    end_devices = []
    for dev in topology.devices:
        if dev.type in ["pc", "server"]:
            plans = device_ips.get(dev.id, [])
            if plans:
                p = plans[0]
                end_devices.append({
                    "id": dev.id,
                    "is_dhcp": False,
                    "ip": p["ip"],
                    "mask": p["mask"],
                    "gateway": p.get("gateway") or ""
                })
            else:
                end_devices.append({
                    "id": dev.id,
                    "is_dhcp": len(topology.services.dhcp) > 0,
                    "ip": "0.0.0.0",
                    "mask": "0.0.0.0",
                    "gateway": "0.0.0.0"
                })

    # 4. Generate PTBuilder JS Script
    ptbuilder_template = jinja_env.get_template("ptbuilder.j2")
    ptbuilder_script = ptbuilder_template.render(
        topology=topology,
        end_devices=end_devices,
        cli_configs=cli_configs
    )

    return GenerateResponse(
        ptbuilder_script=ptbuilder_script.strip(),
        cli_configs=cli_configs
    )
