import pytest
from app.models import Topology, Device, Link, Vlan, IpAssignment, RoutingConfig, ServicesConfig, DhcpPool
from app.services.generator import generate_artifacts, subnet_mask_to_wildcard

def test_wildcard_conversion():
    assert subnet_mask_to_wildcard("255.255.255.0") == "0.0.0.255"
    assert subnet_mask_to_wildcard("255.255.255.252") == "0.0.0.3"
    assert subnet_mask_to_wildcard("255.255.0.0") == "0.0.255.255"

def test_generate_router_ios_config():
    topo = Topology(
        name="test-router",
        devices=[
            Device(id="R1", type="router", model="2911", x=100, y=100)
        ],
        ip_plan=[
            IpAssignment(device="R1", interface="GigabitEthernet0/0", ip="192.168.10.1", mask="255.255.255.0")
        ],
        routing=RoutingConfig(protocol="ospf", process_id=1, area=0)
    )
    res = generate_artifacts(topo)
    assert "R1" in res.cli_configs
    r1_cfg = res.cli_configs["R1"]
    assert "hostname R1" in r1_cfg
    assert "interface GigabitEthernet0/0" in r1_cfg
    assert "ip address 192.168.10.1 255.255.255.0" in r1_cfg
    assert "router ospf 1" in r1_cfg
    assert "network 192.168.10.0 0.0.0.255 area 0" in r1_cfg

def test_generate_router_on_a_stick():
    topo = Topology(
        name="test-roas",
        devices=[
            Device(id="R1", type="router", model="2911", x=100, y=100)
        ],
        ip_plan=[
            IpAssignment(device="R1", interface="GigabitEthernet0/0.10", ip="192.168.10.1", mask="255.255.255.0"),
            IpAssignment(device="R1", interface="GigabitEthernet0/0.20", ip="192.168.20.1", mask="255.255.255.0")
        ]
    )
    res = generate_artifacts(topo)
    r1_cfg = res.cli_configs["R1"]
    assert "interface GigabitEthernet0/0.10" in r1_cfg
    assert "encapsulation dot1Q 10" in r1_cfg
    assert "interface GigabitEthernet0/0.20" in r1_cfg
    assert "encapsulation dot1Q 20" in r1_cfg

def test_generate_switch_vlans_and_trunks():
    topo = Topology(
        name="test-switch",
        devices=[
            Device(id="R1", type="router", model="2911", x=100, y=100),
            Device(id="SW1", type="switch", model="2960-24TT", x=100, y=250),
            Device(id="PC1", type="pc", model="PC-PT", x=100, y=400)
        ],
        links=[
            Link(a="SW1", a_port="GigabitEthernet0/1", b="R1", b_port="GigabitEthernet0/0", cable="straight"),
            Link(a="SW1", a_port="FastEthernet0/1", b="PC1", b_port="FastEthernet0", cable="straight")
        ],
        vlans=[
            Vlan(id=10, name="ENGINEERING"),
            Vlan(id=20, name="SALES")
        ]
    )
    res = generate_artifacts(topo)
    sw1_cfg = res.cli_configs["SW1"]
    assert "hostname SW1" in sw1_cfg
    assert "vlan 10" in sw1_cfg
    assert "name ENGINEERING" in sw1_cfg
    assert "vlan 20" in sw1_cfg
    assert "name SALES" in sw1_cfg
    # GigabitEthernet0/1 connects to router -> trunk
    assert "interface GigabitEthernet0/1" in sw1_cfg
    assert "switchport mode trunk" in sw1_cfg
    # FastEthernet0/1 connects to PC -> access
    assert "interface FastEthernet0/1" in sw1_cfg
    assert "switchport mode access" in sw1_cfg

def test_generate_ptbuilder_script():
    topo = Topology(
        name="test-ptbuilder",
        devices=[
            Device(id="R1", type="router", model="2911", x=200, y=100),
            Device(id="PC1", type="pc", model="PC-PT", x=200, y=300)
        ],
        links=[
            Link(a="R1", a_port="GigabitEthernet0/0", b="PC1", b_port="FastEthernet0", cable="crossover")
        ],
        ip_plan=[
            IpAssignment(device="R1", interface="GigabitEthernet0/0", ip="192.168.1.1", mask="255.255.255.0"),
            IpAssignment(device="PC1", interface="FastEthernet0", ip="192.168.1.50", mask="255.255.255.0", gateway="192.168.1.1")
        ]
    )
    res = generate_artifacts(topo)
    script = res.ptbuilder_script
    assert 'addDevice("R1", "2911", 200, 100);' in script
    assert 'addDevice("PC1", "PC-PT", 200, 300);' in script
    assert 'addLink("R1", "GigabitEthernet0/0", "PC1", "FastEthernet0", "crossover");' in script
    assert 'configurePcIp("PC1", false, "192.168.1.50", "255.255.255.0", "192.168.1.1");' in script
    assert 'configureIosDevice("R1"' in script
