# app/rag/chroma_client.py
"""Cliente de ChromaDB para recuperación de CNEB. Propiedad de Dev A."""
import chromadb
from chromadb.utils import embedding_functions
import os

class NawiVectorStore:
    def __init__(self):
        # Directorio local definido en tu .env y protegido por .gitignore
        data_dir = os.getenv("CHROMA_DATA_DIR", "./chroma_data")
        
        self.client = chromadb.PersistentClient(path=data_dir)
        
        # Usamos el modelo text-embedding-005 de Google especificado en tu AGENTS.md
        self.embedding_function = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
            api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # Obtener o crear la colección del Currículo Nacional
        self.collection = self.client.get_or_create_collection(
            name="cneb_curriculo",
            embedding_function=self.embedding_function
        )

    def buscar_competencia(self, query: str, n_results: int = 2):
        """Busca los fragmentos del CNEB más relevantes para la evaluación."""
        return self.collection.query(
            query_texts=[query],
            n_results=n_results
        )