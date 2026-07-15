import subprocess
import sys
import os
import time
import signal
import threading

# ── Paths ──────────────────────────────────────────────
ROOT     = os.path.dirname(os.path.abspath(__file__))
FRONTEND = os.path.join(ROOT, "frontend")

# ── Colours ────────────────────────────────────────────
CYAN   = "\033[96m"
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

processes = []

def log(color, tag, msg):
    print(f"{color}{BOLD}[{tag}]{RESET} {msg}")

def stream(proc, color, tag):
    def _read():
        for line in proc.stdout:
            line = line.rstrip()
            if line:
                print(f"{color}[{tag}]{RESET} {line}")
    threading.Thread(target=_read, daemon=True).start()

def shutdown(sig=None, frame=None):
    print(f"\n{YELLOW}{BOLD}[START] Shutting down both services...{RESET}")
    for p in processes:
        try:
            p.terminate()
        except Exception:
            pass
    sys.exit(0)

def start_backend():
    log(CYAN, "BACKEND ", f"Starting FastAPI  →  http://localhost:8000")
    p = subprocess.Popen(
        [sys.executable, "api.py"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    processes.append(p)
    stream(p, CYAN, "BACKEND ")
    return p

def start_frontend():
    log(GREEN, "FRONTEND", f"Starting React    →  http://localhost:3000")
    npm = "npm.cmd" if sys.platform == "win32" else "npm"
    p = subprocess.Popen(
        [npm, "start"],
        cwd=FRONTEND,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env={**os.environ},
    )
    processes.append(p)
    stream(p, GREEN, "FRONTEND")
    return p

if __name__ == "__main__":
    print(f"""
{CYAN}{BOLD}╔══════════════════════════════════════════════╗
║          RESEARCH AUTOPILOT  v1.0            ║
║            Starting all services…            ║
╚══════════════════════════════════════════════╝{RESET}
""")

    signal.signal(signal.SIGINT,  shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    backend  = start_backend()
    time.sleep(2)          # let backend bind port first
    frontend = start_frontend()

    print()
    log(YELLOW, "START", "Both services running. Press Ctrl+C to stop.")
    log(YELLOW, "START", "Open http://localhost:3000 in your browser.\n")

    # Keep alive + auto-restart backend on crash
    while True:
        time.sleep(3)
        if backend.poll() is not None:
            log(RED, "BACKEND ", "Crashed — restarting...")
            backend = start_backend()
        if frontend.poll() is not None:
            log(RED, "FRONTEND", "Exited.")
            shutdown()