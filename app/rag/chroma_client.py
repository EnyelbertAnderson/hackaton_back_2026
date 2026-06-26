# app/rag/chroma_client.py

import chromadb

_client = None


def get_chroma_client():
    """
    Singleton del cliente ChromaDB
    """
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path="./chroma_data")
    return _client


def get_collection(name: str = "cneb"):
    client = get_chroma_client()
    return client.get_or_create_collection(name=name)
