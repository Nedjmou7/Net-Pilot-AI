import os
import sys
import json
import random
from typing import List, Dict, Any

# Ensure backend package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.models import Topology
from app.services.validator import validate_topology

DATASET_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(DATASET_DIR, exist_ok=True)

PROMPT_TEMPLATES = [
    "Build a network with {r_count} routers, {sw_count} switches, and {pc_count} PCs using {routing}.",
    "Create a {name} topology with {r_count} routers connected via {routing} and {pc_count} client PCs.",
    "Design a network lab with {r_count} routers, {sw_count} switches, and DHCP for {pc_count} hosts.",
    "I need a {r_count}-router network configured with {routing} protocol and {pc_count} endpoints.",
    "Set up a {name} infrastructure with {vlan_count} VLANs, inter-VLAN routing, and {pc_count} computers.",
    "Generate a topology with {r_count} routers and {pc_count} workstations running {routing}."
]

def generate_random_valid_topology(idx: int):
    topo_type = random.choice(["linear_ospf", "vlan_dhcp", "small_office", "star_rip"])
    devices = []
    links = []
    vlans = []
    ip_plan = []
    routing = {"protocol": "none", "process_id": None, "area": None}
    services = {"dhcp": [], "nat": None, "acls": []}

    if topo_type == "linear_ospf":
        r_count = random.choice([2, 3, 4])
        sw_count = r_count
        pc_count = r_count
        name = f"linear-ospf-{r_count}r"

        for i in range(1, r_count + 1):
            devices.append({"id": f"R{i}", "type": "router", "model": "2911", "x": 150 * i, "y": 120})
            devices.append({"id": f"SW{i}", "type": "switch", "model": "2960-24TT", "x": 150 * i, "y": 280})
            devices.append({"id": f"PC{i}", "type": "pc", "model": "PC-PT", "x": 150 * i, "y": 450})

            # Router to local Switch
            links.append({"a": f"R{i}", "a_port": "GigabitEthernet0/0", "b": f"SW{i}", "b_port": "GigabitEthernet0/1", "cable": "straight"})
            # Switch to local PC
            links.append({"a": f"SW{i}", "a_port": "FastEthernet0/1", "b": f"PC{i}", "b_port": "FastEthernet0", "cable": "straight"})

            # LAN IP plan
            ip_plan.append({"device": f"R{i}", "interface": "GigabitEthernet0/0", "ip": f"192.168.{i}.1", "mask": "255.255.255.0", "gateway": None})
            ip_plan.append({"device": f"PC{i}", "interface": "FastEthernet0", "ip": f"192.168.{i}.10", "mask": "255.255.255.0", "gateway": f"192.168.{i}.1"})

        # Point-to-point links between routers
        for i in range(1, r_count):
            links.append({
                "a": f"R{i}", "a_port": "GigabitEthernet0/1",
                "b": f"R{i+1}", "b_port": "GigabitEthernet0/2",
                "cable": "crossover"
            })
            ip_plan.append({"device": f"R{i}", "interface": "GigabitEthernet0/1", "ip": f"10.0.{i}.1", "mask": "255.255.255.252", "gateway": None})
            ip_plan.append({"device": f"R{i+1}", "interface": "GigabitEthernet0/2", "ip": f"10.0.{i}.2", "mask": "255.255.255.252", "gateway": None})

        routing = {"protocol": "ospf", "process_id": 1, "area": 0}
        prompt = random.choice(PROMPT_TEMPLATES).format(
            r_count=r_count, sw_count=sw_count, pc_count=pc_count, routing="OSPF", name="OSPF backbone", vlan_count=0
        )

    elif topo_type == "vlan_dhcp":
        v_count = random.choice([2, 3])
        name = f"vlan-roas-{v_count}v"
        devices.append({"id": "R1", "type": "router", "model": "2911", "x": 350, "y": 120})
        devices.append({"id": "SW1", "type": "switch", "model": "2960-24TT", "x": 350, "y": 280})
        links.append({"a": "R1", "a_port": "GigabitEthernet0/0", "b": "SW1", "b_port": "GigabitEthernet0/1", "cable": "straight"})

        vlan_names = ["STAFF", "VOICE", "STUDENTS", "GUESTS", "FINANCE"]
        for vi in range(1, v_count + 1):
            vid = vi * 10
            vname = vlan_names[vi - 1]
            vlans.append({"id": vid, "name": vname})
            devices.append({"id": f"PC{vi}", "type": "pc", "model": "PC-PT", "x": 150 + vi * 120, "y": 450})
            links.append({"a": "SW1", "a_port": f"FastEthernet0/{vi}", "b": f"PC{vi}", "b_port": "FastEthernet0", "cable": "straight"})

            gw_ip = f"192.168.{vid}.1"
            pc_ip = f"192.168.{vid}.{vi*10}"
            ip_plan.append({"device": "R1", "interface": f"GigabitEthernet0/0.{vid}", "ip": gw_ip, "mask": "255.255.255.0", "gateway": None})
            ip_plan.append({"device": f"PC{vi}", "interface": "FastEthernet0", "ip": pc_ip, "mask": "255.255.255.0", "gateway": gw_ip})

            services["dhcp"].append({
                "pool_name": f"POOL_{vname}",
                "network": f"192.168.{vid}.0",
                "mask": "255.255.255.0",
                "default_router": gw_ip,
                "dns_server": "8.8.8.8"
            })

        prompt = f"Create a network with 1 router, 1 switch, {v_count} VLANs with inter-VLAN routing and DHCP."

    else:
        # Small office or star topology
        name = f"office-{idx}"
        devices.append({"id": "R1", "type": "router", "model": "2911", "x": 300, "y": 120})
        devices.append({"id": "SW1", "type": "switch", "model": "2960-24TT", "x": 300, "y": 280})
        links.append({"a": "R1", "a_port": "GigabitEthernet0/0", "b": "SW1", "b_port": "GigabitEthernet0/1", "cable": "straight"})

        devices.append({"id": "PC1", "type": "pc", "model": "PC-PT", "x": 200, "y": 450})
        devices.append({"id": "PC2", "type": "pc", "model": "PC-PT", "x": 400, "y": 450})
        links.append({"a": "SW1", "a_port": "FastEthernet0/1", "b": "PC1", "b_port": "FastEthernet0", "cable": "straight"})
        links.append({"a": "SW1", "a_port": "FastEthernet0/2", "b": "PC2", "b_port": "FastEthernet0", "cable": "straight"})

        ip_plan.append({"device": "R1", "interface": "GigabitEthernet0/0", "ip": "192.168.1.1", "mask": "255.255.255.0", "gateway": None})
        ip_plan.append({"device": "PC1", "interface": "FastEthernet0", "ip": "192.168.1.10", "mask": "255.255.255.0", "gateway": "192.168.1.1"})
        ip_plan.append({"device": "PC2", "interface": "FastEthernet0", "ip": "192.168.1.20", "mask": "255.255.255.0", "gateway": "192.168.1.1"})

        prompt = "Build a small office network with 1 router, 1 switch, and 2 PCs."

    topo = {
        "name": name,
        "devices": devices,
        "links": links,
        "vlans": vlans,
        "ip_plan": ip_plan,
        "routing": routing,
        "services": services
    }

    # Verify that it strictly passes pydantic and validator
    pydantic_obj = Topology.model_validate(topo)
    val = validate_topology(pydantic_obj)
    if not val.is_valid:
        raise ValueError(f"Generated topology failed validation: {val.errors}")

    return prompt, topo

def generate_datasets(train_count: int = 500, val_count: int = 50):
    system_prompt = "You are TopoGemma, an expert Cisco networking assistant. Output valid topology JSON only matching the schema."

    train_path = os.path.join(DATASET_DIR, "train.jsonl")
    val_path = os.path.join(DATASET_DIR, "val.jsonl")

    print(f"Generating {train_count} training examples...")
    with open(train_path, "w", encoding="utf-8") as f_train:
        for i in range(train_count):
            prompt, topo = generate_random_valid_topology(i)
            entry = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": json.dumps(topo)}
                ]
            }
            f_train.write(json.dumps(entry) + "\n")

    print(f"Generating {val_count} validation examples...")
    with open(val_path, "w", encoding="utf-8") as f_val:
        for i in range(val_count):
            prompt, topo = generate_random_valid_topology(1000 + i)
            entry = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": json.dumps(topo)}
                ]
            }
            f_val.write(json.dumps(entry) + "\n")

    print(f"Successfully generated:\n- {train_path} ({train_count} lines)\n- {val_path} ({val_count} lines)")

if __name__ == "__main__":
    generate_datasets(500, 50)
