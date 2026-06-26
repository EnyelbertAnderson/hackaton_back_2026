# scripts/indexar_cneb.py
"""Indexa los fragmentos estructurados del CNEB en ChromaDB. Dueño: Dev C."""
import sys
import os
# Añadir la raíz al path para que reconozca el módulo 'app' al ejecutarse como script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rag.chroma_client import NawiVectorStore
from scripts.extraer_cneb import extraer_fragmentos_cneb
import structlog

logger = structlog.get_logger()

def ejecutar_indexacion():
    logger.info("Iniciando indexación en base de datos vectorial ChromaDB")
    
    # Instanciar el vector store (Dev A)
    vector_store = NawiVectorStore()
    
    # Extraer los datos a procesar
    fragmentos = extraer_fragmentos_cneb()
    
    if not fragmentos:
        logger.error("No se encontraron fragmentos para indexar")
        return

    # Preparar listas para la carga por lotes (Batch)
    ids = [f"cneb_doc_{i}" for i in range(len(fragmentos))]
    metadatas = [{"origen": "CNEB_Oficial_MINEDU", "index": i} for i in range(len(fragmentos))]
    
    # Almacenar en la colección local de Chroma
    try:
        vector_store.collection.add(
            documents=fragmentos,
            metadatas=metadatas,
            ids=ids
        )
        logger.info("Indexación masiva completada con éxito", documentos_cargados=len(ids))
    except Exception as e:
        logger.error("Fallo crítico durante la indexación", error=str(e))

if __name__ == "__main__":
    ejecutar_indexacion()