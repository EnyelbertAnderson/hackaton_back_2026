# app/agents/evaluator.py

from app.agents.context_packet import ContextPacket, EvaluationResult, RubricMatch  # noqa: F401 — tipos en context_packet
from app.rag.retrieval import retrieve_context
import re


def run_evaluator(packet: ContextPacket) -> EvaluationResult:
    """
    Evalúa el examen usando:
    - OCR del alumno
    - RAG (CNEB / rúbricas)
    - scoring simple (hackathon MVP)
    """

    if not packet.ocr:
        return _empty_result()

    text = packet.ocr.text

    # 1. RAG: traer contexto relevante
    context = retrieve_context(text, k=3)
    packet.retrieved_context = context

    # 2. Evaluación simple por heurística (MVP)
    score, matches = _simple_scoring(text, context)

    feedback = _generate_feedback(score, text)

    return EvaluationResult(
        total_score=score,
        feedback=feedback,
        rubric_matches=matches,
        strengths=_extract_strengths(text),
        weaknesses=_extract_weaknesses(text)
    )


# ---------------------------------------------------
# SCORE SIMPLE (MVP)
# ---------------------------------------------------
def _simple_scoring(text: str, context: list[str]):
    score = 10.0
    matches = []

    # heurística 1: longitud de respuesta
    if len(text) > 200:
        score += 3
    else:
        score -= 2

    # heurística 2: palabras clave
    keywords = {
        "agua": "ciclo del agua",
        "evapora": "proceso físico",
        "plantas": "biología básica",
        "fotosíntesis": "concepto correcto"
    }

    for k, concept in keywords.items():
        if re.search(k, text.lower()):
            score += 2
            matches.append(
                RubricMatch(
                    competence_id=concept,
                    expected_criteria=k,
                    matched_evidence=[k],
                    score=2,
                    justification=f"Detectado concepto: {k}"
                )
            )

    # clamp score
    score = max(0, min(20, score))

    return score, matches


# ---------------------------------------------------
# FEEDBACK SIMPLE
# ---------------------------------------------------
def _generate_feedback(score: float, text: str) -> str:
    if score >= 16:
        return "Buen dominio del tema. Respuesta clara y correcta."
    elif score >= 10:
        return "Respuesta aceptable, pero puede mejorar en profundidad."
    return "Respuesta insuficiente. Requiere reforzar conceptos clave."


def _extract_strengths(text: str) -> list[str]:
    strengths = []
    if "explica" in text.lower():
        strengths.append("Intenta explicar conceptos")
    if "porque" in text.lower():
        strengths.append("Incluye razonamiento")
    return strengths


def _extract_weaknesses(text: str) -> list[str]:
    weaknesses = []
    if len(text) < 100:
        weaknesses.append("Respuesta muy corta")
    return weaknesses


def _empty_result():
    return EvaluationResult(
        total_score=0,
        feedback="No se encontró OCR",
        rubric_matches=[]
    )
