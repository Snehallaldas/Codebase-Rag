# ingestion/embedder.py
import chromadb
from chromadb.utils import embedding_functions
from ingestion.ast_chunker import CodeChunk

COLLECTION_NAME = "codebase"

def get_chroma_client(persist_dir: str = "./chroma_store") -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path=persist_dir)


def get_or_create_collection(client: chromadb.PersistentClient):
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"  # fast, good for code
    )
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )


def store_chunks(chunks: list[CodeChunk], persist_dir: str = "./chroma_store"):
    """
    Embeds and stores all chunks in ChromaDB.
    Replaces existing collection for the same repo (fresh ingest).
    """
    client = get_chroma_client(persist_dir)

    # delete and recreate for a fresh ingest
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = get_or_create_collection(client)

    # ChromaDB batch limit is 5461 — chunk your batches
    BATCH_SIZE = 500
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        collection.add(
            ids=[c.chunk_id for c in batch],
            documents=[c.content for c in batch],
            metadatas=[{
                "file_path":   c.file_path,
                "chunk_type":  c.chunk_type,
                "name":        c.name,
                "start_line":  c.start_line,
                "end_line":    c.end_line,
                "language":    c.language,
            } for c in batch],
        )

    print(f"Stored {len(chunks)} chunks in ChromaDB.")
    return collection