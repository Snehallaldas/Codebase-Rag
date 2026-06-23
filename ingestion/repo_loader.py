# ingestion/repo_loader.py
import os
import shutil
import tempfile
import zipfile
import io
import requests
import git
import urllib.parse

def parse_github_url(url: str) -> tuple[str, str] | None:
    url = url.strip()
    if url.startswith("git@github.com:"):
        path = url.split("git@github.com:")[-1]
        parts = [p for p in path.split("/") if p]
        if len(parts) >= 2:
            owner = parts[0]
            repo = parts[1].replace(".git", "")
            return owner, repo
    else:
        parsed = urllib.parse.urlparse(url)
        if "github.com" in parsed.netloc:
            parts = [p for p in parsed.path.split("/") if p]
            if len(parts) >= 2:
                owner = parts[0]
                repo = parts[1].replace(".git", "")
                return owner, repo
    return None

def load_from_github(url: str, target_dir: str) -> str:
    repo_name = url.rstrip("/").split("/")[-1].replace(".git", "")
    clone_path = os.path.join(target_dir, repo_name)
    if os.path.exists(clone_path):
        shutil.rmtree(clone_path)

    # Try Git clone first
    try:
        git.Repo.clone_from(url, clone_path, depth=1)
        return clone_path
    except Exception as e:
        print(f"Git clone failed or Git is not installed: {e}. Falling back to ZIP download...")

    # Fallback to ZIP download
    parsed_info = parse_github_url(url)
    if not parsed_info:
        raise ValueError(
            f"Failed to clone using Git, and URL '{url}' is not a valid GitHub repository URL "
            f"for fallback ZIP download."
        )

    owner, repo = parsed_info
    print(f"Downloading ZIP archive for {owner}/{repo}...")

    headers = {"User-Agent": "Codebase-RAG-Ingester"}
    downloaded = False
    zipball_url = f"https://api.github.com/repos/{owner}/{repo}/zipball"

    try:
        response = requests.get(zipball_url, headers=headers, allow_redirects=True, timeout=30)
        if response.status_code == 200:
            with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
                zf.extractall(target_dir)
            downloaded = True
    except Exception as api_err:
        print(f"GitHub API zipball download failed: {api_err}")

    if not downloaded:
        # Fallback to direct archive download links
        for branch in ["main", "master"]:
            archive_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
            try:
                response = requests.get(archive_url, headers=headers, allow_redirects=True, timeout=30)
                if response.status_code == 200:
                    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
                        zf.extractall(target_dir)
                    downloaded = True
                    break
            except Exception as branch_err:
                print(f"Failed to download archive for branch {branch}: {branch_err}")

    if not downloaded:
        raise RuntimeError(
            f"Ingestion failed: Git clone was unavailable/failed, and downloading the ZIP "
            f"archive from GitHub failed as well for {owner}/{repo}."
        )

    # After zip extraction, the repo will be in a subdirectory under target_dir.
    # Find that subdirectory and move its contents to clone_path.
    entries = [os.path.join(target_dir, d) for d in os.listdir(target_dir)]
    subdirs = [d for d in entries if os.path.isdir(d)]

    if len(subdirs) == 1:
        shutil.move(subdirs[0], clone_path)
        return clone_path
    elif len(subdirs) > 1:
        for sd in subdirs:
            if repo.lower() in os.path.basename(sd).lower():
                shutil.move(sd, clone_path)
                return clone_path
        shutil.move(subdirs[0], clone_path)
        return clone_path

    return target_dir

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
    Supports Python, JavaScript/TypeScript, HTML, JSON, and Markdown.
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
            elif f.endswith((".html", ".htm")):
                files["html"].append(full_path)
            elif f.endswith(".json"):
                files["json"].append(full_path)
            elif f.endswith(".md"):
                files["markdown"].append(full_path)

    return files
