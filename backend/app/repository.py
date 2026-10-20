import json
import sqlite3
from typing import List, Optional, Dict, Any
from app.database import get_connection

def create_project(name: str, topology_json: str) -> Dict[str, Any]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO projects (name, topology_json, created_at, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
        (name, topology_json)
    )
    conn.commit()
    project_id = cursor.lastrowid
    cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row)

def get_projects() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects ORDER BY updated_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_project(project_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def update_project(project_id: int, name: Optional[str] = None, topology_json: Optional[str] = None) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    if name and topology_json:
        cursor.execute(
            "UPDATE projects SET name = ?, topology_json = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (name, topology_json, project_id)
        )
    elif name:
        cursor.execute(
            "UPDATE projects SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (name, project_id)
        )
    elif topology_json:
        cursor.execute(
            "UPDATE projects SET topology_json = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (topology_json, project_id)
        )
    conn.commit()
    cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def delete_project(project_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

def save_message(project_id: Optional[int], role: str, content: str, intent: Optional[str] = None) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (project_id, role, content, intent, created_at) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
        (project_id, role, content, intent)
    )
    conn.commit()
    msg_id = cursor.lastrowid
    conn.close()
    return msg_id

def get_messages(project_id: int) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages WHERE project_id = ? ORDER BY created_at ASC", (project_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_generation(project_id: Optional[int], ptbuilder_script: str, cli_configs_json: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO generations (project_id, ptbuilder_script, cli_configs_json, created_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
        (project_id, ptbuilder_script, cli_configs_json)
    )
    conn.commit()
    gen_id = cursor.lastrowid
    conn.close()
    return gen_id

def save_llm_log(prompt: str, response: str, model: str, latency_ms: int, valid_json: bool = False) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO llm_logs (prompt, response, model, latency_ms, valid_json, created_at) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
        (prompt, response, model, latency_ms, 1 if valid_json else 0)
    )
    conn.commit()
    log_id = cursor.lastrowid
    conn.close()
    return log_id

def get_lab_templates() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lab_templates ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_lab_template(title: str, description: str, difficulty: str, topology_json: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO lab_templates (title, description, difficulty, topology_json) VALUES (?, ?, ?, ?)",
        (title, description, difficulty, topology_json)
    )
    conn.commit()
    tpl_id = cursor.lastrowid
    conn.close()
    return tpl_id
