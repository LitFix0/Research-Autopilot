<div align="center">

# 🔬 Research Autopilot

### Multi-Agent AI Research Pipeline

*Enter a topic. Get a fully cited research report in ~30 seconds.*

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)
![CrewAI](https://img.shields.io/badge/CrewAI-1.14.7-6366f1?style=flat-square)
![React](https://img.shields.io/badge/React-18-61dafb?style=flat-square&logo=react)
![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688?style=flat-square&logo=fastapi)
![Cost](https://img.shields.io/badge/Monthly%20Cost-%240-10b981?style=flat-square)

</div>

---

## What is this?

Research Autopilot is a fully automated multi-agent AI system that takes a natural language research query and produces a structured, cited markdown report — end to end, without human intervention.

**One query in → full research report out.**

```
User: "What are the latest developments in fusion energy?"

Pipeline:
  Planner      → breaks into 3 focused sub-questions
  Searcher ×3  → searches the web in parallel (live Tavily results)
  Synthesizer  → merges findings into a markdown report
  Critic       → validates quality, sends back for revision if needed

Output: reports/fusion-energy.md  ✅
```

---

## Demo

```
╔══════════════════════════════════════════════╗
║          RESEARCH AUTOPILOT  v1.0            ║
║   Planner → Searcher × 3 → Synthesizer       ║
║              → Critic → Report               ║
╚══════════════════════════════════════════════╝

🔍 Research query: What is quantum computing and its latest developments

🚀 Starting research pipeline...
   Started at: 19:58:56

[crew] Pipeline run 1/2
[crew] Sub-questions: ['What are the core principles...', 'What recent hardware...', 'What are the applications...']
[crew] Critic approved the report.
[crew] Report saved to: reports\quantum-computing.md

✅  Research complete in 27s
```

---

## Tech Stack

| Layer | Tool | Cost |
|---|---|---|
| LLM | Groq API — `llama-3.3-70b-versatile` | Free |
| Agent framework | CrewAI | Free |
| LLM bridge | LiteLLM | Free |
| Web search | Tavily API | Free (1000/month) |
| Backend | FastAPI + Uvicorn | Free |
| Frontend | React 18 | Free |
| Memory | SQLite | Free (built-in) |
| Runtime | Python 3.12 | Free |

**Total monthly cost: $0**

---

## Project Structure

```
Research Autopilot/
├── start.py              ← single command to launch everything
├── main.py               ← CLI fallback (no frontend needed)
├── api.py                ← FastAPI backend (REST + SSE)
│
├── core/
│   ├── __init__.py
│   ├── config.py         ← API keys, model, constants
│   ├── memory.py         ← SQLite operations
│   ├── agents.py         ← Planner, Searcher ×3, Synthesizer, Critic
│   ├── tools.py          ← Tavily search tool
│   └── crew.py           ← Pipeline orchestration + retry loop
│
├── frontend/
│   └── src/
│       └── App.jsx       ← React dashboard
│
├── reports/              ← generated at runtime
├── research_memory.db    ← generated at runtime
├── .env                  ← your API keys (never commit this)
└── .gitignore
```

---

## Quick Start

### 1. Prerequisites

- Python **3.12** (not 3.13 or 3.14 — CrewAI doesn't support them yet)
- Node.js 18+ and npm
- Free API keys from:
  - [console.groq.com](https://console.groq.com) → Create API key
  - [tavily.com](https://tavily.com) → Get API key

### 2. Clone & Install

```powershell
# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux

# Install Python dependencies
pip install crewai crewai-tools tavily-python groq litellm python-dotenv fastapi uvicorn

# Install React dependencies
cd frontend
npm install
cd ..
```

### 3. Configure API Keys

Create a `.env` file in the project root:

```env
GROQ_API_KEY=gsk_...
TAVILY_API_KEY=tvly-...
```

### 4. Run

```powershell
python start.py
```

This launches both the FastAPI backend (`localhost:8000`) and React frontend (`localhost:3000`) with a single command. Your browser opens automatically.

---

## Pipeline Architecture

```
User Query
    │
    ▼
┌─────────────────┐
│  Planner Agent  │  Breaks query into 3 focused sub-questions
└────────┬────────┘
         │
    ┌────┴────┐
    ▼    ▼    ▼
┌──────┐ ┌──────┐ ┌──────┐
│ S1   │ │ S2   │ │ S3   │  Searcher agents — parallel Tavily search
└──────┘ └──────┘ └──────┘
    │         │        │
    └────┬────┘────────┘
         ▼
┌──────────────────┐
│  Synthesizer     │  Merges all findings into markdown report
└────────┬─────────┘
         ▼
┌──────────────────┐
│  Critic Agent    │  Validates quality — approves or sends back
└────────┬─────────┘
         │
    ┌────┴──────────┐
    │  approved?    │
    └──┬────────────┘
       │ yes              no → retry (max 2 loops)
       ▼
  reports/*.md  ✅
```

---

## Dashboard

The React dashboard runs at `http://localhost:3000` and includes:

- **Dashboard** — metrics, session table with pipeline stage dots, agent activity log
- **New Research** — live pipeline progress bar, scrolling log, report preview
- **Session History** — all past runs with individual delete buttons
- **Reports** — approved reports with full content viewer

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check |
| `GET` | `/api/sessions` | List recent sessions |
| `DELETE` | `/api/sessions/{id}` | Delete a session |
| `GET` | `/api/sessions/{id}/report` | Fetch report content |
| `POST` | `/api/research` | Run pipeline (SSE stream) |

---

## Configuration

All settings are in `core/config.py`:

```python
GROQ_MODEL          = "llama-3.3-70b-versatile"  # swap model here
MAX_SEARCH_RESULTS  = 5                           # results per Tavily call
NUM_SEARCHER_AGENTS = 3                           # parallel searchers
MAX_RETRY_LOOPS     = 2                           # critic retry limit
```

---

## Known Issues & Fixes

| Bug | Fix |
|---|---|
| `cache_breakpoint` rejected by Groq | Monkey-patched in `main.py` and `api.py` — strips field before request |
| CrewAI rejects `ChatGroq` object | Use CrewAI's native `LLM` class instead |
| Python 3.13/3.14 wheel failures | Use Python 3.12 strictly |
| `litellm` not found | `pip install litellm` explicitly |

---

## CLI Mode (no frontend)

You can also run without the dashboard:

```powershell
python main.py
```

Reports are saved to `reports/` and previewed in the terminal.

---

## Roadmap

- [ ] PDF export of reports
- [ ] Email delivery via SendGrid
- [ ] Real-time agent logs streamed to dashboard
- [ ] Model selector (Llama, Mixtral, Gemma)
- [ ] True parallel search with `asyncio.gather`
- [ ] Scheduled research runs (cron-based)
- [ ] Vector memory with ChromaDB

---

## License

MIT — free to use, modify, and distribute.

---

<div align="center">

Built with ❤️ using Groq · CrewAI · Tavily · FastAPI · React

</div>
