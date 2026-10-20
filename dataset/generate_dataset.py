import os
import sys
import json
import random
from typing import Dict, Any, List, Tuple

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.models import Topology, Device, Link, Vlan, IpPlanItem, RoutingConfig, ServicesConfig, DhcpPool, NatConfig
from backend.services.validator import validate_topology

DATASET_DIR = os.path.abspath(os.path.dirname(__file__))
PROMPTS_DIR = os.path.abspath(os.path.join(DATASET_DIR, "..", "prompts"))

with open(os.path.join(PROMPTS_DIR, "system_build.md"), "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

VLAN_NAMES = ["STAFF", "MANAGEMENT", "SALES", "ENGINEERING", "HR", "GUEST", "VOICE", "IT_ADMIN", "STUDENTS", "FACULTY"]

PROMPT_TEMPLATES = [
    "Build a network with {desc}.",
    "Create a Cisco topology having {desc}.",
    "Design a network lab with {desc}.",
    "I need a Packet Tracer topology configured for {desc}.",
    "Please set up a network with {desc}.",
    "Generate a topology with {desc}."
]


def make_single_router_topology(idx: int) -> Tuple[Topology, str]:
    lan_net = random.choice([10, 20, 30, 40, 50, 100])
    num_pcs = random.randint(2, 4)
    has_dhcp = random.choice([True, False])
    has_server = random.choice([True, False])

    devices = [
        Device(id="R1", type="router", model="2911", x=350, y=120),
        Device(id="SW1", type="switch", model="2960-24TT", x=350, y=260)
    ]
    links = [
        Link(a="R1", a_port="GigabitEthernet0/0", b="SW1", b_port="GigabitEthernet0/1", cable="straight")
    ]
    ip_plan = [
        IpPlanItem(device="R1", interface="GigabitEthernet0/0", ip=f"192.168.{lan_net}.1", mask="255.255.255.0", gateway=None)
    ]

    current_x = 180
    for p in range(1, num_pcs + 1):
        pc_id = f"PC{p}"
        devices.append(Device(id=pc_id, type="pc", model="PC-PT", x=current_x, y=420))
        links.append(Link(a="SW1", a_port=f"FastEthernet0/{p}", b=pc_id, b_port="FastEthernet0", cable="straight"))
        ip_plan.append(IpPlanItem(
            device=pc_id,
            interface="FastEthernet0",
            ip=f"192.168.{lan_net}.{10 + p}",
            mask="255.255.255.0",
            gateway=f"192.168.{lan_net}.1"
        ))
        current_x += 160

    if has_server:
        devices.append(Device(id="SRV1", type="server", model="Server-PT", x=current_x, y=420))
        links.append(Link(a="SW1", a_port=f"FastEthernet0/{num_pcs + 1}", b="SRV1", b_port="FastEthernet0", cable="straight"))
        ip_plan.append(IpPlanItem(
            device="SRV1",
            interface="FastEthernet0",
            ip=f"192.168.{lan_net}.5",
            mask="255.255.255.0",
            gateway=f"192.168.{lan_net}.1"
        ))

    dhcp_pools = []
    if has_dhcp:
        dhcp_pools.append(DhcpPool(
            pool_name="LAN_POOL",
            network=f"192.168.{lan_net}.0",
            mask="255.255.255.0",
            default_router=f"192.168.{lan_net}.1",
            dns_server="8.8.8.8"
        ))

    topo = Topology(
        name=f"lan-setup-{idx}",
        devices=devices,
        links=links,
        vlans=[],
        ip_plan=ip_plan,
        routing=RoutingConfig(protocol="none"),
        services=ServicesConfig(dhcp=dhcp_pools)
    )

    desc = f"1 router, 1 switch, and {num_pcs} PCs"
    if has_server:
        desc += " plus a server"
    if has_dhcp:
        desc += " with DHCP configured"
    return topo, desc


def make_two_router_topology(idx: int) -> Tuple[Topology, str]:
    protocol = random.choice(["static", "rip", "ospf"])
    r1_net = random.randint(10, 50)
    r2_net = random.randint(60, 90)

    devices = [
        Device(id="R1", type="router", model="2911", x=250, y=140),
        Device(id="R2", type="router", model="2911", x=550, y=140),
        Device(id="SW1", type="switch", model="2960-24TT", x=250, y=280),
        Device(id="SW2", type="switch", model="2960-24TT", x=550, y=280),
        Device(id="PC1", type="pc", model="PC-PT", x=180, y=430),
        Device(id="PC2", type="pc", model="PC-PT", x=320, y=430),
        Device(id="PC3", type="pc", model="PC-PT", x=480, y=430),
        Device(id="PC4", type="pc", model="PC-PT", x=620, y=430)
    ]

    links = [
        Link(a="R1", a_port="GigabitEthernet0/1", b="R2", b_port="GigabitEthernet0/1", cable="cross"),
        Link(a="R1", a_port="GigabitEthernet0/0", b="SW1", b_port="GigabitEthernet0/1", cable="straight"),
        Link(a="R2", a_port="GigabitEthernet0/0", b="SW2", b_port="GigabitEthernet0/1", cable="straight"),
        Link(a="SW1", a_port="FastEthernet0/1", b="PC1", b_port="FastEthernet0", cable="straight"),
        Link(a="SW1", a_port="FastEthernet0/2", b="PC2", b_port="FastEthernet0", cable="straight"),
        Link(a="SW2", a_port="FastEthernet0/1", b="PC3", b_port="FastEthernet0", cable="straight"),
        Link(a="SW2", a_port="FastEthernet0/2", b="PC4", b_port="FastEthernet0", cable="straight")
    ]

    ip_plan = [
        IpPlanItem(device="R1", interface="GigabitEthernet0/1", ip="10.0.0.1", mask="255.255.255.252", gateway=None),
        IpPlanItem(device="R2", interface="GigabitEthernet0/1", ip="10.0.0.2", mask="255.255.255.252", gateway=None),
        IpPlanItem(device="R1", interface="GigabitEthernet0/0", ip=f"192.168.{r1_net}.1", mask="255.255.255.0", gateway=None),
        IpPlanItem(device="R2", interface="GigabitEthernet0/0", ip=f"192.168.{r2_net}.1", mask="255.255.255.0", gateway=None),
        IpPlanItem(device="PC1", interface="FastEthernet0", ip=f"192.168.{r1_net}.10", mask="255.255.255.0", gateway=f"192.168.{r1_net}.1"),
        IpPlanItem(device="PC2", interface="FastEthernet0", ip=f"192.168.{r1_net}.11", mask="255.255.255.0", gateway=f"192.168.{r1_net}.1"),
        IpPlanItem(device="PC3", interface="FastEthernet0", ip=f"192.168.{r2_net}.10", mask="255.255.255.0", gateway=f"192.168.{r2_net}.1"),
        IpPlanItem(device="PC4", interface="FastEthernet0", ip=f"192.168.{r2_net}.11", mask="255.255.255.0", gateway=f"192.168.{r2_net}.1")
    ]

    routing = RoutingConfig(protocol=protocol, process_id=1 if protocol == "ospf" else None, area=0 if protocol == "ospf" else None)

    topo = Topology(
        name=f"two-router-{protocol}-{idx}",
        devices=devices,
        links=links,
        vlans=[],
        ip_plan=ip_plan,
        routing=routing,
        services=ServicesConfig()
    )

    desc = f"2 routers connecting 2 LANs (4 PCs total) using {protocol.upper()} routing"
    return topo, desc


def make_router_on_a_stick_topology(idx: int) -> Tuple[Topology, str]:
    vlan_a = random.randint(10, 30)
    vlan_b = random.randint(40, 60)
    name_a = random.choice(["STAFF", "SALES", "MARKETING"])
    name_b = random.choice(["GUEST", "ENGINEERING", "DEV"])

    devices = [
        Device(id="R1", type="router", model="2911", x=350, y=120),
        Device(id="SW1", type="switch", model="2960-24TT", x=350, y=270),
        Device(id="PC1", type="pc", model="PC-PT", x=220, y=430),
        Device(id="PC2", type="pc", model="PC-PT", x=480, y=430)
    ]

    links = [
        Link(a="R1", a_port="GigabitEthernet0/0", b="SW1", b_port="GigabitEthernet0/1", cable="straight"),
        Link(a="SW1", a_port="FastEthernet0/1", b="PC1", b_port="FastEthernet0", cable="straight"),
        Link(a="SW1", a_port="FastEthernet0/2", b="PC2", b_port="FastEthernet0", cable="straight")
    ]

    vlans = [
        Vlan(id=vlan_a, name=name_a),
        Vlan(id=vlan_b, name=name_b)
    ]

    ip_plan = [
        IpPlanItem(device="R1", interface=f"GigabitEthernet0/0.{vlan_a}", ip=f"192.168.{vlan_a}.1", mask="255.255.255.0", gateway=None),
        IpPlanItem(device="R1", interface=f"GigabitEthernet0/0.{vlan_b}", ip=f"192.168.{vlan_b}.1", mask="255.255.255.0", gateway=None),
        IpPlanItem(device="PC1", interface="FastEthernet0", ip=f"192.168.{vlan_a}.10", mask="255.255.255.0", gateway=f"192.168.{vlan_a}.1"),
        IpPlanItem(device="PC2", interface="FastEthernet0", ip=f"192.168.{vlan_b}.10", mask="255.255.255.0", gateway=f"192.168.{vlan_b}.1")
    ]

    services = ServicesConfig(
        dhcp=[
            DhcpPool(pool_name=f"{name_a}_POOL", network=f"192.168.{vlan_a}.0", mask="255.255.255.0", default_router=f"192.168.{vlan_a}.1", dns_server="1.1.1.1"),
            DhcpPool(pool_name=f"{name_b}_POOL", network=f"192.168.{vlan_b}.0", mask="255.255.255.0", default_router=f"192.168.{vlan_b}.1", dns_server="1.1.1.1")
        ]
    )

    topo = Topology(
        name=f"roas-vlan-{idx}",
        devices=devices,
        links=links,
        vlans=vlans,
        ip_plan=ip_plan,
        routing=RoutingConfig(protocol="none"),
        services=services
    )

    desc = f"router-on-a-stick with 2 VLANs (VLAN {vlan_a} {name_a} and VLAN {vlan_b} {name_b}) and DHCP"
    return topo, desc


def make_three_router_ospf_topology(idx: int) -> Tuple[Topology, str]:
    devices = [
        Device(id="R1", type="router", model="2911", x=200, y=130),
        Device(id="R2", type="router", model="2911", x=450, y=130),
        Device(id="R3", type="router", model="2911", x=700, y=130),
        Device(id="SW1", type="switch", model="2960-24TT", x=200, y=280),
        Device(id="SW2", type="switch", model="2960-24TT", x=700, y=280),
        Device(id="PC1", type="pc", model="PC-PT", x=130, y=440),
        Device(id="PC2", type="pc", model="PC-PT", x=270, y=440),
        Device(id="PC3", type="pc", model="PC-PT", x=700, y=440)
    ]

    links = [
        Link(a="R1", a_port="GigabitEthernet0/1", b="R2", b_port="GigabitEthernet0/0", cable="cross"),
        Link(a="R2", a_port="GigabitEthernet0/1", b="R3", b_port="GigabitEthernet0/0", cable="cross"),
        Link(a="R1", a_port="GigabitEthernet0/0", b="SW1", b_port="GigabitEthernet0/1", cable="straight"),
        Link(a="R3", a_port="GigabitEthernet0/1", b="SW2", b_port="GigabitEthernet0/1", cable="straight"),
        Link(a="SW1", a_port="FastEthernet0/1", b="PC1", b_port="FastEthernet0", cable="straight"),
        Link(a="SW1", a_port="FastEthernet0/2", b="PC2", b_port="FastEthernet0", cable="straight"),
        Link(a="SW2", a_port="FastEthernet0/1", b="PC3", b_port="FastEthernet0", cable="straight")
    ]

    vlans = [
        Vlan(id=10, name="MANAGEMENT"),
        Vlan(id=20, name="STAFF")
    ]

    ip_plan = [
        IpPlanItem(device="R1", interface="GigabitEthernet0/1", ip="10.0.12.1", mask="255.255.255.252", gateway=None),
        IpPlanItem(device="R2", interface="GigabitEthernet0/0", ip="10.0.12.2", mask="255.255.255.252", gateway=None),
        IpPlanItem(device="R2", interface="GigabitEthernet0/1", ip="10.0.23.1", mask="255.255.255.252", gateway=None),
        IpPlanItem(device="R3", interface="GigabitEthernet0/0", ip="10.0.23.2", mask="255.255.255.252", gateway=None),
        IpPlanItem(device="R1", interface="GigabitEthernet0/0.10", ip="192.168.10.1", mask="255.255.255.0", gateway=None),
        IpPlanItem(device="R1", interface="GigabitEthernet0/0.20", ip="192.168.20.1", mask="255.255.255.0", gateway=None),
        IpPlanItem(device="R3", interface="GigabitEthernet0/1", ip="192.168.30.1", mask="255.255.255.0", gateway=None),
        IpPlanItem(device="PC1", interface="FastEthernet0", ip="192.168.10.10", mask="255.255.255.0", gateway="192.168.10.1"),
        IpPlanItem(device="PC2", interface="FastEthernet0", ip="192.168.20.10", mask="255.255.255.0", gateway="192.168.20.1"),
        IpPlanItem(device="PC3", interface="FastEthernet0", ip="192.168.30.10", mask="255.255.255.0", gateway="192.168.30.1")
    ]

    services = ServicesConfig(
        dhcp=[
            DhcpPool(pool_name="MGMT_POOL", network="192.168.10.0", mask="255.255.255.0", default_router="192.168.10.1", dns_server="1.1.1.1"),
            DhcpPool(pool_name="STAFF_POOL", network="192.168.20.0", mask="255.255.255.0", default_router="192.168.20.1", dns_server="1.1.1.1")
        ]
    )

    topo = Topology(
        name=f"3-router-ospf-{idx}",
        devices=devices,
        links=links,
        vlans=vlans,
        ip_plan=ip_plan,
        routing=RoutingConfig(protocol="ospf", process_id=1, area=0),
        services=services
    )

    desc = "3 routers with OSPF Area 0, 2 switches, 3 PCs, and 2 VLANs with DHCP"
    return topo, desc


# Generator functions list

GENERATORS = [
    make_single_router_topology,
    make_two_router_topology,
    make_router_on_a_stick_topology,
    make_three_router_ospf_topology
]


def generate_example(idx: int) -> Dict[str, Any]:
    gen = random.choice(GENERATORS)
    topo, desc = gen(idx)

    # Validate strictly
    res = validate_topology(topo)
    if res.errors:
        raise ValueError(f"Generated invalid topology: {res.errors}")

    template = random.choice(PROMPT_TEMPLATES)
    user_prompt = template.format(desc=desc)

    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
            {"role": "assistant", "content": json.dumps(topo.model_dump())}
        ]
    }


def main():
    print("Generating 500 training examples (dataset/train.jsonl)...")
    train_path = os.path.join(DATASET_DIR, "train.jsonl")
    val_path = os.path.join(DATASET_DIR, "val.jsonl")

    with open(train_path, "w", encoding="utf-8") as f:
        for i in range(500):
            ex = generate_example(i)
            f.write(json.dumps(ex) + "\n")

    print("Generating 50 validation examples (dataset/val.jsonl)...")
    with open(val_path, "w", encoding="utf-8") as f:
        for i in range(50):
            ex = generate_example(500 + i)
            f.write(json.dumps(ex) + "\n")

    print("Fine-tuning datasets successfully generated and 100% verified with Pydantic validator!")


if __name__ == "__main__":
    main()
