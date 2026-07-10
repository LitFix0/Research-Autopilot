import sqlite3
import json
from core.config import DB_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables if they don't exist."""
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS research_sessions (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                query       TEXT NOT NULL,
                status      TEXT DEFAULT 'running',
                created_at  TEXT DEFAULT (datetime('now')),
                finished_at TEXT
            );

            CREATE TABLE IF NOT EXISTS agent_outputs (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id  INTEGER NOT NULL,
                agent_name  TEXT NOT NULL,
                output      TEXT NOT NULL,
                created_at  TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (session_id) REFERENCES research_sessions(id)
            );

            CREATE TABLE IF NOT EXISTS search_results (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id  INTEGER NOT NULL,
                sub_query   TEXT NOT NULL,
                results     TEXT NOT NULL,
                created_at  TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (session_id) REFERENCES research_sessions(id)
            );
        """)


def create_session(query: str) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO research_sessions (query) VALUES (?)", (query,)
        )
        return cur.lastrowid


def close_session(session_id: int):
    with get_connection() as conn:
        conn.execute(
            "UPDATE research_sessions SET status='done', finished_at=datetime('now') WHERE id=?",
            (session_id,)
        )


def save_agent_output(session_id: int, agent_name: str, output: str):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO agent_outputs (session_id, agent_name, output) VALUES (?,?,?)",
            (session_id, agent_name, output)
        )


def get_agent_outputs(session_id: int) -> list:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT agent_name, output, created_at FROM agent_outputs WHERE session_id=? ORDER BY id",
            (session_id,)
        ).fetchall()
    return [dict(r) for r in rows]


def save_search_results(session_id: int, sub_query: str, results: list):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO search_results (session_id, sub_query, results) VALUES (?,?,?)",
            (session_id, sub_query, json.dumps(results))
        )


def get_search_results(session_id: int) -> list:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT sub_query, results FROM search_results WHERE session_id=? ORDER BY id",
            (session_id,)
        ).fetchall()
    return [{"sub_query": r["sub_query"], "results": json.loads(r["results"])} for r in rows]


def get_recent_sessions(limit: int = 5) -> list:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, query, status, created_at FROM research_sessions ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [dict(r) for r in rows]