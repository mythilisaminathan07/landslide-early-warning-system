import os
import re
from datetime import datetime, timezone

# Root directory of the repository
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_FILE = os.path.join(ROOT_DIR, "PROJECT_CODE_COMPLETE.md")

# Explicit ordered list of source files to include
INCLUDED_FILES = [
    # Gateway & Backend
    "serial_bridge.py",
    "backend/main.py",
    "backend/csv_reader.py",
    "backend/risk_engine.py",
    "backend/sensor_data.py",
    "backend/locations.py",
    "backend/weather_service.py",
    "backend/weather_risk.py",
    "backend/ml/model.py",
    "backend/test_phase2.py",
    "backend/test_weather.py",
    "backend/test_weather_risk.py",
    "backend/requirements.txt",
    "backend/.env.example",

    # Frontend Config & Core
    "frontend/index.html",
    "frontend/package.json",
    "frontend/vite.config.js",
    "frontend/.oxlintrc.json",
    "frontend/src/main.jsx",
    "frontend/src/App.jsx",
    "frontend/src/App.css",
    "frontend/src/index.css",

    # Frontend Components
    "frontend/src/components/Header.jsx",
    "frontend/src/components/LiveTelemetry.jsx",
    "frontend/src/components/Sidebar.jsx",

    # Frontend Pages
    "frontend/src/pages/Dashboard.jsx",
    "frontend/src/pages/Sensors.jsx",
    "frontend/src/pages/Alerts.jsx",
    "frontend/src/pages/History.jsx",
    "frontend/src/pages/GIS.jsx",
    "frontend/src/pages/MLPrediction.jsx",
]

def get_language_tag(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    mapping = {
        ".py": "python",
        ".jsx": "jsx",
        ".js": "javascript",
        ".css": "css",
        ".json": "json",
        ".html": "html",
        ".ino": "cpp",
        ".cpp": "cpp",
        ".h": "cpp",
        ".txt": "text",
        ".example": "text",
    }
    return mapping.get(ext, "text")

def count_lines(text):
    if not text:
        return 0
    return text.count("\n") + (1 if not text.endswith("\n") else 0)

def find_longest_backtick_sequence(text):
    matches = re.findall(r"`+", text)
    if not matches:
        return 0
    return max(len(m) for m in matches)

def scan_files_not_included(root_dir, included_rel_paths):
    excluded_info = []
    # Directories completely ignored
    ignored_dirs = {"node_modules", "venv", ".venv", "__pycache__", "dist", "build", ".git", ".gemini", ".vscode"}
    
    for root, dirs, files in os.walk(root_dir):
        # Modify dirs in-place to prune ignored directories
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, root_dir).replace("\\", "/")
            
            # Skip output bundle and generator script
            if rel_path in ["PROJECT_CODE_COMPLETE.md", "tools/make_code_bundle.py"]:
                continue
            
            if rel_path not in included_rel_paths:
                size_bytes = os.path.getsize(full_path)
                category = "Unknown"
                if rel_path.endswith(".csv"):
                    category = "Sensor Data CSV"
                elif rel_path.endswith((".tif", ".tiff")):
                    category = "GIS Raster Data"
                elif rel_path.endswith((".pkl", ".joblib")):
                    category = "Trained ML Model Binary"
                elif rel_path.endswith(".pdf"):
                    category = "PDF Documentation"
                elif rel_path.endswith((".png", ".jpg", ".jpeg", ".svg")):
                    category = "Image Asset"
                elif rel_path == "backend/.env":
                    category = "Local Environment File (Excluded for security)"
                elif rel_path.endswith("package-lock.json"):
                    category = "Package Lock File"
                elif rel_path.startswith("documentation/"):
                    category = "Project Documentation"
                elif rel_path.endswith(".md"):
                    category = "Markdown Documentation"
                elif rel_path.endswith(".gitignore"):
                    category = "Git Ignore File"
                
                excluded_info.append((rel_path, size_bytes, category))
                
    excluded_info.sort(key=lambda x: x[0])
    return excluded_info

