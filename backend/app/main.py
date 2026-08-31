import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.api.telemetry import router as telemetry_router
from app.api.devices import router as devices_router
from app.api.incidents import router as incidents_router
from app.services.deadman_switch import deadman_switch_worker

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialização do Banco de Dados
    await init_db()
    
    # Inicia Worker Assíncrono do Dead Man's Switch
    worker_task = asyncio.create_task(deadman_switch_worker())
    
    yield
    
    # Cancelamento limpo do worker no shutdown
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Keepalive Foresight - API Central de Monitoramento de Sondas WAN/LAN (C.Vale)",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(telemetry_router, prefix=settings.API_V1_STR)
app.include_router(devices_router, prefix=settings.API_V1_STR)
app.include_router(incidents_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Healthcheck"])
async def healthcheck():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }
