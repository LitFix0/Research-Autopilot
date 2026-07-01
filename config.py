import os
from dotenv import load_dotenv

load_dotenv()

# ── API Keys ──────────────────────────────────────────────
GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# ── Model (free on Groq) ──────────────────────────────────
# Options: "llama-3.3-70b-versatile" | "mixtral-8x7b-32768" | "gemma2-9b-it"
GROQ_MODEL = "llama-3.3-70b-versatile"

# ── Agent behaviour ───────────────────────────────────────
MAX_SEARCH_RESULTS  = 5
NUM_SEARCHER_AGENTS = 3
MAX_RETRY_LOOPS     = 2

# ── Memory ────────────────────────────────────────────────
DB_PATH = "research_memory.db"

# ── Output ────────────────────────────────────────────────
OUTPUT_DIR = "reports"

# ── Validation ────────────────────────────────────────────
def validate():
    missing = []
    if not GROQ_API_KEY:
        missing.append("GROQ_API_KEY")
    if not TAVILY_API_KEY:
        missing.append("TAVILY_API_KEY")
    if missing:
        raise EnvironmentError(
            f"Missing environment variables: {', '.join(missing)}\n"
            "Create a .env file with these keys."
        )

if __name__ == "__main__":
    validate()
    print("Config OK")
    print(f"  Model  : {GROQ_MODEL}")
    print(f"  DB     : {DB_PATH}")
    print(f"  Output : {OUTPUT_DIR}/")