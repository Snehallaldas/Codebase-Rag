# retrieval/generator.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"


def generate_answer(prompt: str, model: str = "mistral-small-latest") -> str:
    """
    Sends the prompt to Mistral and returns the answer text.
    """
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,   # low temp = more factual, less creative
        "max_tokens": 1024,
    }

    response = requests.post(MISTRAL_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"].strip()
