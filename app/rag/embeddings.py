# app/rag/embeddings.py

from typing import List
import hashlib


def embed_text(text: str) -> List[float]:
    """
    Embedding MOCK (hackathon-safe).
    Reemplazable por OpenAI / Gemini embeddings.
    """

    h = hashlib.sha256(text.encode()).hexdigest()

    # convierte hash en vector numérico simple
    vec = [int(h[i:i+2], 16) / 255 for i in range(0, 32, 2)]

    return vec


def embed_batch(texts: list[str]) -> list[list[float]]:
    return [embed_text(t) for t in texts]
