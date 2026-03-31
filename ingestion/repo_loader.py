# ingestion/repo_loader.py
import os
import shutil
import tempfile
import zipfile
import git

def load_from_github(url: str, target_dir: str) -> str:
    repo_name = url.rstrip("/").split("/")[-1].replace(".git", "")
    clone_path = os.path.join(target_dir, repo_name)
    if os.path.exists(clone_path):
        shutil.rmtree(clone_path)
    git.Repo.clone_from(url, clone_path, depth=1)
    return clone_path

def load_from_zip(zip_path: str, target_dir: str) -> str:
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(target_dir)
    entries = os.listdir(target_dir)
    if len(entries) == 1 and os.path.isdir(os.path.join(target_dir, entries[0])):
        return os.path.join(target_dir, entries[0])
    return target_dir

def collect_python_files(repo_path: str) -> list[str]:
    skip_dirs = {"__pycache__", ".git", "migrations", "node_modules", ".venv", "venv"}
    py_files = []
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))
    return py_files

def collect_supported_files(repo_path: str) -> dict:
    """
    Returns dict of language -> list of file paths.
    Supports Python and JavaScript/TypeScript.
    """
    skip_dirs = {
        "__pycache__", ".git", "migrations", "node_modules",
        ".venv", "venv", "dist", "build", "coverage", ".next"
    }
    files = {
        "python":     [],
        "javascript": [],
        "html":       [],
        "json":       [],
        "markdown":   [],
    }

    for root, dirs, filenames in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in filenames:
            full_path = os.path.join(root, f)
            if f.endswith(".py"):
                files["python"].append(full_path)
            elif f.endswith((".js", ".ts", ".jsx", ".tsx")):
                files["javascript"].append(full_path)

    return files