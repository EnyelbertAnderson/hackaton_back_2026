"""Agente OCR: transcribe examen manuscrito con Gemini Flash-Lite."""
from __future__ import annotations
import base64
import os
import json
import structlog
from google import genai
from google.genai import types
from app.agents.context_packet import ContextPacket, OCRResult

log = structlog.get_logger()

_PROMPT = """Eres un transcriptor de exámenes escolares peruanos.
Transcribe LITERALMENTE lo que escribió el alumno — no corrijas ortografía ni gramática.
Si hay operaciones matemáticas o diagramas, descríbelos entre corchetes [diagrama: ...].

Responde SOLO con JSON válido:
{
  "alumno_nombre": "<nombre del encabezado o null si ilegible>",
  "text": "<transcripción completa literal>"
}"""


def run_vision(packet: ContextPacket) -> OCRResult:
    if packet.image is None:
        log.warning("vision.no_image", exam_id=packet.exam_id)
        return OCRResult(text="", alumno_nombre=None)

    try:
        client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])
        img_b64 = base64.b64encode(packet.image.raw_bytes).decode()

        response = client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=[
                types.Part.from_bytes(data=base64.b64decode(img_b64), mime_type="image/jpeg"),
                _PROMPT,
            ],
        )

        data = json.loads(response.text)
        packet.stage = "vision"
        packet.descartar_imagen()  # privacidad de menores
        log.info("vision.ok", exam_id=packet.exam_id, alumno=data.get("alumno_nombre"))
        return OCRResult(text=data["text"], alumno_nombre=data.get("alumno_nombre"))

    except Exception as exc:
        log.error("vision.error", exam_id=packet.exam_id, error=str(exc))
        packet.descartar_imagen()
        return OCRResult(text="", alumno_nombre=None)
