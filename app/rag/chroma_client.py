# app/rag/chroma_client.py
"""Cliente de ChromaDB para recuperación de competencias del CNEB. Propiedad de Dev A."""
import os
import chromadb
from chromadb.utils import embedding_functions
import structlog

logger = structlog.get_logger()

class NawiVectorStore:
    def __init__(self):
        # 1. Obtener la ruta del directorio de persistencia local
        self.data_dir = os.getenv("CHROMA_DATA_DIR", "./chroma_data")
        logger.info("Inicializando ChromaDB", path=self.data_dir)
        
        # 2. Crear el cliente persistente
        self.client = chromadb.PersistentClient(path=self.data_dir)
        
        # 3. Configurar la función de embeddings text-embedding-005 de Google (según AGENTS.md)
        # Requiere que GOOGLE_API_KEY esté configurado en tu entorno o archivo .env
        self.embedding_function = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
            api_key=os.getenv("GOOGLE_API_KEY")
        )
        
        # 4. Obtener o crear la colección dedicada al Currículo Nacional (CNEB)
        self.collection = self.client.get_or_create_collection(
            name="cneb_curriculo",
            embedding_function=self.embedding_function
        )
        logger.info("Colección cneb_curriculo lista para operar")

    def buscar_competencia(self, query: str, n_results: int = 2):
        """
        Busca los fragmentos o artículos del CNEB más relevantes para la evaluación actual.
        """
        logger.info("Ejecutando consulta RAG en ChromaDB", query=query)
        try:
            resultados = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            return resultados
        except Exception as e:
            logger.error("Error al consultar ChromaDB", error=str(e))
            return {"documents": [[]], "metadatas": [[]]}