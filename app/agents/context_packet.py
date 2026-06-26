"""Schema del JSON que viaja entre agentes. Cambiar aquí rompe todo lo demás."""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


# ── Sub-modelos por agente ───────────────────────────────────────────────────

class ImageData(BaseModel):
    image_id: str
    raw_bytes: bytes  # se descarta después de vision (privacidad de menores)

    model_config = {"arbitrary_types_allowed": True}


class OCRResult(BaseModel):
    text: str                          # transcripción literal — sin corregir ortografía
    alumno_nombre: Optional[str] = None  # None si ilegible


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
    confidence: float              # 0.0 – 1.0
    needs_review: bool
    motivo: Optional[str] = None  # por qué se deriva a revisión humana


class DiagnosticResult(BaseModel):
    errores_comunes: list[str] = Field(default_factory=list)
    cluster_label: Optional[str] = None


# ── Packet principal ─────────────────────────────────────────────────────────

class ContextPacket(BaseModel):
    exam_id: str        # UUID generado en el endpoint (era session_id)
    student_id: str     # identificador del alumno
    docente_id: str = "demo"

    image: Optional[ImageData] = None
    ocr: Optional[OCRResult] = None
    evaluation: Optional[EvaluationResult] = None
    verification: Optional[VerificationResult] = None
    diagnostic: Optional[DiagnosticResult] = None

    retrieved_context: list[str] = Field(default_factory=list)
    stage: str = "input"  # input | vision | evaluator | verifier | diagnostic | done

    def descartar_imagen(self) -> None:
        """La imagen no se propaga más allá de vision."""
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
