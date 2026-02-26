import os

# --- CONFIGURATION ---
# Files we still need to see for a 100% architectural review
REMAINING_SCAFFOLDING = [
    "src/alembic/env.py",
    "src/alembic/versions/8839c3bb117f_initial_clean_baseline.py",
    "scripts/ops/run.sh",
    "scripts/ops/ready.sh",
    "scripts/ops/dev.sh",
    "src/app/models/__init__.py",
    "src/app/api/routes/__init__.py",
    "Taskfile.yml",
    "pyproject.toml"
]

OUTPUT_FILE = "remaining_payload.txt"

def bundle_remaining():
    payloads = []
    
    for f_path in REMAINING_SCAFFOLDING:
        if os.path.exists(f_path):
            try:
                with open(f_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    payloads.append((f_path, content))
            except Exception as e:
                payloads.append((f_path, f"# Error reading: {e}"))
        else:
            print(f"⚠️ Skipping (not found): {f_path}")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
        out.write("🏁 FINAL REMAINING PIECES FOR REVIEW\n")
        out.write("="*50 + "\n\n")

        for i, (path, content) in enumerate(payloads):
            line_count = content.count('\n')
            # Check for shell vs python for markdown highlighting
            lang = "bash" if path.endswith(".sh") or "Taskfile" in path else "python"
            if path.endswith(".toml"): lang = "toml"
            
            out.write(f"--- REMAINING BATCH {i+1} | {path} ---\n")
            out.write(f"### FILE: {path}\n")
            out.write(f"```{lang}\n{content}\n```\n")
            out.write("\n" + "="*50 + "\n\n")

    print(f"✨ Success! {len(payloads)} structural files bundled into {OUTPUT_FILE}")

if __name__ == "__main__":
    bundle_remaining()