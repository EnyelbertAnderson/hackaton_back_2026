# app/rag/chroma_client.py
"""Cliente ChromaDB con embedding function propia (sin descarga de modelos)."""
import chromadb
from chromadb import EmbeddingFunction, Embeddings, Documents
from app.rag.embeddings import embed_batch

_client = None


class LocalEmbeddingFunction(EmbeddingFunction):
    """Wrapper que conecta nuestros embeddings locales con ChromaDB."""
    def __call__(self, input: Documents) -> Embeddings:
        return embed_batch(list(input))


_embedding_fn = LocalEmbeddingFunction()


def get_chroma_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path="./chroma_data")
    return _client


def get_collection(name: str = "cneb") -> chromadb.Collection:
    return get_chroma_client().get_or_create_collection(
        name=name,
        embedding_function=_embedding_fn,
    )


class NawiVectorStore:
    def __init__(self, collection_name: str = "cneb"):
        self.collection = get_collection(collection_name)

    def add_documents(self, documents: list[str], ids: list[str],
                      metadatas: list[dict] | None = None) -> None:
        self.collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas or [{} for _ in documents]
        )
