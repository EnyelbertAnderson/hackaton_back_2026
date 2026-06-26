# app/main.py
"""FastAPI app + registro de rutas. HOTSPOT: solo Dev A."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import routes_evaluar, routes_aula

app = FastAPI(
    title="Ñawi API",
    description="Pipeline agéntico para evaluación formativa de exámenes manuscritos.",
    version="1.0.0"
)

# Configuración de CORS obligatoria para desarrollo/hackathon
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modificar en producción si es necesario
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de los routers
app.include_router(routes_evaluar.router)
app.include_router(routes_aula.router)

@app.get("/")
async def root():
    return {"status": "online", "proyecto": "Ñawi"}