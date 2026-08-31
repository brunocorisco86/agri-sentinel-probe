from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from app.core.config import settings
from app.core.database import get_db
from app.models.device import Device
from app.models.telemetry import Telemetry
from app.models.incident import Incident

router = APIRouter(prefix="/admin", tags=["Administração"])

class ResetDBRequest(BaseModel):
    admin_password: str

@router.post("/reset-database")
async def reset_database(payload: ResetDBRequest, db: AsyncSession = Depends(get_db)):
    """
    Limpa completamente todas as tabelas (telemetrias, incidentes e dispositivos) para iniciar a produção do zero.
    Requer autenticação com senha de administrador.
    """
    if payload.admin_password != settings.ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha de administrador incorreta."
        )
        
    # Limpa as tabelas
    await db.execute(delete(Telemetry))
    await db.execute(delete(Incident))
    await db.execute(delete(Device))
    await db.commit()
    
    # Otimiza arquivo SQLite
    if "sqlite" in settings.DATABASE_URL:
        try:
            await db.exec_driver_sql("VACUUM;")
        except Exception:
            pass
            
    return {
        "status": "OK",
        "message": "Banco de dados limpo com sucesso! Todas as tabelas foram reiniciadas do zero para início de produção."
    }
