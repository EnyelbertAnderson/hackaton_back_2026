# app/agents/verifier.py
"""Agente verificador de coherencia pedagógica (Claude). Dueño: Dev C."""
import os
import structlog
import anthropic
from app.agents.context_packet import ContextPacket, VerificationResult

logger = structlog.get_logger()


def run_verifier(packet: ContextPacket) -> VerificationResult:
    """Verifica coherencia entre OCR, score y feedback. Retorna VerificationResult."""
    if not packet.ocr or not packet.evaluation:
        logger.warning("verifier.skip", reason="no ocr o evaluation")
        return VerificationResult(is_consistent=True, confidence=0.5, needs_review=True,
                                  motivo="Datos insuficientes para verificar")

    try:
        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

        prompt = f"""Eres un auditor pedagógico. Revisa si hay contradicción entre:
- Transcripción: {packet.ocr.text[:500]}
- Puntaje asignado: {packet.evaluation.total_score} / {packet.evaluation.score_max}
- Feedback: {packet.evaluation.feedback}

Responde SOLO con JSON válido:
{{
  "is_consistent": true o false,
  "confidence": número entre 0.0 y 1.0,
  "needs_review": true o false,
  "motivo": "razón breve si needs_review es true, sino null"
}}"""

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}]
        )

        import json
        text = message.content[0].text.strip()
        # Limpiar posibles backticks
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        data = json.loads(text.strip())

        logger.info("verifier.ok", exam_id=packet.exam_id,
                    consistent=data.get("is_consistent"), confidence=data.get("confidence"))
        return VerificationResult(
            is_consistent=data.get("is_consistent", True),
            confidence=float(data.get("confidence", 0.8)),
            needs_review=data.get("needs_review", False),
            motivo=data.get("motivo")
        )

    except Exception as exc:
        logger.error("verifier.error", exam_id=packet.exam_id, error=str(exc))
        return VerificationResult(is_consistent=True, confidence=0.6,
                                  needs_review=True, motivo=f"Error de verificación: {str(exc)[:80]}")
