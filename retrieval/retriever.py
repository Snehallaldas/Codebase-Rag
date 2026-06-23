# retrieval/retriever.py
import chromadb
from config import CHROMA_PERSIST_DIR
from retrieval.embeddings import embed_text

COLLECTION_NAME = "codebase"

def get_collection(persist_dir: str = CHROMA_PERSIST_DIR):
    client = chromadb.PersistentClient(path=persist_dir)
    return client.get_collection(name=COLLECTION_NAME)


def retrieve_chunks(query: str, top_k: int = 5, persist_dir: str = CHROMA_PERSIST_DIR) -> list[dict]:
    """
    Retrieves the top_k most relevant code chunks for a query.
    Returns list of dicts with content + metadata.
    """
    collection = get_collection(persist_dir)
    results = collection.query(
        query_embeddings=[embed_text(query)],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        chunks.append({
            "content":    doc,
            "file_path":  meta.get("file_path", "unknown"),
            "name":       meta.get("name", "unknown"),
            "chunk_type": meta.get("chunk_type", "unknown"),
            "start_line": meta.get("start_line", 0),
            "end_line":   meta.get("end_line", 0),
            "score":      round(1 - dist, 4),  # cosine similarity
        })

    return chunks
