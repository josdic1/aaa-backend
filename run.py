import sys
import subprocess

def run_server() -> None:
    # --app-dir src allows Python to see inside the src/ folder correctly
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
        # We removed check=True so it doesn't scream on exit
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\n👋 [AAA] Shutdown requested. Cleaning up...")
        sys.exit(0)

if __name__ == "__main__":
    run_server()