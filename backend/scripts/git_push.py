import sys
import os
from pathlib import Path
from dulwich import porcelain

ROOT_DIR = Path(__file__).resolve().parents[2]
TOKEN = os.getenv("GITHUB_TOKEN") or (sys.argv[1] if len(sys.argv) > 1 else None)

if TOKEN:
    REMOTE_URL = f"https://{TOKEN}@github.com/A760-st/manganese_reserve.git"
else:
    REMOTE_URL = "https://github.com/A760-st/manganese_reserve.git"

print(f"--> Target repository path: {ROOT_DIR}")

# Check or initialize git repo
git_dir = ROOT_DIR / ".git"
if not git_dir.exists():
    print("--> Initializing git repository...")
    porcelain.init(str(ROOT_DIR))

# Add all files
print("--> Staging files...")
porcelain.add(str(ROOT_DIR))

# Create commit
commit_msg = b"feat: integrate official mineral and earth observation data sources"
print(f"--> Creating commit: {commit_msg.decode()}")
try:
    commit_id = porcelain.commit(str(ROOT_DIR), message=commit_msg)
    print(f"--> Created commit {commit_id.decode() if isinstance(commit_id, bytes) else commit_id}")
except Exception as e:
    print(f"--> Commit status: {e}")

# Push to remote
print(f"--> Pushing to remote https://github.com/A760-st/manganese_reserve.git...")
try:
    porcelain.push(str(ROOT_DIR), REMOTE_URL, refspecs=b"HEAD:refs/heads/main")
    print("--> Pushed to remote successfully!")
except Exception as e:
    print(f"--> Push result: {e}")
    if not TOKEN:
        print("\n--> NOTE: Remote push requires authentication. Set GITHUB_TOKEN environment variable or run:")
        print("    python scripts/git_push.py YOUR_GITHUB_TOKEN")
