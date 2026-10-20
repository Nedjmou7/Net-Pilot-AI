import pytest
from backend.models import (
    Topology, Device, Link, Vlan, IpPlanItem,
    RoutingConfig, ServicesConfig, DhcpPool
)
from backend.services.validator import validate_topology
from backend.services.generator import generate_all_artifacts, generate_ios_configs, generate_ptbuilder_script
from backend.services.topology_agent import (
    count_validation_errors,
    requested_device_counts,
    requested_protocol,
    build_exact_count_topology,
)


def build_sample_topology() -> Topology:
    return Topology(
        name="test-topology",
        devices=[
            Device(id="R1", type="router", model="2911", x=200, y=100),
            Device(id="SW1", type="switch", model="2960-24TT", x=200, y=250),
            Device(id="PC1", type="pc", model="PC-PT", x=100, y=400)
        ],
        links=[
            Link(a="R1", a_port="GigabitEthernet0/0", b="SW1", b_port="GigabitEthernet0/1", cable="straight"),
            Link(a="SW1", a_port="FastEthernet0/1", b="PC1", b_port="FastEthernet0", cable="straight")
        ],
        vlans=[],
        ip_plan=[
            IpPlanItem(device="R1", interface="GigabitEthernet0/0", ip="192.168.10.1", mask="255.255.255.0"),
            IpPlanItem(device="PC1", interface="FastEthernet0", ip="192.168.10.10", mask="255.255.255.0", gateway="192.168.10.1")
        ],
        routing=RoutingConfig(protocol="none"),
        services=ServicesConfig(dhcp=[])
    )


def test_requested_device_counts_are_enforced():
    topo = build_sample_topology()
    requested = requested_device_counts("Build 3 routers, 5 switches, and 10 PCs with DHCP")
    errors = count_validation_errors(topo, requested)
    assert requested == {"router": 3, "switch": 5, "pc": 10}
    assert "Requested 3 routers, but generated 1." in errors
    assert "Requested 5 switches, but generated 1." in errors
    assert "Requested 10 pcs, but generated 1." in errors


def test_requested_protocol_is_preserved_for_exact_topology():
    request = "Build 3 routers, 5 switches, and 10 PCs using EIGRP with DHCP"
    topology = build_exact_count_topology(
        request,
        requested_device_counts(request),
        requested_protocol(request),
    )
    assert topology is not None
    assert topology.routing.protocol == "eigrp"
    assert any("not natively generated" in warning for warning in validate_topology(topology).warnings)


def test_arbitrary_requested_protocol_is_preserved():
    assert requested_protocol("Build 3 routers using VXLAN with DHCP") == "vxlan"


# 1. Valid topology test
def test_valid_topology():
    topo = build_sample_topology()
    res = validate_topology(topo)
    assert len(res.errors) == 0, f"Expected 0 errors, got: {res.errors}"


# 2. Duplicate device IDs test
def test_duplicate_device_ids():
    topo = build_sample_topology()
    topo.devices.append(Device(id="R1", type="router", model="2911", x=300, y=100))
    res = validate_topology(topo)
    assert any("Duplicate device ID" in err for err in res.errors)


# 3. Non-existent device in link
def test_nonexistent_device_in_link():
    topo = build_sample_topology()
    topo.links.append(Link(a="R1", a_port="GigabitEthernet0/1", b="GhostDevice", b_port="FastEthernet0/1", cable="straight"))
    res = validate_topology(topo)
    assert any("GhostDevice" in err for err in res.errors)


# 4. Invalid port for model
def test_invalid_port_for_model():
    topo = build_sample_topology()
    topo.links.append(Link(a="R1", a_port="FastEthernet0/99", b="SW1", b_port="FastEthernet0/2", cable="straight"))
    res = validate_topology(topo)
    assert any("Invalid port" in err for err in res.errors)


