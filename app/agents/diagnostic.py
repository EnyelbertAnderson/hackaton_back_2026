# app/agents/diagnostic.py
"""Agente diagnóstico de aula (Claude). Dueño: Dev C."""
import os
import structlog
import anthropic
from app.agents.context_packet import ContextPacket, DiagnosticResult

logger = structlog.get_logger()


def run_diagnostic(packet: ContextPacket) -> DiagnosticResult:
    """Genera diagnóstico pedagógico basado en la evaluación del estudiante."""
    if not packet.evaluation:
        logger.warning("diagnostic.skip", reason="no evaluation")
        return DiagnosticResult()

    try:
        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

        debilidades = packet.evaluation.weaknesses or []
        matches = [m.competence_id for m in packet.evaluation.rubric_matches]

        prompt = f"""Eres un analista pedagógico experto en el Currículo Nacional de Educación Básica (CNEB) peruano.

Datos del estudiante:
- Puntaje: {packet.evaluation.total_score}/{packet.evaluation.score_max}
- Debilidades detectadas: {debilidades}
- Competencias evaluadas: {matches}
- Feedback previo: {packet.evaluation.feedback}

Identifica los errores conceptuales más probables y clasifica al estudiante.

Responde SOLO con JSON válido:
{{
  "errores_comunes": ["error 1", "error 2"],
  "cluster_label": "En riesgo | Promedio | Avanzado"
}}"""

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}]
        )

        import json
        text = message.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        data = json.loads(text.strip())

        logger.info("diagnostic.ok", exam_id=packet.exam_id,
                    cluster=data.get("cluster_label"))
        return DiagnosticResult(
            errores_comunes=data.get("errores_comunes", []),
            cluster_label=data.get("cluster_label")
        )

    except Exception as exc:
        logger.error("diagnostic.error", exam_id=packet.exam_id, error=str(exc))
        return DiagnosticResult(
            errores_comunes=["No se pudo analizar errores automáticamente"],
            cluster_label="Sin clasificar"
        )
