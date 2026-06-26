# app/agents/vision.py
"""Agente OCR de examen manuscrito (Gemini). Dueño: Dev C."""
import os
from google import genai
import structlog

logger = structlog.get_logger()

class VisionAgent:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash"

    async def extract_text(self, image_data: bytes) -> str:
        logger.info("Paso 1: Iniciando OCR de examen manuscrito en memoria")
        
        prompt = (
            "Transcribe textualmente todo el contenido manuscrito y las operaciones matemáticas "
            "de este examen. Si hay gráficos, descríbelos brevemente. Sé ultra preciso."
        )

        try:
            # Pasar los bytes directamente usando la estructura del SDK nativo de Google GenAI
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    prompt,
                    {"mime_type": "image/png", "data": image_data}
                ]
            )
            logger.info("OCR completado de forma exitosa")
            return response.text
        except Exception as e:
            logger.error("Error en Agente Visión, aplicando fallback textual", error=str(e))
            return "[Error de lectura en el examen manuscrito: No se pudo procesar la imagen]"