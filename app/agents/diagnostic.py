# app/agents/diagnostic.py
"""Agente diagnóstico para recopilar errores recurrentes del aula (Gemini 3 Flash). Dueño: Dev C."""
import os
from google import genai
from google.genai import types
import structlog
from app.agents.context_packet import DiagnosticoAulaResponse

logger = structlog.get_logger()

class DiagnosticAgent:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash"  # Ejecutado bajo el tier gratuito de Google AI Studio

    async def analizar_aula(self, aula_id: str, evaluaciones: list) -> DiagnosticoAulaResponse:
        logger.info("Paso 4: Generando diagnóstico analítico consolidado", aula_id=aula_id, total_examenes=len(evaluaciones))
        
        prompt_sistema = (
            "Eres un agente analista de datos educativos enfocado en el Currículo Nacional (CNEB).\n"
            "Recibirás una lista de evaluaciones de alumnos de un aula. Debes agrupar y determinar:\n"
            "1. Errores más comunes cometidos.\n"
            "2. Puntos fuertes del grupo.\n"
            "3. Recomendaciones pedagógicas basadas directamente en el CNEB.\n"
            "4. Un breve resumen ejecutivo del rendimiento global."
        )

        # Serializamos las evaluaciones para dárselas como contexto al modelo
        datos_estudiantes = "\n".join([
            f"- Alumno: {ev.nombre_alumno} | Nota: {ev.nota} | Feedback: {ev.feedback}"
            for ev in evaluaciones
        ])

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=f"Aula ID: {aula_id}\n\nResultados del lote:\n{datos_estudiantes}",
                config=types.GenerateContentConfig(
                    system_instruction=prompt_sistema,
                    response_mime_type="application/json",
                    response_schema=DiagnosticoAulaResponse,
                    temperature=0.2
                )
            )
            
            resultado_estructurado = DiagnosticoAulaResponse.model_validate_json(response.text)
            logger.info("Diagnóstico de aula generado exitosamente")
            return resultado_estructurado

        except Exception as e:
            logger.error("Error al consolidar diagnóstico del aula", error=str(e))
            # Fallback estructurado básico en caso de error de red o cuota en la hackathon
            return DiagnosticoAulaResponse(
                aula_id=aula_id,
                errores_comunes=["No se pudo calcular la analítica de errores recurrentes debido a un fallo técnico temporal."],
                puntos_fuertes=["Datos en proceso de recopilación."],
                recomendaciones_cneb=["Reforzar las competencias base indicadas en las cartillas individuales."],
                resumen_rendimiento="Análisis en cola."
            )