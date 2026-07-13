import sys
import os
import json
import asyncio
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# ── Monkey-patch litellm before anything imports it ────
def _patch_litellm():
    try:
        import litellm
        _original = litellm.completion
        def _patched(*args, **kwargs):
            for msg in kwargs.get("messages", []):
                if isinstance(msg, dict) and "cache_breakpoint" in msg:
                    del msg["cache_breakpoint"]
            return _original(*args, **kwargs)
        litellm.completion = _patched
    except ImportError:
        pass

_patch_litellm()

from core.config import validate
from core.memory import (
    init_db, get_recent_sessions, create_session,
    close_session, save_agent_output, get_agent_outputs,
    get_search_results
)

# ── App setup ──────────────────────────────────────────
app = FastAPI(title="Research Autopilot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

validate()
init_db()


# ── Request models ─────────────────────────────────────
class ResearchRequest(BaseModel):
    query: str


# ── GET /api/sessions ──────────────────────────────────
@app.get("/api/sessions")
def get_sessions():
    return get_recent_sessions(limit=20)


# ── DELETE /api/sessions/{id} ──────────────────────────
@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: int):
    from core.memory import get_connection
    with get_connection() as conn:
        conn.execute("DELETE FROM agent_outputs  WHERE session_id=?", (session_id,))
        conn.execute("DELETE FROM search_results WHERE session_id=?", (session_id,))
        conn.execute("DELETE FROM research_sessions WHERE id=?",      (session_id,))
    return {"deleted": session_id}


# ── GET /api/sessions/{id}/report ─────────────────────
@app.get("/api/sessions/{session_id}/report")
def get_report(session_id: int):
    from core.config import OUTPUT_DIR
    from core.memory import get_connection
    with get_connection() as conn:
        row = conn.execute(
            "SELECT query FROM research_sessions WHERE id=?", (session_id,)
        ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Session not found")

    query = row["query"]
    safe  = "".join(c if c.isalnum() or c in " _-" else "_" for c in query)[:50]
    path  = os.path.join(OUTPUT_DIR, f"{safe}.md")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Report file not found")

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    return {"session_id": session_id, "query": query, "content": content}


# ── POST /api/research  (SSE stream) ──────────────────
@app.post("/api/research")
async def run_research(req: ResearchRequest):
    """
    Streams pipeline progress as Server-Sent Events.
    Each event is a JSON object: { type, message, data? }
    """
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    async def event_stream():
        def send(type_, message, data=None):
            payload = {"type": type_, "message": message}
            if data:
                payload["data"] = data
            return f"data: {json.dumps(payload)}\n\n"

        yield send("start", "Pipeline starting…")

        try:
            loop = asyncio.get_event_loop()

            # Run the full pipeline in a thread so we don't block
            def run():
                from core.crew import run_pipeline
                return run_pipeline(req.query)

            yield send("stage", "Planner agent running…", {"stage": "planner"})
            await asyncio.sleep(0.1)

            yield send("stage", "Searcher agents running…", {"stage": "searchers"})
            await asyncio.sleep(0.1)

            yield send("stage", "Synthesizer agent running…", {"stage": "synthesizer"})
            await asyncio.sleep(0.1)

            yield send("stage", "Critic agent validating…", {"stage": "critic"})

            report_path = await loop.run_in_executor(None, run)

            # Read report content
            with open(report_path, "r", encoding="utf-8") as f:
                content = f.read()

            yield send("done", "Research complete!", {
                "report_path": report_path,
                "report_content": content,
                "sessions": get_recent_sessions(limit=20),
            })

        except Exception as e:
            yield send("error", str(e))

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ── GET /api/health ────────────────────────────────────
@app.get("/api/health")
def health():
    return {"status": "ok", "time": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)