# 5. Port reused multiple times
def test_port_reused_multiple_times():
    topo = build_sample_topology()
    # R1 GigabitEthernet0/0 is already linked to SW1; link it again to SW1 FastEthernet0/3
    topo.links.append(Link(a="R1", a_port="GigabitEthernet0/0", b="SW1", b_port="FastEthernet0/3", cable="straight"))
    res = validate_topology(topo)
    assert any("used in multiple links" in err for err in res.errors)


# 6. Duplicate IP assignment
def test_duplicate_ip_assignment():
    topo = build_sample_topology()
    topo.ip_plan.append(IpPlanItem(device="SW1", interface="Vlan1", ip="192.168.10.10", mask="255.255.255.0"))
    res = validate_topology(topo)
    assert any("Duplicate IP" in err for err in res.errors)


# 7. Gateway outside subnet
def test_gateway_outside_subnet():
    topo = build_sample_topology()
    topo.ip_plan[1].gateway = "10.0.0.1"  # PC1 is in 192.168.10.0/24
    res = validate_topology(topo)
    assert any("outside subnet" in err for err in res.errors)


# 8. Device linked to itself
def test_device_self_link():
    topo = build_sample_topology()
    topo.links.append(Link(a="SW1", a_port="FastEthernet0/5", b="SW1", b_port="FastEthernet0/6", cable="cross"))
    res = validate_topology(topo)
    assert any("itself" in err for err in res.errors)


# 9. Empty topology error
def test_empty_topology():
    topo = Topology(devices=[], links=[])
    res = validate_topology(topo)
    assert len(res.errors) > 0
    assert "no devices" in res.errors[0]


# 10. Invalid IP address format
def test_invalid_ip_format():
    topo = build_sample_topology()
    topo.ip_plan.append(IpPlanItem(device="R1", interface="GigabitEthernet0/1", ip="999.999.999.999", mask="255.255.255.0"))
    res = validate_topology(topo)
    assert any("Invalid IP/mask" in err for err in res.errors)


# 11. Generator PTBuilder script checks
def test_generator_ptbuilder_output():
    topo = build_sample_topology()
    script = generate_ptbuilder_script(topo)
    assert "function main()" in script
    assert 'addDevice("R1", "2911", 200, 100);' in script
    assert 'addDevice("SW1", "2960-24TT", 200, 250);' in script
    assert 'addDevice("PC1", "PC-PT", 100, 400);' in script
    assert 'addLink("R1", "GigabitEthernet0/0", "SW1", "GigabitEthernet0/1", "straight");' in script
    assert 'configurePcIp("PC1", false, "192.168.10.10", "255.255.255.0", "192.168.10.1");' in script
    assert 'configureIosDevice("R1"' in script


def test_dhcp_artifacts_use_dhcp_hosts_and_local_router_pools():
    from backend.services.topology_agent import build_exact_count_topology, requested_device_counts
    from backend.services.generator import generate_all_artifacts

    request = "Build 3 routers, 5 switches, and 10 PCs with DHCP and OSPF"
    topology = build_exact_count_topology(request, requested_device_counts(request), "ospf")
    script, configs = generate_all_artifacts(topology)

    assert 'configurePcIp("PC1", true, "", "", "");' in script
    assert "ip dhcp pool LAN_1_POOL" in configs["R1"]
    assert "ip dhcp pool LAN_2_POOL" not in configs["R1"]
    assert "ip dhcp pool LAN_3_POOL" not in configs["R1"]
    assert "ip dhcp pool LAN_2_POOL" in configs["R2"]
    assert "ip dhcp pool LAN_1_POOL" not in configs["R2"]


# 12. Generator IOS router config checks
def test_generator_ios_configs_router():
    topo = build_sample_topology()
    configs = generate_ios_configs(topo)
    r1_cfg = configs["R1"]
    assert "hostname R1" in r1_cfg
    assert "interface GigabitEthernet0/0" in r1_cfg
    assert "ip address 192.168.10.1 255.255.255.0" in r1_cfg
    assert "no shutdown" in r1_cfg
    assert "write memory" in r1_cfg


