import sys
import os
from pathlib import Path
from dulwich import porcelain

ROOT_DIR = Path(__file__).resolve().parents[2]
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
    print(f"--> Commit note: {e}")

# Push to remote
print(f"--> Pushing to remote {REMOTE_URL}...")
try:
    porcelain.push(str(ROOT_DIR), REMOTE_URL, refspecs=b"HEAD:refs/heads/main")
    print("--> Pushed to remote successfully!")
except Exception as e:
    print(f"--> Push notification: {e}")
