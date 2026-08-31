from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.schemas.incident import IncidentResponse
from app.models.incident import Incident

router = APIRouter(prefix="/incidents", tags=["Incidentes"])

@router.get("", response_model=List[IncidentResponse])
async def list_incidents(db: AsyncSession = Depends(get_db)):
    query = select(Incident).order_by(Incident.opened_at.desc())
    result = await db.execute(query)
    return result.scalars().all()
