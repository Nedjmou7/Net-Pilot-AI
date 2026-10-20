import sqlite3
import json
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

DB_FILE = os.getenv("DB_PATH", "app.db")
SCHEMA_FILE = os.path.join(os.path.dirname(__file__), "schema.sql")


_db_initialized = False

def get_db_connection() -> sqlite3.Connection:
    global _db_initialized
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    if not _db_initialized:
        cursor = conn.cursor()
        if os.path.exists(SCHEMA_FILE):
            with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
                cursor.executescript(f.read())
        conn.commit()
        _db_initialized = True
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    if os.path.exists(SCHEMA_FILE):
        with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())
    conn.commit()

    # Seed default templates if empty
    cursor.execute("SELECT COUNT(*) FROM lab_templates")
    if cursor.fetchone()[0] == 0:
        seed_lab_templates(cursor)
        conn.commit()

    conn.close()


def seed_lab_templates(cursor: sqlite3.Cursor):
    sample_templates = [
        (
            "3-Router OSPF Backbone",
            "Full CCNA lab with 3 Cisco 2911 routers running OSPF Area 0, connecting two branch LANs and a central distribution hub.",
            "Intermediate",
            json.dumps({
                "name": "3-router-ospf-backbone",
                "devices": [
                    {"id": "R1", "type": "router", "model": "2911", "x": 200, "y": 140},
                    {"id": "R2", "type": "router", "model": "2911", "x": 480, "y": 140},
                    {"id": "R3", "type": "router", "model": "2911", "x": 760, "y": 140},
                    {"id": "SW1", "type": "switch", "model": "2960-24TT", "x": 200, "y": 300},
                    {"id": "SW2", "type": "switch", "model": "2960-24TT", "x": 760, "y": 300},
                    {"id": "PC1", "type": "pc", "model": "PC-PT", "x": 140, "y": 460},
                    {"id": "PC2", "type": "pc", "model": "PC-PT", "x": 260, "y": 460},
                    {"id": "PC3", "type": "pc", "model": "PC-PT", "x": 760, "y": 460}
                ],
                "links": [
                    {"a": "R1", "a_port": "GigabitEthernet0/1", "b": "R2", "b_port": "GigabitEthernet0/0", "cable": "cross"},
                    {"a": "R2", "a_port": "GigabitEthernet0/1", "b": "R3", "b_port": "GigabitEthernet0/0", "cable": "cross"},
                    {"a": "R1", "a_port": "GigabitEthernet0/0", "b": "SW1", "b_port": "GigabitEthernet0/1", "cable": "straight"},
                    {"a": "R3", "a_port": "GigabitEthernet0/1", "b": "SW2", "b_port": "GigabitEthernet0/1", "cable": "straight"},
                    {"a": "SW1", "a_port": "FastEthernet0/1", "b": "PC1", "b_port": "FastEthernet0", "cable": "straight"},
                    {"a": "SW1", "a_port": "FastEthernet0/2", "b": "PC2", "b_port": "FastEthernet0", "cable": "straight"},
                    {"a": "SW2", "a_port": "FastEthernet0/1", "b": "PC3", "b_port": "FastEthernet0", "cable": "straight"}
                ],
                "vlans": [],
                "ip_plan": [
                    {"device": "R1", "interface": "GigabitEthernet0/1", "ip": "10.0.12.1", "mask": "255.255.255.252", "gateway": None},
                    {"device": "R2", "interface": "GigabitEthernet0/0", "ip": "10.0.12.2", "mask": "255.255.255.252", "gateway": None},
                    {"device": "R2", "interface": "GigabitEthernet0/1", "ip": "10.0.23.1", "mask": "255.255.255.252", "gateway": None},
                    {"device": "R3", "interface": "GigabitEthernet0/0", "ip": "10.0.23.2", "mask": "255.255.255.252", "gateway": None},
                    {"device": "R1", "interface": "GigabitEthernet0/0", "ip": "192.168.10.1", "mask": "255.255.255.0", "gateway": None},
                    {"device": "R3", "interface": "GigabitEthernet0/1", "ip": "192.168.30.1", "mask": "255.255.255.0", "gateway": None},
                    {"device": "PC1", "interface": "FastEthernet0", "ip": "192.168.10.10", "mask": "255.255.255.0", "gateway": "192.168.10.1"},
                    {"device": "PC2", "interface": "FastEthernet0", "ip": "192.168.10.11", "mask": "255.255.255.0", "gateway": "192.168.10.1"},
                    {"device": "PC3", "interface": "FastEthernet0", "ip": "192.168.30.10", "mask": "255.255.255.0", "gateway": "192.168.30.1"}
                ],
                "routing": {"protocol": "ospf", "process_id": 1, "area": 0},
                "services": {
                    "dhcp": [
                        {"pool_name": "LAN_A_POOL", "network": "192.168.10.0", "mask": "255.255.255.0", "default_router": "192.168.10.1", "dns_server": "8.8.8.8"},
                        {"pool_name": "LAN_B_POOL", "network": "192.168.30.0", "mask": "255.255.255.0", "default_router": "192.168.30.1", "dns_server": "8.8.8.8"}
                    ],
                    "nat": None,
                    "acls": []
                }
            })
        ),
        (
            "Inter-VLAN Routing (Router-on-a-Stick)",
            "VLAN 10 (Sales) and VLAN 20 (Engineering) segmented on a switch with 802.1Q trunking to a 2911 router subinterfaces.",
            "Beginner",
            json.dumps({
                "name": "inter-vlan-router-on-a-stick",
                "devices": [
                    {"id": "R1", "type": "router", "model": "2911", "x": 380, "y": 130},
                    {"id": "SW1", "type": "switch", "model": "2960-24TT", "x": 380, "y": 280},
                    {"id": "PC1", "type": "pc", "model": "PC-PT", "x": 220, "y": 440},
                    {"id": "PC2", "type": "pc", "model": "PC-PT", "x": 540, "y": 440}
                ],
                "links": [
                    {"a": "R1", "a_port": "GigabitEthernet0/0", "b": "SW1", "b_port": "GigabitEthernet0/1", "cable": "straight"},
                    {"a": "SW1", "a_port": "FastEthernet0/1", "b": "PC1", "b_port": "FastEthernet0", "cable": "straight"},
                    {"a": "SW1", "a_port": "FastEthernet0/2", "b": "PC2", "b_port": "FastEthernet0", "cable": "straight"}
                ],
                "vlans": [
                    {"id": 10, "name": "SALES"},
                    {"id": 20, "name": "ENGINEERING"}
                ],
                "ip_plan": [
                    {"device": "R1", "interface": "GigabitEthernet0/0.10", "ip": "192.168.10.1", "mask": "255.255.255.0", "gateway": None},
                    {"device": "R1", "interface": "GigabitEthernet0/0.20", "ip": "192.168.20.1", "mask": "255.255.255.0", "gateway": None},
                    {"device": "PC1", "interface": "FastEthernet0", "ip": "192.168.10.10", "mask": "255.255.255.0", "gateway": "192.168.10.1"},
                    {"device": "PC2", "interface": "FastEthernet0", "ip": "192.168.20.10", "mask": "255.255.255.0", "gateway": "192.168.20.1"}
                ],
                "routing": {"protocol": "none", "process_id": None, "area": None},
                "services": {
                    "dhcp": [
                        {"pool_name": "SALES_POOL", "network": "192.168.10.0", "mask": "255.255.255.0", "default_router": "192.168.10.1", "dns_server": "1.1.1.1"},
                        {"pool_name": "ENG_POOL", "network": "192.168.20.0", "mask": "255.255.255.0", "default_router": "192.168.20.1", "dns_server": "1.1.1.1"}
                    ],
                    "nat": None,
                    "acls": []
                }
            })
        )
    ]
    cursor.executemany(
        "INSERT INTO lab_templates (title, description, difficulty, topology_json) VALUES (?, ?, ?, ?)",
        sample_templates
    )


