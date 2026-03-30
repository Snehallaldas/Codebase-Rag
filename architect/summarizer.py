# architect/summarizer.py
import random
from retrieval.retriever import get_collection
from retrieval.generator import generate_answer


def sample_chunks_broadly(n: int = 20) -> list[dict]:
    """
    Fetches a broad sample of chunks from ChromaDB.
    Uses get() instead of query() — no semantic search, just coverage.
    """
    collection = get_collection()
    total = collection.count()
    fetch_n = min(n, total)

    result = collection.get(
        limit=fetch_n,
        include=["documents", "metadatas"]
    )

    chunks = []
    for doc, meta in zip(result["documents"], result["metadatas"]):
        chunks.append({
            "content":    doc,
            "file_path":  meta.get("file_path", "unknown"),
            "name":       meta.get("name", "unknown"),
            "chunk_type": meta.get("chunk_type", "unknown"),
            "start_line": meta.get("start_line", 0),
            "end_line":   meta.get("end_line", 0),
        })

    # shuffle so we don't always get the same files if total > n
    random.shuffle(chunks)
    return chunks


ARCHITECTURE_PROMPT = """You are a senior software architect reviewing an unfamiliar codebase.
Based on the code samples below, produce a structured architecture summary with these exact sections:

1. PROJECT OVERVIEW — What does this application do? (2-3 sentences)
2. TECH STACK — Languages, frameworks, libraries detected
3. MAIN COMPONENTS — List the key modules/services and what each does
4. ENTRY POINTS — Where does execution start? (main files, routers, CLI)
5. DATA FLOW — How does data move through the system at a high level?
6. NOTABLE PATTERNS — Any design patterns, architectural decisions worth noting

Be concise but specific. Cite file names where relevant.

Code samples:
{context}
"""


def generate_architecture_summary() -> dict:
    """
    Samples chunks broadly and generates a full architecture summary.
    Returns the summary text plus the list of files sampled.
    """
    chunks = sample_chunks_broadly(n=20)

    # build context — truncate each chunk to avoid blowing the context window
    context_blocks = []
    for chunk in chunks:
        header = f"[{chunk['file_path']} — {chunk['chunk_type']}: {chunk['name']}]"
        body = chunk["content"][:400]   # cap per chunk
        context_blocks.append(f"{header}\n{body}")

    context = "\n\n".join(context_blocks)
    prompt = ARCHITECTURE_PROMPT.format(context=context)

    summary = generate_answer(prompt, model="mistral-small-latest")

    files_sampled = list({c["file_path"] for c in chunks})

    return {
        "summary":       summary,
        "files_sampled": sorted(files_sampled),
        "chunks_used":   len(chunks),
    }