import os
import sys
import subprocess
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
PYTHON_EXE = sys.executable

def run_script(script_name, args=None):
    cmd = [PYTHON_EXE, str(BACKEND_DIR / "scripts" / script_name)]
    if args:
        cmd.extend(args)
    print(f"\n==========================================")
    print(f"Running: {' '.join(cmd)}")
    print(f"==========================================")
    res = subprocess.run(cmd, cwd=str(BACKEND_DIR))
    if res.returncode != 0:
        print(f"FAILED: {script_name}")
        sys.exit(res.returncode)

def main():
    print("--> Starting Full Data & ML Pipeline Refresh...")
    run_script("seed_demo_data.py")
    run_script("ingest_official_data.py", ["--source", "all"])
    run_script("build_features.py")
    run_script("train_models.py")
    print("\n--> Full Data & ML Pipeline Refresh Completed Successfully!")

if __name__ == "__main__":
    main()
