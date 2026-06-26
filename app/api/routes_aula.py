# app/api/routes_aula.py
from fastapi import APIRouter, HTTPException
from app.agents.context_packet import DiagnosticoAulaResponse
import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/aula", tags=["Aula"])

@router.get("/{aula_id}/diagnostico", response_model=DiagnosticoAulaResponse)
async def obtener_diagnostico_aula(aula_id: str):
    try:
        logger.info("Generando diagnóstico consolidado de aula", aula_id=aula_id)
        
        # 1. Recuperar de ChromaDB o de la BD temporal las notas consolidadas de esta aula
        # 2. Pasar el consolidado al agente 'diagnostic' para que extraiga la analítica de errores
        
        # Mock estructurado según lo que espera el frontend de la imagen:
        mock_diagnostico = {
            "aula_id": aula_id,
            "errores_comunes": [
                "Confusión recurrente entre perímetro y área.",
                "Omisión de unidades de medida (cm, m) en la respuesta final."
            ],
            "puntos_fuertes": [
                "Buen planteamiento algebraico inicial.",
                "Comprensión clara de operaciones aritméticas básicas."
            ],
            "recomendaciones_cneb": [
                "Reforzar competencia 'Resuelve problemas de forma, movimiento y localización' del CNEB.",
                "Implementar sesiones de modelado gráfico antes del cálculo numérico."
            ],
            "resumen_rendimiento": "El 65% del aula requiere refuerzo en geometría aplicada."
        }
        
        return mock_diagnostico

    except Exception as e:
        logger.error("Error al obtener diagnóstico", aula_id=aula_id, error=str(e))
        raise HTTPException(status_code=500, detail="No se pudo procesar el diagnóstico del aula.")