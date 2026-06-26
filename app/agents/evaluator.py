# app/agents/evaluator.py
"""Agente evaluador: analiza respuesta del alumno con Claude + RAG (CNEB)."""
import os
import json
import structlog
import anthropic
from app.agents.context_packet import ContextPacket, EvaluationResult, RubricMatch
from app.rag.retrieval import retrieve_context

logger = structlog.get_logger()


def run_evaluator(packet: ContextPacket) -> EvaluationResult:
    """Evalúa la respuesta OCR usando Claude + contexto RAG del CNEB."""
    if not packet.ocr or not packet.ocr.text.strip():
        return _empty_result()

    text = packet.ocr.text

    # 1. RAG: recuperar contexto del CNEB relevante
    try:
        context_chunks = retrieve_context(text, k=3)
    except Exception:
        context_chunks = []
    packet.retrieved_context = context_chunks
    context_str = "\n".join(context_chunks) if context_chunks else "No se encontró contexto curricular relevante."

    # 2. Evaluar con Claude
    try:
        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

        prompt = f"""Eres un docente experto en el Currículo Nacional de Educación Básica (CNEB) peruano.

Contexto curricular recuperado:
{context_str}

Respuesta del estudiante (transcripción literal):
\"\"\"{text}\"\"\"

Evalúa la respuesta en escala vigesimal (0-20). Identifica fortalezas, debilidades y errores conceptuales.

Responde SOLO con JSON válido:
{{
  "total_score": <número 0-20>,
  "feedback": "<retroalimentación personalizada en 2-3 oraciones>",
  "strengths": ["fortaleza 1", "fortaleza 2"],
  "weaknesses": ["debilidad 1", "debilidad 2"],
  "rubric_matches": [
    {{
      "competence_id": "<nombre de competencia CNEB>",
      "expected_criteria": "<criterio esperado>",
      "matched_evidence": ["<evidencia encontrada>"],
      "score": <puntaje parcial>,
      "justification": "<justificación>"
    }}
  ]
}}"""

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        raw = message.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw.strip())

        matches = [
            RubricMatch(
                competence_id=m.get("competence_id", ""),
                expected_criteria=m.get("expected_criteria", ""),
                matched_evidence=m.get("matched_evidence", []),
                score=float(m.get("score", 0)),
                justification=m.get("justification", "")
            )
            for m in data.get("rubric_matches", [])
        ]

        score = max(0.0, min(20.0, float(data.get("total_score", 10))))
        logger.info("evaluator.ok", exam_id=packet.exam_id, score=score)

        return EvaluationResult(
            total_score=score,
            feedback=data.get("feedback", ""),
            rubric_matches=matches,
            strengths=data.get("strengths", []),
            weaknesses=data.get("weaknesses", [])
        )

    except Exception as exc:
        logger.error("evaluator.error", exam_id=packet.exam_id, error=str(exc))
        return EvaluationResult(
            total_score=10.0,
            feedback=f"No se pudo evaluar automáticamente: {str(exc)[:100]}",
            rubric_matches=[]
        )


def _empty_result() -> EvaluationResult:
    return EvaluationResult(
        total_score=0,
        feedback="No se encontró texto en la imagen.",
        rubric_matches=[]
    )
