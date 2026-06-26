# app/api/routes_aula.py
from fastapi import APIRouter, HTTPException
from app.agents.context_packet import DiagnosticoAulaResponse
from app.agents.diagnostic import run_diagnostic
from app.agents.context_packet import ContextPacket, EvaluationResult
import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/aula", tags=["Aula"])


@router.get(
    "/{aula_id}/diagnostico",
    response_model=DiagnosticoAulaResponse,
    summary="Diagnóstico consolidado de un aula",
)
async def obtener_diagnostico_aula(aula_id: str):
    """
    Devuelve errores comunes, fortalezas y recomendaciones CNEB para el aula.
    En el MVP usa datos de ejemplo; conectar a BD en producción.
    """
    try:
        logger.info("diagnostico.inicio", aula_id=aula_id)
        return DiagnosticoAulaResponse(
            aula_id=aula_id,
            errores_comunes=[
                "Confusión recurrente entre perímetro y área.",
                "Omisión de unidades de medida (cm, m²) en la respuesta final.",
                "Dificultad para interpretar enunciados con datos implícitos.",
            ],
            puntos_fuertes=[
                "Buen planteamiento algebraico inicial.",
                "Comprensión clara de operaciones aritméticas básicas.",
            ],
            recomendaciones_cneb=[
                "Reforzar competencia 'Resuelve problemas de forma, movimiento y localización' (CNEB p.138).",
                "Implementar sesiones de modelado gráfico antes del cálculo numérico.",
                "Trabajar con situaciones contextualizadas que exijan interpretar el enunciado.",
            ],
            resumen_rendimiento="El 65 % del aula requiere refuerzo en geometría aplicada.",
        )
    except Exception as e:
        logger.error("diagnostico.error", aula_id=aula_id, error=str(e))
        raise HTTPException(status_code=500, detail="No se pudo generar el diagnóstico.")
