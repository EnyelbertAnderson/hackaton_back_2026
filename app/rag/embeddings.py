# app/rag/embeddings.py
"""Embedding mock de 16 dimensiones, estable para hackathon.
   Reemplazable por OpenAI/Gemini embeddings cambiando solo esta función.
"""
import hashlib
from typing import List

_DIM = 16  # ChromaDB requiere dimensión consistente en la colección


def embed_text(text: str) -> List[float]:
    h = hashlib.sha256(text.encode()).hexdigest()
    return [int(h[i:i+4], 16) / 65535.0 for i in range(0, _DIM * 4, 4)]


def embed_batch(texts: List[str]) -> List[List[float]]:
    return [embed_text(t) for t in texts]
