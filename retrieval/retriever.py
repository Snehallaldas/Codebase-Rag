# retrieval/retriever.py
from pinecone import Pinecone
from config import PINECONE_API_KEY, PINECONE_INDEX_NAME
from retrieval.embeddings import embed_text

def get_pinecone_index():
    if not PINECONE_API_KEY:
        raise ValueError("PINECONE_API_KEY is required but not configured.")
    
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    # Check if index exists, raise ValueError if it doesn't (so main.py returns 400 Bad Request)
    if PINECONE_INDEX_NAME not in pc.list_indexes().names():
        raise ValueError("No codebase has been ingested yet. Please ingest a repository first.")
        
    return pc.Index(PINECONE_INDEX_NAME)

def retrieve_chunks(query: str, top_k: int = 5, persist_dir: str = None) -> list[dict]:
    """
    Retrieves the top_k most relevant code chunks for a query from Pinecone.
    Returns list of dicts with content + metadata.
    """
    index = get_pinecone_index()
    query_vector = embed_text(query)
    
    results = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )
    
    chunks = []
    if not results or "matches" not in results:
        return chunks
        
    for match in results["matches"]:
        meta = match.get("metadata", {})
        score = match.get("score", 0.0)
        
        chunks.append({
            "content":    meta.get("content", ""),
            "file_path":  meta.get("file_path", "unknown"),
            "name":       meta.get("name", "unknown"),
            "chunk_type": meta.get("chunk_type", "unknown"),
            "start_line": int(meta.get("start_line", 0)),
            "end_line":   int(meta.get("end_line", 0)),
            "score":      round(score, 4),  # Pinecone returns cosine similarity directly
        })
        
    return chunks