def build_bundle():
    print(f"Reading {len(INCLUDED_FILES)} files from repository...")
    file_data = {}
    
    # 1. Read all files verbatim
    for rel_path in INCLUDED_FILES:
        full_path = os.path.join(ROOT_DIR, rel_path)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Required file missing: {full_path}")
        
        with open(full_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        
        lines = count_lines(content)
        longest_ticks = find_longest_backtick_sequence(content)
        # Use backtick fence that is strictly longer than any backtick inside the file, minimum 4
        fence_len = max(longest_ticks + 1, 4)
        fence = "`" * fence_len
        lang = get_language_tag(rel_path)
        
        file_data[rel_path] = {
            "content": content,
            "lines": lines,
            "fence": fence,
            "lang": lang,
        }

    # 2. Build Markdown content
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    out = []
    out.append("# GeoRisk / SlopeGuard AI - Complete Source Code Bundle\n\n")
    out.append(f"> **Generated:** {now_str}\n")
    out.append(f"> **Total Source Files Included:** {len(INCLUDED_FILES)}\n")
    out.append("> **Note:** All source code and configurations are copied verbatim without modifications.\n\n")
    
    out.append("---\n\n")
    out.append("## Table of Contents\n\n")
    out.append("| # | File Path | Type | Line Count |\n")
    out.append("|---|-----------|------|------------|\n")
    
    for idx, rel_path in enumerate(INCLUDED_FILES, 1):
        info = file_data[rel_path]
        out.append(f"| {idx} | [`{rel_path}`](#{rel_path.replace('/', '').replace('.', '').replace('-', '').lower()}) | `{info['lang']}` | {info['lines']} |\n")
    
    out.append("\n---\n\n")
    
    # 3. Add each file content
    for rel_path in INCLUDED_FILES:
        info = file_data[rel_path]
        out.append(f"## `{rel_path}`\n\n")
        out.append(f"{info['fence']}{info['lang']}\n")
        out.append(info['content'])
        if not info['content'].endswith("\n"):
            out.append("\n")
        out.append(f"{info['fence']}\n\n")
        out.append("---\n\n")
        
    # 4. Add Files Not Included section
    excluded_files = scan_files_not_included(ROOT_DIR, set(INCLUDED_FILES))
    out.append("## Files Not Included\n\n")
    out.append("The following data, binary, documentation, and lock files were excluded from the source code bundle in accordance with specifications:\n\n")
    out.append("| File Path | Size (Bytes) | Category / Reason |\n")
    out.append("|-----------|--------------|-------------------|\n")
    for rel_path, size_bytes, category in excluded_files:
        out.append(f"| `{rel_path}` | {size_bytes:,} | {category} |\n")
    out.append("\n")

    bundle_text = "".join(out)
    
    # Write to output file
    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="\n") as f:
        f.write(bundle_text)
        
    print(f"Bundle generated: {OUTPUT_FILE}")
    return file_data, bundle_text

def verify_bundle(file_data, bundle_text):
    print("\n" + "=" * 80)
    print("VERIFICATION OF BUNDLE INTEGRITY")
    print("=" * 80)
    
    # 1. Byte-for-byte check of every file inside bundle
    verified_count = 0
    diff_count = 0
    
    for rel_path in INCLUDED_FILES:
        orig = file_data[rel_path]["content"]
        fence = file_data[rel_path]["fence"]
        lang = file_data[rel_path]["lang"]
        
        # Look for exact block
        expected_block = f"## `{rel_path}`\n\n{fence}{lang}\n{orig}"
        if not orig.endswith("\n"):
            expected_block += "\n"
        expected_block += f"{fence}\n"
        
        if expected_block in bundle_text:
            verified_count += 1
        else:
            diff_count += 1
            print(f"MISMATCH in file: {rel_path}")

    print(f"Verification Result: {len(INCLUDED_FILES)} files included, {verified_count} verified identical, {diff_count} differences")
    assert diff_count == 0, f"Verification failed with {diff_count} differences!"

    # 2. Total Line Count & File Table
    total_lines = count_lines(bundle_text)
    print(f"\nTotal Line Count of PROJECT_CODE_COMPLETE.md: {total_lines:,} lines")
    print(f"File Size: {os.path.getsize(OUTPUT_FILE):,} bytes ({round(os.path.getsize(OUTPUT_FILE) / 1024, 2)} KB)\n")
    
    print("Included Files & Line Counts:")
    for rel_path in INCLUDED_FILES:
        print(f"  • {rel_path:<40} : {file_data[rel_path]['lines']} lines")
        
    # 3. Security & Secret Scanning
    print("\n" + "=" * 80)
    print("SEARCH FOR SECRETS IN BUNDLE")
    print("=" * 80)
    secret_terms = ["API_KEY", "SECRET", "PASSWORD", "TOKEN", "mongodb+srv"]
    
    found_secrets = []
    lines = bundle_text.splitlines()
    for line_no, line in enumerate(lines, 1):
        for term in secret_terms:
            if term.lower() in line.lower():
                found_secrets.append((line_no, term, line.strip()))
                
    if found_secrets:
        print(f"Found {len(found_secrets)} occurrences of searched keywords:")
        for line_no, term, line in found_secrets:
            print(f"  Line {line_no} [{term}]: {line}")
    else:
        print("No occurrences of secret keywords found.")

if __name__ == "__main__":
    file_data, bundle_text = build_bundle()
    verify_bundle(file_data, bundle_text)
