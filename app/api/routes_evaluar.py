# app/api/routes_evaluar.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.agents.context_packet import EvaluacionResponse
from app.agents.orchestrator import PipelineOrchestrator
import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/evaluar", tags=["Evaluación"])

@router.post("", response_model=EvaluacionResponse)
async def evaluar_examen(
    alumno_id: str = Form(...),
    nombre_alumno: str = Form(...),
    file: UploadFile = File(...)
):
    # Validar formato de imagen
    if not file.content_type.startswith("image/"):
        logger.error("Archivo inválido", content_type=file.content_type)
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen.")
    
    try:
        logger.info("Iniciando pipeline de evaluación", alumno_id=alumno_id)
        
        # Leer archivo en memoria (No guardar en disco por privacidad)
        image_bytes = await file.read()
        
        # Instanciar orquestador y correr el pipeline de los 4 agentes
        orchestrator = PipelineOrchestrator()
        resultado_context = await orchestrator.run(
            alumno_id=alumno_id,
            nombre_alumno=nombre_alumno,
            image_data=image_bytes
            # Aquí el RAG recupera automáticamente sobre CNEB usando tu cliente de Chroma
        )
        
        return resultado_context

    except Exception as e:
        logger.error("Error en pipeline agéntico", error=str(e))
        raise HTTPException(status_code=500, detail="Error interno procesando el examen.")