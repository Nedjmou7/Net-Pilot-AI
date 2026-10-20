import pytest
from app.models import Topology, Device, Link, Vlan, IpAssignment, RoutingConfig, ServicesConfig, DhcpPool
from app.services.validator import validate_topology

def test_valid_topology_simple():
    topo = Topology(
        name="simple-valid",
        devices=[
            Device(id="R1", type="router", model="2911", x=100, y=100),
            Device(id="SW1", type="switch", model="2960-24TT", x=100, y=250),
            Device(id="PC1", type="pc", model="PC-PT", x=100, y=400)
        ],
        links=[
            Link(a="R1", a_port="GigabitEthernet0/0", b="SW1", b_port="GigabitEthernet0/1", cable="straight"),
            Link(a="SW1", a_port="FastEthernet0/1", b="PC1", b_port="FastEthernet0", cable="straight")
        ],
        ip_plan=[
            IpAssignment(device="R1", interface="GigabitEthernet0/0", ip="192.168.1.1", mask="255.255.255.0"),
            IpAssignment(device="PC1", interface="FastEthernet0", ip="192.168.1.50", mask="255.255.255.0", gateway="192.168.1.1")
        ]
    )
    result = validate_topology(topo)
    assert result.is_valid is True
    assert len(result.errors) == 0

def test_empty_devices():
    topo = Topology(name="empty", devices=[])
    result = validate_topology(topo)
    assert result.is_valid is False
    assert any("no devices" in e.lower() for e in result.errors)

def test_duplicate_device_id():
    topo = Topology(
        name="dup-id",
        devices=[
            Device(id="R1", type="router", model="2911"),
            Device(id="R1", type="router", model="2911")
        ]
    )
    result = validate_topology(topo)
    assert result.is_valid is False
    assert any("duplicate device id" in e.lower() for e in result.errors)

def test_link_nonexistent_device():
    topo = Topology(
        name="link-nonexistent",
        devices=[Device(id="R1", type="router", model="2911")],
        links=[Link(a="R1", a_port="GigabitEthernet0/0", b="GHOST", b_port="GigabitEthernet0/1")]
    )
    result = validate_topology(topo)
    assert result.is_valid is False
    assert any("non-existent device 'ghost'" in e.lower() for e in result.errors)

def test_link_self_loop():
    topo = Topology(
        name="self-loop",
        devices=[Device(id="R1", type="router", model="2911")],
        links=[Link(a="R1", a_port="GigabitEthernet0/0", b="R1", b_port="GigabitEthernet0/1")]
    )
    result = validate_topology(topo)
    assert result.is_valid is False
    assert any("cannot be linked to itself" in e.lower() for e in result.errors)

def test_invalid_port_for_model():
    topo = Topology(
        name="bad-port",
        devices=[
            Device(id="R1", type="router", model="2911"),
            Device(id="SW1", type="switch", model="2960-24TT")
        ],
        links=[
            Link(a="R1", a_port="FastEthernet99/99", b="SW1", b_port="GigabitEthernet0/1")
        ]
    )
    result = validate_topology(topo)
    assert result.is_valid is False
    assert any("is invalid for model" in e.lower() for e in result.errors)

def test_port_used_twice():
    topo = Topology(
        name="port-reuse",
        devices=[
            Device(id="R1", type="router", model="2911"),
            Device(id="SW1", type="switch", model="2960-24TT"),
            Device(id="SW2", type="switch", model="2960-24TT")
        ],
        links=[
            Link(a="R1", a_port="GigabitEthernet0/0", b="SW1", b_port="GigabitEthernet0/1"),
            Link(a="R1", a_port="GigabitEthernet0/0", b="SW2", b_port="GigabitEthernet0/1")
        ]
    )
    result = validate_topology(topo)
    assert result.is_valid is False
    assert any("already used" in e.lower() for e in result.errors)

def test_duplicate_ip_address():
    topo = Topology(
        name="dup-ip",
        devices=[
            Device(id="R1", type="router", model="2911"),
            Device(id="PC1", type="pc", model="PC-PT")
        ],
        ip_plan=[
            IpAssignment(device="R1", interface="GigabitEthernet0/0", ip="192.168.1.1", mask="255.255.255.0"),
            IpAssignment(device="PC1", interface="FastEthernet0", ip="192.168.1.1", mask="255.255.255.0")
        ]
    )
    result = validate_topology(topo)
    assert result.is_valid is False
    assert any("duplicate ip address" in e.lower() for e in result.errors)

def test_invalid_ip_format():
    topo = Topology(
        name="bad-ip-format",
        devices=[Device(id="R1", type="router", model="2911")],
        ip_plan=[
            IpAssignment(device="R1", interface="GigabitEthernet0/0", ip="999.888.777.666", mask="255.255.255.0")
        ]
    )
    result = validate_topology(topo)
    assert result.is_valid is False
    assert any("invalid ip/mask" in e.lower() for e in result.errors)

def test_gateway_mismatched_subnet():
    topo = Topology(
        name="mismatched-gw",
        devices=[
            Device(id="R1", type="router", model="2911"),
            Device(id="PC1", type="pc", model="PC-PT")
        ],
        ip_plan=[
            IpAssignment(device="R1", interface="GigabitEthernet0/0", ip="192.168.1.1", mask="255.255.255.0"),
            # PC is in 192.168.10.0/24 but gateway is 192.168.1.1
            IpAssignment(device="PC1", interface="FastEthernet0", ip="192.168.10.50", mask="255.255.255.0", gateway="192.168.1.1")
        ]
    )
    result = validate_topology(topo)
    assert result.is_valid is False
    assert any("not in the same subnet" in e.lower() for e in result.errors)

def test_dhcp_default_router_invalid_subnet():
    topo = Topology(
        name="bad-dhcp-gw",
        devices=[Device(id="R1", type="router", model="2911")],
        services=ServicesConfig(
            dhcp=[
                DhcpPool(
                    pool_name="TEST_POOL",
                    network="192.168.10.0",
                    mask="255.255.255.0",
                    default_router="10.0.0.1"  # Not inside 192.168.10.0/24
                )
            ]
        )
    )
    result = validate_topology(topo)
    assert result.is_valid is False
    assert any("default-router '10.0.0.1' is not in network" in e.lower() for e in result.errors)

def test_duplicate_vlan_id():
    topo = Topology(
        name="dup-vlan",
        devices=[Device(id="SW1", type="switch", model="2960-24TT")],
        vlans=[
            Vlan(id=10, name="STAFF"),
            Vlan(id=10, name="VOICE")
        ]
    )
    result = validate_topology(topo)
    assert result.is_valid is False
    assert any("duplicate vlan id '10'" in e.lower() for e in result.errors)
