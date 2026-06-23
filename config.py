import os
from dotenv import load_dotenv

load_dotenv()

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_store")
ENABLE_INGEST = os.getenv("ENABLE_INGEST", "true").strip().lower() in ("1", "true", "yes", "on")
