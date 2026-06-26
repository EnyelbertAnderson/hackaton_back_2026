# scripts/indexar_cneb.py
"""Indexa fragmentos del CNEB en ChromaDB. Ejecutar una sola vez."""
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.rag.chroma_client import NawiVectorStore
import structlog

logger = structlog.get_logger()

# Fragmentos de ejemplo del CNEB. Reemplazar con extracción real del PDF oficial.
FRAGMENTOS_CNEB = [
    "Competencia: Resuelve problemas de cantidad. El estudiante soluciona problemas referidos a construir el significado de los números y sus operaciones.",
    "Competencia: Resuelve problemas de regularidad, equivalencia y cambio. Caracteriza equivalencias y generaliza regularidades.",
    "Competencia: Lee diversos tipos de textos escritos. El estudiante obtiene información del texto escrito, infiere e interpreta información.",
    "Competencia: Escribe diversos tipos de textos. El estudiante adecúa, organiza y desarrolla las ideas de forma coherente y cohesionada.",
    "Competencia: Indaga mediante métodos científicos. El estudiante problematiza situaciones, diseña estrategias para hacer indagación.",
    "Capacidad: Traduce cantidades a expresiones numéricas, comunicando su comprensión sobre los números y las operaciones.",
    "Desempeño esperado: Resuelve problemas aditivos de una etapa con números naturales de hasta cuatro cifras.",
    "Competencia: Resuelve problemas de forma, movimiento y localización. Modela objetos con formas geométricas y sus transformaciones.",
    "Capacidad: Comunica su comprensión sobre las formas y relaciones geométricas usando lenguaje geométrico.",
    "Enfoque transversal: Orientación al bien común. Los estudiantes comparten siempre los bienes disponibles con sentido de equidad y justicia.",
]


def ejecutar_indexacion():
    logger.info("Iniciando indexación del CNEB en ChromaDB")
    store = NawiVectorStore()

    ids = [f"cneb_{i:04d}" for i in range(len(FRAGMENTOS_CNEB))]
    metadatas = [{"origen": "CNEB_MINEDU", "index": i} for i in range(len(FRAGMENTOS_CNEB))]

    try:
        # Evitar duplicados al re-indexar
        existing = store.collection.get(ids=ids)
        existing_ids = set(existing["ids"])
        new_docs = [(doc, id_, meta) for doc, id_, meta in zip(FRAGMENTOS_CNEB, ids, metadatas)
                    if id_ not in existing_ids]

        if not new_docs:
            logger.info("CNEB ya indexado, no se agregaron documentos nuevos")
            return

        store.add_documents(
            documents=[d[0] for d in new_docs],
            ids=[d[1] for d in new_docs],
            metadatas=[d[2] for d in new_docs]
        )
        logger.info("Indexación completada", documentos=len(new_docs))
    except Exception as e:
        logger.error("Error durante indexación", error=str(e))
        raise


if __name__ == "__main__":
    ejecutar_indexacion()
