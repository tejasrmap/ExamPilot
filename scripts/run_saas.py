"""
ExamPilot 2.0 — SaaS Development Server Launcher
Starts both FastAPI backend (port 8000) and Next.js frontend (port 3000).
GT InnoX LLP
"""

import subprocess
import sys
import time
import os

def run_services():
    print("==================================================")
    print("   ExamPilot 2.0 — Online SaaS Development Server")
    print("   Company: GT InnoX LLP")
    print("   Tagline: Understand Questions. Learn the Answers.")
    print("==================================================")

    # 1. Start FastAPI backend
    print("\n[1/2] Starting FastAPI backend on http://127.0.0.1:8000 ...")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload"],
        cwd=os.getcwd()
    )

    # 2. Start Next.js frontend
    print("\n[2/2] Starting Next.js App Router frontend on http://localhost:3000 ...")
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    frontend_proc = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=frontend_dir
    )

    print("\n✓ Both services are launching:")
    print("   • Web Frontend: http://localhost:3000")
    print("   • Backend API Docs: http://127.0.0.1:8000/api/docs")
    print("   • Press Ctrl+C in this terminal to gracefully shut down.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down ExamPilot 2.0 servers...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Shutdown complete.")

if __name__ == "__main__":
    run_services()

