import os
import sys
import subprocess
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent
ENV_PATH = ROOT_DIR / ".env"

# 1) Load .env into THIS process
load_dotenv(dotenv_path=ENV_PATH, override=False)


def run_server() -> None:
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8080",
        "--app-dir", "src",
        "--reload",
    ]

    try:
        print("\n🚀 [AAA] Starting server at http://localhost:8080")
        print("📁 [AAA] App directory: src/")

        # 3) Force env vars into the uvicorn process (reloader + server)
        child_env = os.environ.copy()
        subprocess.run(cmd, env=child_env)
    except KeyboardInterrupt:
        print("\n\n👋 [AAA] Shutdown requested. Cleaning up...")
        sys.exit(0)

if __name__ == "__main__":
    run_server()