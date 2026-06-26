# app/agents/orchestrator.py
"""Encadena los 4 agentes. HOTSPOT: solo Dev A."""
from app.agents.context_packet import (
    ContextPacket, ImageData,
    EvaluarResponse, DiagnosticOut, RubricMatchOut,
)
from app.agents.vision import run_vision
from app.agents.evaluator import run_evaluator
from app.agents.verifier import run_verifier
from app.agents.diagnostic import run_diagnostic


def run_pipeline(image_bytes: bytes, student_id: str, session_id: str,
                 docente_id: str = "demo", mime_type: str = "image/jpeg") -> EvaluarResponse:
    packet = ContextPacket(
        exam_id=session_id,
        student_id=student_id,
        docente_id=docente_id,
        image=ImageData(
            image_id=f"{session_id}_{student_id}",
            raw_bytes=image_bytes,
            mime_type=mime_type,
        ),
    )

    packet.ocr        = run_vision(packet)
    packet.stage      = "evaluator"
    packet.evaluation = run_evaluator(packet)
    packet.stage      = "verifier"
    packet.verification = run_verifier(packet)
    packet.stage      = "diagnostic"
    packet.diagnostic = run_diagnostic(packet)
    packet.stage      = "done"

    ev  = packet.evaluation
    ver = packet.verification
    dia = packet.diagnostic

    return EvaluarResponse(
        exam_id=packet.exam_id,
        student_id=packet.student_id,
        alumno_nombre=packet.ocr.alumno_nombre if packet.ocr else None,
        score=ev.total_score if ev else 0.0,
        score_max=ev.score_max if ev else 20.0,
        feedback=ev.feedback if ev else "",
        strengths=ev.strengths if ev else [],
        weaknesses=ev.weaknesses if ev else [],
        rubric_matches=[
            RubricMatchOut(
                competence_id=m.competence_id,
                expected_criteria=m.expected_criteria,
                matched_evidence=m.matched_evidence,
                score=m.score,
                justification=m.justification,
            )
            for m in (ev.rubric_matches if ev else [])
        ],
        needs_review=ver.needs_review if ver else True,
        confidence=ver.confidence if ver else 0.0,
        diagnostic=DiagnosticOut(
            errores_comunes=dia.errores_comunes if dia else [],
            cluster_label=dia.cluster_label if dia else None,
        ),
        pipeline_state=packet.get_pipeline_state(),
    )
