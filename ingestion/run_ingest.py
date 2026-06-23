# ingestion/run_ingest.py
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import CHROMA_PERSIST_DIR
from ingestion.repo_loader import load_from_github, collect_supported_files
from ingestion.ast_chunker import chunk_repository_multilang
from ingestion.embedder import store_chunks

def ingest(github_url: str, persist_dir: str = CHROMA_PERSIST_DIR):
    """Clone a GitHub repo, chunk supported files, and store embeddings locally."""
    print(f"Cloning {github_url}...")
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = load_from_github(github_url, tmpdir)

        files_by_lang = collect_supported_files(repo_path)
        total_files = sum(len(v) for v in files_by_lang.values())

        print(f"Found {total_files} supported files:")
        for lang, paths in files_by_lang.items():
            print(f"  {lang}: {len(paths)}")

        if not any(files_by_lang.values()):
            raise RuntimeError(
                "No supported files found. Supported: Python, JavaScript, TypeScript."
            )

        chunks = chunk_repository_multilang(files_by_lang, repo_path)
        print(f"Extracted {len(chunks)} chunks.")

        store_chunks(chunks, persist_dir=persist_dir)
        print(f"Ingestion complete. Stored chunks in: {persist_dir}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ingestion/run_ingest.py <github_url>")
        sys.exit(1)

    url = sys.argv[1]
    ingest(url)
