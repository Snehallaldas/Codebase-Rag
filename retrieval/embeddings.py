import os

import requests
from dotenv import load_dotenv

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_EMBEDDING_MODEL = os.getenv("MISTRAL_EMBEDDING_MODEL", "mistral-embed")
MISTRAL_EMBEDDING_URL = "https://api.mistral.ai/v1/embeddings"


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    if not MISTRAL_API_KEY:
        raise RuntimeError("MISTRAL_API_KEY is required to generate embeddings.")

    response = requests.post(
        MISTRAL_EMBEDDING_URL,
        headers={
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MISTRAL_EMBEDDING_MODEL,
            "input": texts,
        },
        timeout=90,
    )
    response.raise_for_status()

    data = response.json()["data"]
    data.sort(key=lambda item: item.get("index", 0))
    return [item["embedding"] for item in data]


def embed_text(text: str) -> list[float]:
    return embed_texts([text])[0]
