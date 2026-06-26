from fastapi import APIRouter, UploadFile, File, Form
from app.agents.orchestrator import run_pipeline

router = APIRouter()


@router.post("/evaluar")
async def evaluar_examen(
    image: UploadFile = File(...),
    student_id: str = Form(...),
    session_id: str = Form(...),
    docente_id: str = Form(default="demo"),
):
    image_bytes = await image.read()
    return run_pipeline(
        image_bytes=image_bytes,
        student_id=student_id,
        session_id=session_id,
        docente_id=docente_id,
    )
