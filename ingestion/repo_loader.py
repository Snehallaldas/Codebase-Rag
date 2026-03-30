# ingestion/repo_loader.py
import os
import shutil
import tempfile
import zipfile
from git import Repo

def load_from_github(url: str, target_dir: str) -> str:
    """
    Clones a public GitHub repo into target_dir.
    Returns the path to the cloned repo root.
    """
    repo_name = url.rstrip("/").split("/")[-1].replace(".git", "")
    clone_path = os.path.join(target_dir, repo_name)

    if os.path.exists(clone_path):
        shutil.rmtree(clone_path)  # always fresh clone

    Repo.clone_from(url, clone_path, depth=1)  # depth=1 = shallow, faster
    return clone_path


def load_from_zip(zip_path: str, target_dir: str) -> str:
    """
    Extracts a zip file into target_dir.
    Returns the path to the extracted root folder.
    """
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(target_dir)

    # zip files often have a single top-level folder — find it
    entries = os.listdir(target_dir)
    if len(entries) == 1 and os.path.isdir(os.path.join(target_dir, entries[0])):
        return os.path.join(target_dir, entries[0])
    return target_dir


def collect_python_files(repo_path: str) -> list[str]:
    """
    Walks the repo and returns all .py file paths.
    Skips common noise: __pycache__, .git, migrations, tests (optional).
    """
    skip_dirs = {"__pycache__", ".git", "migrations", "node_modules", ".venv", "venv"}
    py_files = []

    for root, dirs, files in os.walk(repo_path):
        # prune skip dirs in-place so os.walk doesn't descend into them
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))

    return py_files