# Project operations
def list_projects() -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, topology_json, created_at, updated_at FROM projects ORDER BY updated_at DESC")
    rows = cursor.fetchall()
    conn.close()
    projects = []
    for r in rows:
        try:
            topo = json.loads(r["topology_json"])
        except Exception:
            topo = {}
        projects.append({
            "id": r["id"],
            "name": r["name"],
            "topology": topo,
            "created_at": r["created_at"],
            "updated_at": r["updated_at"]
        })
    return projects


def get_project(project_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, topology_json, created_at, updated_at FROM projects WHERE id = ?", (project_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    try:
        topo = json.loads(row["topology_json"])
    except Exception:
        topo = {}
    return {
        "id": row["id"],
        "name": row["name"],
        "topology": topo,
        "created_at": row["created_at"],
        "updated_at": row["updated_at"]
    }


def save_project(name: str, topology_dict: Dict[str, Any], project_id: Optional[int] = None) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    topo_json = json.dumps(topology_dict)
    if project_id:
        cursor.execute(
            "UPDATE projects SET name = ?, topology_json = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (name, topo_json, project_id)
        )
        pid = project_id
    else:
        cursor.execute(
            "INSERT INTO projects (name, topology_json) VALUES (?, ?)",
            (name, topo_json)
        )
        pid = cursor.lastrowid
    conn.commit()
    conn.close()
    return pid


def add_message(project_id: Optional[int], role: str, content: str, intent: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (project_id, role, content, intent) VALUES (?, ?, ?, ?)",
        (project_id, role, content, intent)
    )
    conn.commit()
    conn.close()


def get_messages(project_id: int) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, project_id, role, content, intent, created_at FROM messages WHERE project_id = ? ORDER BY id ASC",
        (project_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def log_llm_interaction(prompt: str, response: str, model: str, latency_ms: int, valid_json: bool):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO llm_logs (prompt, response, model, latency_ms, valid_json) VALUES (?, ?, ?, ?, ?)",
        (prompt, response, model, latency_ms, 1 if valid_json else 0)
    )
    conn.commit()
    conn.close()


def save_generation(project_id: Optional[int], ptbuilder_script: str, cli_configs: Dict[str, str]):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO generations (project_id, ptbuilder_script, cli_configs_json) VALUES (?, ?, ?)",
        (project_id, ptbuilder_script, json.dumps(cli_configs))
    )
    conn.commit()
    conn.close()
