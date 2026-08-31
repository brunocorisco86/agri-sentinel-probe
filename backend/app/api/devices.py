from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.schemas.device import DeviceResponse, DeviceSummary
from app.models.device import Device
from app.services.classifier import STATE_ONLINE, STATE_LAN_FAILURE, STATE_WAN_TIMEOUT

router = APIRouter(prefix="/devices", tags=["Dispositivos"])

@router.get("", response_model=List[DeviceResponse])
async def list_devices(db: AsyncSession = Depends(get_db)):
    query = select(Device).order_by(Device.location_name)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/summary", response_model=DeviceSummary)
async def get_devices_summary(db: AsyncSession = Depends(get_db)):
    query = select(Device).order_by(Device.location_name)
    result = await db.execute(query)
    devices = result.scalars().all()
    
    total = len(devices)
    online = sum(1 for d in devices if d.status == STATE_ONLINE)
    lan_fail = sum(1 for d in devices if d.status == STATE_LAN_FAILURE)
    wan_timeout = sum(1 for d in devices if d.status == STATE_WAN_TIMEOUT)
    
    return DeviceSummary(
        total_devices=total,
        online_count=online,
        lan_failure_count=lan_fail,
        wan_timeout_count=wan_timeout,
        devices=devices
    )

@router.get("/{device_id}/status", response_model=DeviceResponse)
async def get_device_status(device_id: str, db: AsyncSession = Depends(get_db)):
    query = select(Device).where(Device.device_id == device_id)
    result = await db.execute(query)
    device = result.scalars().first()
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dispositivo nao encontrado")
    return device
