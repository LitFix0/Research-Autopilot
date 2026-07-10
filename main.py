import sys
import os
from datetime import datetime


# ── Monkey-patch: strip cache_breakpoint from messages before Groq sees it ──
def _patch_litellm():
    try:
        import litellm
        _original_completion = litellm.completion

        def _patched_completion(*args, **kwargs):
            messages = kwargs.get("messages", [])
            for msg in messages:
                if isinstance(msg, dict) and "cache_breakpoint" in msg:
                    del msg["cache_breakpoint"]
            kwargs["messages"] = messages
            return _original_completion(*args, **kwargs)

        litellm.completion = _patched_completion
    except ImportError:
        pass

_patch_litellm()
# ────────────────────────────────────────────────────────────────────────────


def print_banner():
    print("""
╔══════════════════════════════════════════════╗
║          RESEARCH AUTOPILOT  v1.0            ║
║   Planner → Searcher × 3 → Synthesizer       ║
║              → Critic → Report               ║
╚══════════════════════════════════════════════╝
    """)


def print_session_history():
    from core.memory import init_db, get_recent_sessions
    init_db()
    sessions = get_recent_sessions(limit=5)
    if not sessions:
        print("  No previous sessions found.\n")
        return
    print("  Recent research sessions:")
    for s in sessions:
        status_icon = "✅" if s["status"] == "done" else "⏳"
        print(f"  {status_icon} [{s['id']}] {s['query'][:60]}  ({s['created_at']})")
    print()


def get_query_from_user() -> str:
    print("─" * 50)
    print("Enter your research query below.")
    print("Type 'history' to see past sessions.")
    print("Type 'quit' to exit.")
    print("─" * 50)

    while True:
        try:
            query = input("\n🔍 Research query: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nExiting. Goodbye!")
            sys.exit(0)

        if not query:
            print("  ⚠  Please enter a query.")
            continue

        if query.lower() == "quit":
            print("Goodbye!")
            sys.exit(0)

        if query.lower() == "history":
            print_session_history()
            continue

        return query


def run():
    # ── Validate config first ─────────────────────────────
    try:
        from core.config import validate
        validate()
    except EnvironmentError as e:
        print(f"\n❌  Config error:\n{e}")
        sys.exit(1)

    print_banner()
    print_session_history()

    while True:
        query = get_query_from_user()

        print(f"\n🚀 Starting research pipeline...")
        print(f"   Query     : {query}")
        print(f"   Started at: {datetime.now().strftime('%H:%M:%S')}\n")

        try:
            from core.crew import run_pipeline
            start = datetime.now()
            report_path = run_pipeline(query)
            elapsed = (datetime.now() - start).seconds

            print("\n" + "═" * 50)
            print(f"✅  Research complete in {elapsed}s")
            print(f"📄  Report saved to: {report_path}")
            print("═" * 50)

            # Preview first 20 lines of the report
            try:
                with open(report_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()[:20]
                print("\n── Report preview ──────────────────────────\n")
                print("".join(lines))
                if len(lines) == 20:
                    print(f"... (open {report_path} for the full report)")
            except Exception:
                pass

        except KeyboardInterrupt:
            print("\n\n⚠  Pipeline interrupted by user.")

        except Exception as e:
            print(f"\n❌  Pipeline error: {e}")
            import traceback
            traceback.print_exc()

        print("\n" + "─" * 50)
        try:
            again = input("Run another query? (y/n): ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            again = "n"

        if again != "y":
            print("\nGoodbye! Your reports are saved in the reports/ folder.")
            break


if __name__ == "__main__":
    run()