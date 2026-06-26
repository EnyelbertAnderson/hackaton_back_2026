# app/api/routes_evaluar.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.agents.orchestrator import run_pipeline
from app.agents.context_packet import EvaluarResponse
import structlog

logger = structlog.get_logger()
router = APIRouter(tags=["Evaluación"])


@router.post("/evaluar", response_model=EvaluarResponse, summary="Evalúa un examen manuscrito o PDF")
async def evaluar_examen(
    image: UploadFile = File(..., description="Foto del examen (JPG, PNG, PDF)"),
    student_id: str = Form(..., description="ID del estudiante, ej: ALU-001"),
    session_id: str = Form(..., description="ID de sesión/examen, ej: EXAM-2026-01"),
    docente_id: str = Form(default="demo", description="ID del docente"),
):
    ct = image.content_type or ""
    fname = (image.filename or "").lower()
    is_pdf = ct == "application/pdf" or fname.endswith(".pdf")
    is_image = ct.startswith("image/")

    if not is_pdf and not is_image:
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen (JPG, PNG) o PDF.")

    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="El archivo está vacío.")

    mime_type = "application/pdf" if is_pdf else ct or "image/jpeg"
    logger.info("evaluar.inicio", student_id=student_id, session_id=session_id, mime=mime_type)

    try:
        return run_pipeline(
            image_bytes=image_bytes,
            student_id=student_id,
            session_id=session_id,
            docente_id=docente_id,
            mime_type=mime_type,
        )
    except Exception as e:
        logger.error("evaluar.error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error en el pipeline: {str(e)}")
