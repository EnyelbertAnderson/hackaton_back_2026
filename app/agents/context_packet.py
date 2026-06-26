# app/agents/context_packet.py
from pydantic import BaseModel
from typing import List, Optional

class ExamenBase(BaseModel):
    alumno_id: str
    nombre_alumno: str

class EvaluacionResponse(ExamenBase):
    nota: str
    criterio_citado: str
    feedback: str
    transcripcion_ocr: Optional[str] = None

class DiagnosticoAulaResponse(BaseModel):
    aula_id: str
    errores_comunes: List[str]
    puntos_fuertes: List[str]
    recomendaciones_cneb: List[str]
    resumen_rendimiento: str