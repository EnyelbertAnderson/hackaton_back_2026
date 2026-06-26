"""Encadena los 4 agentes. HOTSPOT: solo Dev A."""
from app.agents.context_packet import ContextPacket, ImageData
from app.agents.vision import run_vision
from app.agents.evaluator import run_evaluator
from app.agents.verifier import run_verifier
from app.agents.diagnostic import run_diagnostic


def run_pipeline(image_bytes: bytes, student_id: str, session_id: str, docente_id: str = "demo") -> dict:
    packet = ContextPacket(
        exam_id=session_id,
        student_id=student_id,
        docente_id=docente_id,
        image=ImageData(
            image_id=f"{session_id}_{student_id}",
            raw_bytes=image_bytes,
        ),
    )

    packet.ocr = run_vision(packet)
    packet.stage = "evaluator"

    packet.evaluation = run_evaluator(packet)
    packet.stage = "verifier"

    packet.verification = run_verifier(packet)
    packet.stage = "diagnostic"

    packet.diagnostic = run_diagnostic(packet)
    packet.stage = "done"

    return {
        "exam_id": packet.exam_id,
        "student_id": packet.student_id,
        "alumno_nombre": packet.ocr.alumno_nombre if packet.ocr else None,
        "score": packet.evaluation.total_score if packet.evaluation else None,
        "score_max": packet.evaluation.score_max if packet.evaluation else None,
        "feedback": packet.evaluation.feedback if packet.evaluation else None,
        "needs_review": packet.verification.needs_review if packet.verification else True,
        "confidence": packet.verification.confidence if packet.verification else 0.0,
        "diagnostic": packet.diagnostic.model_dump() if packet.diagnostic else None,
        "pipeline_state": packet.get_pipeline_state(),
    }
