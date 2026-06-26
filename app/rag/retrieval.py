# app/rag/retrieval.py

from app.rag.chroma_client import get_collection
from app.rag.embeddings import embed_text


def retrieve_context(query: str, k: int = 3) -> list[str]:
    """
    Busca fragmentos relevantes en ChromaDB
    """

    collection = get_collection()

    query_embedding = embed_text(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )

    documents = results.get("documents", [[]])[0]

    return documents
