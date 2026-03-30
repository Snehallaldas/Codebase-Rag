# ingestion/run_ingest.py
import tempfile
import sys
from ingestion.repo_loader import load_from_github, collect_python_files
from ingestion.ast_chunker import chunk_repository
from ingestion.embedder import store_chunks

def ingest(github_url: str):
    print(f"Cloning {github_url}...")
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = load_from_github(github_url, tmpdir)
        py_files = collect_python_files(repo_path)
        print(f"Found {len(py_files)} Python files.")

        chunks = chunk_repository(py_files, repo_path)
        print(f"Extracted {len(chunks)} chunks.")

        store_chunks(chunks)
        print("Ingestion complete.")

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://github.com/tiangolo/fastapi"
    ingest(url)