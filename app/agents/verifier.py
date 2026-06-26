# app/agents/verifier.py
"""Agente verificador de calidad y coherencia formativa (Gemini). Dueño: Dev C."""
import os
from google import genai
from google.genai import types
import structlog
from app.agents.context_packet import EvaluacionResponse

logger = structlog.get_logger()

class VerifierAgent:
    def __init__(self):
        # Utiliza la nueva SDK de Google GenAI especificada en requirements y AGENTS.md
        api_key = os.getenv("GOOGLE_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash"  # Reemplazo óptimo para Flash-Lite en la SDK actual

    async def verify(self, current_packet: EvaluacionResponse) -> EvaluacionResponse:
        logger.info("Paso 3: Iniciando control de calidad en Agente Verificador", alumno_id=current_packet.alumno_id)
        
        prompt_sistema = (
            "Eres un agente auditor de consistencia pedagógica experto en el Currículo Nacional Peruano.\n"
            "Tu única tarea es analizar la respuesta de evaluación de un examen y verificar si existe "
            "alguna contradicción evidente entre la nota asignada, la transcripción del examen y el feedback dado.\n"
            "Si encuentras discrepancias graves, ajusta o refina el feedback para corregir la contradicción. "
            "Si todo es correcto, devuelve los campos intactos."
        )

        prompt_usuario = (
            f"Transcripción del Examen: {current_packet.transcripcion_ocr}\n"
            f"Nota Asignada: {current_packet.nota}\n"
            f"Criterio Aplicado: {current_packet.criterio_citado}\n"
            f"Feedback Propuesto: {current_packet.feedback}"
        )

        try:
            # Forzar salida en formato JSON estructurado que coincida con nuestro Schema de Pydantic
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt_usuario,
                config=types.GenerateContentConfig(
                    system_instruction=prompt_sistema,
                    response_mime_type="application/json",
                    response_schema=EvaluacionResponse,
                    temperature=0.1
                )
            )
            
            # Pydantic puede leer y validar directamente cadenas de texto estructuradas JSON
            valid_json = EvaluacionResponse.model_validate_json(response.text)
            logger.info("Verificación de consistencia completada sin novedades")
            return valid_json

        except Exception as e:
            logger.error("Error en la ejecución del Agente Verificador, aplicando fallback", error=str(e))
            # Fallback seguro: Continuar con los datos del paquete sin detener el servidor de la Hackathon
            return current_packet