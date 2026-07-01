import sqlite3
import json
from datetime import datetime
from config import DB_PATH


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
    print(f"[memory] DB initialised at '{DB_PATH}'")


# ── Sessions ──────────────────────────────────────────────

def create_session(query: str) -> int:
    """Start a new research session, return its id."""
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO research_sessions (query) VALUES (?)", (query,)
        )
        return cur.lastrowid


def close_session(session_id: int):
    """Mark a session as complete."""
    with get_connection() as conn:
        conn.execute(
            "UPDATE research_sessions SET status='done', finished_at=datetime('now') WHERE id=?",
            (session_id,)
        )


# ── Agent outputs ─────────────────────────────────────────

def save_agent_output(session_id: int, agent_name: str, output: str):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO agent_outputs (session_id, agent_name, output) VALUES (?,?,?)",
            (session_id, agent_name, output)
        )


def get_agent_outputs(session_id: int) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT agent_name, output, created_at FROM agent_outputs WHERE session_id=? ORDER BY id",
            (session_id,)
        ).fetchall()
    return [dict(r) for r in rows]


# ── Search results ────────────────────────────────────────

def save_search_results(session_id: int, sub_query: str, results: list):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO search_results (session_id, sub_query, results) VALUES (?,?,?)",
            (session_id, sub_query, json.dumps(results))
        )


def get_search_results(session_id: int) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT sub_query, results FROM search_results WHERE session_id=? ORDER BY id",
            (session_id,)
        ).fetchall()
    return [{"sub_query": r["sub_query"], "results": json.loads(r["results"])} for r in rows]


# ── History ───────────────────────────────────────────────

def get_recent_sessions(limit: int = 5) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, query, status, created_at FROM research_sessions ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


if __name__ == "__main__":
    init_db()
    sid = create_session("Test query: what is CrewAI?")
    save_agent_output(sid, "planner", "Sub-tasks: [1] What is CrewAI [2] How does it work")
    save_search_results(sid, "What is CrewAI", [{"url": "example.com", "content": "CrewAI is..."}])
    close_session(sid)
    print("[memory] Session test passed")
    print("[memory] Recent sessions:", get_recent_sessions())