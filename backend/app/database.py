import sqlite3
import os
from typing import Generator
from app.config import settings

def get_db_path() -> str:
    db_path = settings.DB_PATH
    db_dir = os.path.dirname(os.path.abspath(db_path))
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    return db_path

_initialized = False

def init_db():
    global _initialized
    conn = sqlite3.connect(get_db_path(), check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    schema_file = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_file, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()
    _initialized = True

def get_connection() -> sqlite3.Connection:
    global _initialized
    if not _initialized:
        init_db()
    conn = sqlite3.connect(get_db_path(), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
