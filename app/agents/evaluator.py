# app/agents/evaluator.py
"""Agente evaluador principal: calificación + RAG (Haiku 4.5). Dueño: Dev A."""
import os
from anthropic import Anthropic
import structlog
from app.rag.chroma_client import NawiVectorStore
from app.agents.context_packet import EvaluacionResponse

logger = structlog.get_logger()

class EvaluatorAgent:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        # Invocar la base de datos de vectores que configuramos antes
        self.vector_store = NawiVectorStore()

    async def evaluate(self, alumno_id: str, nombre_alumno: str, ocr_text: str) -> EvaluacionResponse:
        logger.info("Paso 2: Iniciando Evaluación Formativa con Claude Haiku 4.5", alumno_id=alumno_id)
        
        # 1. Recuperar contexto normativo del CNEB mediante RAG local
        logger.info("Consultando criterios en base de datos vectorial...")
        rag_results = self.vector_store.buscar_competencia(query=ocr_text, n_results=1)
        contexto_cneb = rag_results["documents"][0][0] if rag_results["documents"][0] else "CNEB General Competencia Matemática"

        # 2. Diseñar prompts de rol pedagógico
        system_prompt = (
            "Eres el Evaluador Pedagógico Inteligente del sistema Ñawi.\n"
            "Tu tarea es evaluar el examen transcrito de un estudiante basándote estrictamente "
            "en el contexto del Currículo Nacional (CNEB) provisto.\n"
            "Debes retornar OBLIGATORIAMENTE un JSON que cumpla exactamente con estas llaves:\n"
            "{\n"
            "  \"nota\": \"(Logro Destacado (AD) / Logro Esperado (A) / En Proceso (B) / En Inicio (C))\",\n"
            "  \"criterio_citado\": \"(Menciona la competencia/capacidad exacta del CNEB aplicada)\",\n"
            "  \"feedback\": \"(Retroalimentación formativa y empática sobre errores y aciertos)\"\n"
            "}"
        )

        user_content = (
            f"Contexto CNEB Oficial:\n{contexto_cneb}\n\n"
            f"Transcripción del Examen del Alumno:\n{ocr_text}"
        )

        try:
            # Llamada síncrona/bloqueante a Anthropic envuelta para el flujo
            message = self.client.messages.create(
                model="claude-3-5-haiku-20241022", # Ajustado al identificador disponible de Haiku
                max_tokens=1000,
                temperature=0.2,
                system=system_prompt,
                messages=[{"role": "user", "content": user_content}]
            )
            
            raw_text = message.content[0].text
            
            # Limpiar posibles bloques de formato markdown de la IA
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            
            # Validar e instanciar usando Pydantic para garantizar robustez
            import json
            parsed = json.loads(raw_text)
            
            return EvaluacionResponse(
                alumno_id=alumno_id,
                nombre_alumno=nombre_alumno,
                nota=parsed.get("nota", "En Proceso (B)"),
                criterio_citado=parsed.get("criterio_citado", contexto_cneb[:150]),
                feedback=parsed.get("feedback", "Buen intento. Sigue practicando."),
                transcripcion_ocr=ocr_text
            )
        except Exception as e:
            logger.error("Error crítico en Claude Evaluator, aplicando Fallback a formato básico", error=str(e))
            return EvaluacionResponse(
                alumno_id=alumno_id,
                nombre_alumno=nombre_alumno,
                nota="En Proceso (B)",
                criterio_citado="Evaluación curricular general",
                feedback="Se generó una alerta en el procesamiento analítico. El docente revisará manualmente.",
                transcripcion_ocr=ocr_text
            )