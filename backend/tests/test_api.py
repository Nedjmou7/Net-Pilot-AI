import pytest
from starlette.testclient import TestClient
from app.main import app
from app.models import Topology, Device, Link, IpAssignment

client = TestClient(app)

def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "database" in data
    assert "ollama" in data

def test_api_validate():
    topo = {
        "name": "test-val",
        "devices": [
            {"id": "R1", "type": "router", "model": "2911", "x": 100, "y": 100},
            {"id": "PC1", "type": "pc", "model": "PC-PT", "x": 100, "y": 300}
        ],
        "links": [
            {"a": "R1", "a_port": "GigabitEthernet0/0", "b": "PC1", "b_port": "FastEthernet0", "cable": "crossover"}
        ],
        "vlans": [],
        "ip_plan": [
            {"device": "R1", "interface": "GigabitEthernet0/0", "ip": "192.168.1.1", "mask": "255.255.255.0"},
            {"device": "PC1", "interface": "FastEthernet0", "ip": "192.168.1.50", "mask": "255.255.255.0", "gateway": "192.168.1.1"}
        ],
        "routing": {"protocol": "none"},
        "services": {"dhcp": [], "nat": None, "acls": []}
    }
    res = client.post("/api/topology/validate", json=topo)
    assert res.status_code == 200
    data = res.json()
    assert data["is_valid"] is True
    assert len(data["errors"]) == 0

def test_api_generate():
    topo = {
        "name": "test-gen",
        "devices": [
            {"id": "R1", "type": "router", "model": "2911", "x": 100, "y": 100}
        ],
        "links": [],
        "vlans": [],
        "ip_plan": [
            {"device": "R1", "interface": "GigabitEthernet0/0", "ip": "10.0.0.1", "mask": "255.255.255.252"}
        ],
        "routing": {"protocol": "ospf", "process_id": 1, "area": 0},
        "services": {"dhcp": [], "nat": None, "acls": []}
    }
    res = client.post("/api/topology/generate", json={"topology": topo})
    assert res.status_code == 200
    data = res.json()
    assert "ptbuilder_script" in data
    assert "cli_configs" in data
    assert "R1" in data["cli_configs"]
    assert "router ospf 1" in data["cli_configs"]["R1"]

def test_api_projects_crud():
    topo = {
        "name": "crud-proj",
        "devices": [{"id": "R1", "type": "router", "model": "2911", "x": 100, "y": 100}],
        "links": [], "vlans": [], "ip_plan": [], "routing": {"protocol": "none"},
        "services": {"dhcp": [], "nat": None, "acls": []}
    }
    create_res = client.post("/api/projects", json={"name": "Test Project Alpha", "topology": topo})
    assert create_res.status_code == 200
    p = create_res.json()
    p_id = p["id"]

    get_res = client.get(f"/api/projects/{p_id}")
    assert get_res.status_code == 200
    assert get_res.json()["project"]["name"] == "Test Project Alpha"

    list_res = client.get("/api/projects")
    assert list_res.status_code == 200
    assert any(x["id"] == p_id for x in list_res.json())

    del_res = client.delete(f"/api/projects/{p_id}")
    assert del_res.status_code == 200

def test_api_chat_build():
    res = client.post("/api/chat", json={"message": "Build a network with 3 routers and OSPF"})
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "build"
    assert data["topology"] is not None
    assert "devices" in data["topology"]
    assert len(data["topology"]["devices"]) >= 3
