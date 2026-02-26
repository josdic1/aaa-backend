import os

# --- CONFIGURATION ---
# The specific "trail" order you want me to follow
CORE_TRAIL = [
    "src/app/main.py",
    "src/app/database.py",
    "src/app/core/config.py",
]

# Folders to prioritize in order
TARGET_DIRS = [
    "src/app/models",
    "src/app/schemas",
    "src/app/api/deps",
    "src/app/api/routes",
]

# Strictly ignore these
SKIP_DIRS = {".venv", "venv", "__pycache__", ".git", "aaa_backend.egg-info", "node_modules"}
OUTPUT_FILE = "project_payload.txt"

def get_file_content(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"# Error reading file: {e}"

def bundle():
    processed_files = set()
    payloads = []

    # 1. Process Core Trail First
    for f_path in CORE_TRAIL:
        if os.path.exists(f_path):
            payloads.append((f_path, get_file_content(f_path)))
            processed_files.add(os.path.abspath(f_path))

    # 2. Process Target Directories
    for root_dir in TARGET_DIRS:
        if not os.path.exists(root_dir):
            continue
        for root, dirs, files in os.walk(root_dir):
            # Prune skip_dirs in-place
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            
            for file in sorted(files):
                if file.endswith(".py") and file != "__init__.py":
                    full_path = os.path.join(root, file)
                    abs_path = os.path.abspath(full_path)
                    
                    if abs_path not in processed_files:
                        payloads.append((full_path, get_file_content(full_path)))
                        processed_files.add(abs_path)

    # 3. Write to the output file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
        out.write("🚀 PROJECT BUNDLE FOR REVIEW\n")
        out.write("="*50 + "\n\n")

        for i, (path, content) in enumerate(payloads):
            line_count = content.count('\n')
            warning = "⚠️ LARGE FILE - PASTE WITH CARE" if line_count > 250 else "✅ OPTIMAL SIZE"
            
            out.write(f"--- BATCH {i+1} | {path} ---\n")
            out.write(f"STATAUS: {warning} ({line_count} lines)\n")
            out.write(f"### FILE: {path}\n")
            out.write(f"```python\n{content}\n```\n")
            out.write("\n" + "="*50 + "\n\n")

    print(f"✨ Success! {len(payloads)} files bundled into {OUTPUT_FILE}")
    print(f"📂 Open {OUTPUT_FILE} and copy one BATCH at a time.")

if __name__ == "__main__":
    bundle()