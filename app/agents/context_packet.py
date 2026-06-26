# app/agents/context_packet.py
"""Schema del JSON que viaja entre agentes. Cambiar aquí rompe todo lo demás."""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


# ── Sub-modelos internos del pipeline ────────────────────────────────────────

class ImageData(BaseModel):
    image_id: str
    raw_bytes: bytes  # se descarta después de vision (privacidad de menores)
    mime_type: str = "image/jpeg"  # image/jpeg, image/png, application/pdf
    model_config = {"arbitrary_types_allowed": True}


class OCRResult(BaseModel):
    text: str
    alumno_nombre: Optional[str] = None


class RubricMatch(BaseModel):
    competence_id: str
    expected_criteria: str
    matched_evidence: list[str]
    score: float
    justification: str


class EvaluationResult(BaseModel):
    total_score: float
    score_max: float = 20.0
    feedback: str
    rubric_matches: list[RubricMatch] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)


class VerificationResult(BaseModel):
    is_consistent: bool
    confidence: float
    needs_review: bool
    motivo: Optional[str] = None


class DiagnosticResult(BaseModel):
    errores_comunes: list[str] = Field(default_factory=list)
    cluster_label: Optional[str] = None


class ContextPacket(BaseModel):
    exam_id: str
    student_id: str
    docente_id: str = "demo"
    image: Optional[ImageData] = None
    ocr: Optional[OCRResult] = None
    evaluation: Optional[EvaluationResult] = None
    verification: Optional[VerificationResult] = None
    diagnostic: Optional[DiagnosticResult] = None
    retrieved_context: list[str] = Field(default_factory=list)
    stage: str = "input"

    def descartar_imagen(self) -> None:
        self.image = None

    def get_pipeline_state(self) -> dict:
        return {
            "stage": self.stage,
            "has_ocr": self.ocr is not None,
            "has_evaluation": self.evaluation is not None,
            "has_verification": self.verification is not None,
            "has_diagnostic": self.diagnostic is not None,
        }

    model_config = {"arbitrary_types_allowed": True}


# ── Response models (lo que devuelven los endpoints al frontend) ──────────────

class RubricMatchOut(BaseModel):
    competence_id: str
    expected_criteria: str
    matched_evidence: list[str]
    score: float
    justification: str


class DiagnosticOut(BaseModel):
    errores_comunes: list[str]
    cluster_label: Optional[str]


class EvaluarResponse(BaseModel):
    """Respuesta de POST /evaluar"""
    exam_id: str
    student_id: str
    alumno_nombre: Optional[str]
    score: float
    score_max: float
    feedback: str
    strengths: list[str]
    weaknesses: list[str]
    rubric_matches: list[RubricMatchOut]
    needs_review: bool
    confidence: float
    diagnostic: DiagnosticOut
    pipeline_state: dict


class DiagnosticoAulaResponse(BaseModel):
    """Respuesta de GET /aula/{aula_id}/diagnostico"""
    aula_id: str
    errores_comunes: list[str]
    puntos_fuertes: list[str]
    recomendaciones_cneb: list[str]
    resumen_rendimiento: str


class HealthResponse(BaseModel):
    """Respuesta de GET /health"""
    status: str
    version: str
    agentes: list[str]


# ── Alias legacy (usado internamente por verifier/diagnostic) ─────────────────

class EvaluacionResponse(BaseModel):
    alumno_id: str = ""
    nombre_alumno: str = ""
    nota: str = ""
    criterio_citado: str = ""
    feedback: str = ""
    transcripcion_ocr: str = ""
