import os
from dotenv import load_dotenv

load_dotenv()

ENABLE_INGEST = os.getenv("ENABLE_INGEST", "true").strip().lower() in ("1", "true", "yes", "on")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "codebase-rag")