# 13. Generator Switch VLAN configs
def test_generator_switch_vlans():
    topo = build_sample_topology()
    topo.vlans = [Vlan(id=10, name="SALES"), Vlan(id=20, name="ENGINEERING")]
    configs = generate_ios_configs(topo)
    sw_cfg = configs["SW1"]
    assert "vlan 10" in sw_cfg
    assert "name SALES" in sw_cfg
    assert "vlan 20" in sw_cfg
    assert "name ENGINEERING" in sw_cfg


# 14. Generator OSPF routing configuration
def test_generator_ospf_routing():
    topo = build_sample_topology()
    topo.routing = RoutingConfig(protocol="ospf", process_id=1, area=0)
    configs = generate_ios_configs(topo)
    r1_cfg = configs["R1"]
    assert "router ospf 1" in r1_cfg
    assert "network 192.168.10.0 0.0.0.255 area 0" in r1_cfg


# 15. Generator DHCP pool configuration
def test_generator_dhcp_pool():
    topo = build_sample_topology()
    topo.services.dhcp = [
        DhcpPool(pool_name="STAFF_NET", network="192.168.10.0", mask="255.255.255.0", default_router="192.168.10.1", dns_server="8.8.8.8")
    ]
    configs = generate_ios_configs(topo)
    r1_cfg = configs["R1"]
    assert "ip dhcp pool STAFF_NET" in r1_cfg
    assert "network 192.168.10.0 255.255.255.0" in r1_cfg
    assert "default-router 192.168.10.1" in r1_cfg
    assert "dns-server 8.8.8.8" in r1_cfg


# 16. Subinterface router-on-a-stick generation
def test_subinterface_router_on_a_stick():
    topo = build_sample_topology()
    topo.vlans = [Vlan(id=10, name="STAFF")]
    topo.ip_plan = [
        IpPlanItem(device="R1", interface="GigabitEthernet0/0.10", ip="192.168.10.1", mask="255.255.255.0"),
        IpPlanItem(device="PC1", interface="FastEthernet0", ip="192.168.10.10", mask="255.255.255.0", gateway="192.168.10.1")
    ]
    configs = generate_ios_configs(topo)
    r1_cfg = configs["R1"]
    assert "interface GigabitEthernet0/0.10" in r1_cfg
    assert "encapsulation dot1Q 10" in r1_cfg
    assert "ip address 192.168.10.1 255.255.255.0" in r1_cfg


def test_duplicate_vlan_ids_are_rejected():
    topo = build_sample_topology()
    topo.vlans = [Vlan(id=10, name="STAFF"), Vlan(id=10, name="DUPLICATE")]
    result = validate_topology(topo)
    assert any("Duplicate VLAN ID" in error for error in result.errors)


def test_overlapping_subnets_are_rejected():
    topo = build_sample_topology()
    topo.ip_plan.append(
        IpPlanItem(
            device="R1",
            interface="GigabitEthernet0/1",
            ip="192.168.10.129",
            mask="255.255.255.128",
        )
    )
    result = validate_topology(topo)
    assert any("Overlapping subnets" in error for error in result.errors)


def test_duplicate_ip_plan_interface_is_rejected():
    topo = build_sample_topology()
    topo.ip_plan.append(
        IpPlanItem(
            device="R1",
            interface="GigabitEthernet0/0",
            ip="192.168.10.2",
            mask="255.255.255.0",
        )
    )
    result = validate_topology(topo)
    assert any("multiple IP plan entries" in error for error in result.errors)


def test_ip_plan_rejects_unknown_physical_interface():
    topo = build_sample_topology()
    topo.ip_plan.append(
        IpPlanItem(
            device="R1",
            interface="GigabitEthernet0/9",
            ip="192.168.20.1",
            mask="255.255.255.0",
        )
    )
    result = validate_topology(topo)
    assert any("Invalid interface" in error for error in result.errors)


def test_subinterface_requires_declared_vlan():
    topo = build_sample_topology()
    topo.ip_plan[0].interface = "GigabitEthernet0/0.10"
    result = validate_topology(topo)
    assert any("VLAN 10" in warning for warning in result.warnings)
