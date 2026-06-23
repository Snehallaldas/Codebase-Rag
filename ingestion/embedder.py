# ingestion/embedder.py
from pinecone import Pinecone, ServerlessSpec
from config import PINECONE_API_KEY, PINECONE_INDEX_NAME
from ingestion.ast_chunker import CodeChunk
from retrieval.embeddings import embed_texts

def get_pinecone_client() -> Pinecone:
    if not PINECONE_API_KEY:
        raise RuntimeError("PINECONE_API_KEY is required to connect to Pinecone.")
    return Pinecone(api_key=PINECONE_API_KEY)

def get_pinecone_index(pc: Pinecone):
    # Check if index exists, create if not
    # We use serverless spec (AWS us-east-1 is the default free tier)
    if PINECONE_INDEX_NAME not in pc.list_indexes().names():
        print(f"Creating Pinecone index: {PINECONE_INDEX_NAME}...")
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=1024, # mistral-embed dimensions
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
    return pc.Index(PINECONE_INDEX_NAME)

def store_chunks(chunks: list[CodeChunk], persist_dir: str = None):
    """
    Embeds and stores all chunks in Pinecone.
    Wipes the index first for a fresh ingest.
    """
    if not chunks:
        print("No chunks to store.")
        return None

    pc = get_pinecone_client()
    index = get_pinecone_index(pc)

    # Clean existing vectors for a fresh ingest
    try:
        print("Clearing existing vectors in Pinecone index...")
        index.delete(delete_all=True)
    except Exception as e:
        err_str = str(e)
        if "Namespace not found" in err_str or "404" in err_str:
            print("Index is empty (no existing vectors to clear). Proceeding with ingest.")
        else:
            print(f"Warning: Failed to clear Pinecone index: {e}")

    # Pinecone recommended batch size is ~100 vectors
    BATCH_SIZE = 100
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        documents = [c.content for c in batch]
        
        print(f"Embedding batch {i // BATCH_SIZE + 1} ({len(batch)} chunks)...")
        embeddings = embed_texts(documents)
        
        vectors_to_upsert = []
        for chunk, embedding in zip(batch, embeddings):
            safe_id = chunk.chunk_id.encode('ascii', errors='ignore').decode('ascii')
            vectors_to_upsert.append({
                "id": safe_id,
                "values": embedding,
                "metadata": {
                    "file_path":   chunk.file_path,
                    "chunk_type":  chunk.chunk_type,
                    "name":        chunk.name,
                    "start_line":  chunk.start_line,
                    "end_line":    chunk.end_line,
                    "language":    chunk.language,
                    "content":     chunk.content,
                }
            })
            
        print(f"Upserting batch {i // BATCH_SIZE + 1} to Pinecone...")
        index.upsert(vectors=vectors_to_upsert)

    print(f"Successfully stored {len(chunks)} chunks in Pinecone index: {PINECONE_INDEX_NAME}.")
    return index
