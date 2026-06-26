# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import routes_evaluar, routes_aula, routes_process
from .agents.context_packet import HealthResponse

app = FastAPI(
    title="Ñawi API",
    description="Pipeline agéntico para evaluación formativa de exámenes manuscritos.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_process.router)   # /api/evaluations/process  ← front
app.include_router(routes_evaluar.router)   # /evaluar                  ← individual
app.include_router(routes_aula.router)      # /aula/{id}/diagnostico

@app.get("/health", response_model=HealthResponse, tags=["Sistema"])
async def health():
    return HealthResponse(
        status="online",
        version="1.0.0",
        agentes=["vision", "evaluator", "verifier", "diagnostic"],
    )

@app.get("/", tags=["Sistema"])
async def root():
    return {"status": "online", "proyecto": "Ñawi", "docs": "/docs"}
