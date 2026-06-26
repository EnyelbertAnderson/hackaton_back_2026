"""Schema del JSON que viaja entre agentes. HOTSPOT: cambiar aquí rompe todo lo demás."""
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class RubricaCriterio(BaseModel):
    criterio: str                  # e.g. "Comprensión lectora"
    puntaje_max: float
    descriptor: str                # qué espera el docente


class ItemEvaluado(BaseModel):
    pregunta_id: str               # "1a", "2", etc.
    texto_alumno: str              # transcripción literal de vision (sin corregir)
    criterio: RubricaCriterio
    puntaje_obtenido: Optional[float] = None
    feedback: Optional[str] = None
    cneb_referencia: Optional[str] = None   # fragmento del CNEB citado por evaluator


class ContextPacket(BaseModel):
    # ── Identificación ──────────────────────────────────────────────
    exam_id: str                           # UUID generado en el endpoint
    alumno_nombre: Optional[str] = None    # extraído del encabezado por vision; None si ilegible
    docente_id: str

    # ── Input de vision ─────────────────────────────────────────────
    imagen_base64: Optional[str] = None    # solo presente antes de vision; se descarta al salir
    ocr_raw: Optional[str] = None          # transcripción cruda completa (letra del alumno)

    # ── Rúbrica cargada por el docente ──────────────────────────────
    rubrica: list[RubricaCriterio] = Field(default_factory=list)

    # ── Output de evaluator ─────────────────────────────────────────
    items: list[ItemEvaluado] = Field(default_factory=list)
    score_total: Optional[float] = None
    score_max: Optional[float] = None

    # ── Output de verifier ──────────────────────────────────────────
    confidence: Optional[float] = None     # 0.0 – 1.0
    needs_review: bool = False
    review_motivo: Optional[str] = None    # por qué se derivó a revisión humana

    # ── Etapa actual (para trazabilidad) ────────────────────────────
    stage: str = "input"   # input | vision | evaluator | verifier | diagnostic | done

    def descartar_imagen(self) -> None:
        """La imagen no se propaga más allá de vision (privacidad de menores)."""
        self.imagen_base64 = None
