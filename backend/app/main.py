import asyncio
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import init_db
from app.api.telemetry import router as telemetry_router
from app.api.devices import router as devices_router
from app.api.incidents import router as incidents_router
from app.api.reports import router as reports_router
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
app.include_router(reports_router, prefix=settings.API_V1_STR)

TEMPLATE_PATH = Path(__file__).parent / "templates" / "dashboard.html"

@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/dashboard")

@app.get("/dashboard", response_class=HTMLResponse, tags=["Dashboard"])
async def serve_dashboard():
    if TEMPLATE_PATH.exists():
        return HTMLResponse(content=TEMPLATE_PATH.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Dashboard template not found</h1>", status_code=404)

@app.get("/health", tags=["Healthcheck"])
async def healthcheck():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }
