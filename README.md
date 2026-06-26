# Ñawi — Plataforma de Inteligencia Pedagógica

## Requisitos
- Python 3.11+
- Google AI Studio API Key (para OCR con Gemini)
- Anthropic API Key (para evaluación, verificación y diagnóstico)

## Instalación y ejecución

```bash
# 1. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows

# 2. Instalar dependencias
pip install fastapi uvicorn anthropic google-genai chromadb \
            pydantic pydantic-settings structlog python-multipart \
            python-dotenv

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys reales

# 4. Indexar el CNEB en ChromaDB (solo la primera vez)
python -m app.scripts.indexar_cneb

# 5. Levantar el servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints

### POST /evaluar
Evalúa un examen manuscrito fotografiado.

```bash
curl -X POST http://localhost:8000/evaluar \
  -F "image=@examen.jpg" \
  -F "student_id=ALU-001" \
  -F "session_id=SESION-2026-01" \
  -F "docente_id=DOC-001"
```

### GET /aula/{aula_id}/diagnostico
Diagnóstico consolidado del aula.

```bash
curl http://localhost:8000/aula/5A/diagnostico
```

## Pipeline de agentes
1. **Vision** (Gemini Flash-Lite) → OCR del examen manuscrito
2. **Evaluator** (Claude Haiku + RAG) → Puntaje y feedback personalizado
3. **Verifier** (Claude Haiku) → Coherencia entre nota y respuesta
4. **Diagnostic** (Claude Haiku) → Clasificación y errores del estudiante

## Docs interactivas
Una vez levantado: http://localhost:8000/docs
