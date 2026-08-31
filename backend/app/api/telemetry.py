import datetime
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.core.database import get_db
from app.api.dependencies import verify_api_token
from app.schemas.telemetry import TelemetryPayload, TelemetryResponse
from app.models.device import Device
from app.models.telemetry import Telemetry
from app.models.incident import Incident
from app.services.classifier import classify_device_state, STATE_ONLINE, STATE_LAN_FAILURE

router = APIRouter(prefix="/telemetry", tags=["Telemetria"])

@router.post("", response_model=TelemetryResponse, dependencies=[Depends(verify_api_token)])
async def receive_telemetry(payload: TelemetryPayload, db: AsyncSession = Depends(get_db)):
    now = datetime.datetime.utcnow()
    
    # 1. Classificação do estado da sonda
    status_code, desc = classify_device_state(
        is_alive=True,
        local_target_enabled=payload.local_target_enabled,
        local_target_online=payload.local_target_online
    )
    
    # 2. Busca ou cria o registro do Device
    query = select(Device).where(Device.device_id == payload.device_id)
    result = await db.execute(query)
    device = result.scalars().first()
    
    if not device:
        device = Device(
            device_id=payload.device_id,
            device_mac=payload.device_mac,
            location_name=payload.location_name,
            hardware_model=payload.hardware_model,
            firmware_version=payload.firmware_version,
            status=status_code,
            last_seen_at=now,
            wifi_ssid=payload.wifi_ssid,
            wifi_rssi_dbm=payload.wifi_rssi_dbm,
            local_target_enabled=payload.local_target_enabled,
            local_target_ip=payload.local_target_ip,
            local_target_online=payload.local_target_online,
            local_target_rtt_ms=payload.local_target_rtt_ms,
            local_target_mac=payload.local_target_mac,
            uptime_seconds=payload.uptime_seconds,
            free_heap_bytes=payload.free_heap_bytes,
        )
        db.add(device)
    else:
        # Atualiza métricas
        device.location_name = payload.location_name
        device.hardware_model = payload.hardware_model
        device.firmware_version = payload.firmware_version
        device.status = status_code
        device.last_seen_at = now
        device.wifi_ssid = payload.wifi_ssid
        device.wifi_rssi_dbm = payload.wifi_rssi_dbm
        device.local_target_enabled = payload.local_target_enabled
        device.local_target_ip = payload.local_target_ip
        device.local_target_online = payload.local_target_online
        device.local_target_rtt_ms = payload.local_target_rtt_ms
        device.local_target_mac = payload.local_target_mac
        device.uptime_seconds = payload.uptime_seconds
        device.free_heap_bytes = payload.free_heap_bytes

    # 3. Registra ponto histórico de telemetria
    telemetry = Telemetry(
        device_id=payload.device_id,
        wifi_rssi_dbm=payload.wifi_rssi_dbm,
        local_target_online=payload.local_target_online,
        local_target_rtt_ms=payload.local_target_rtt_ms,
        free_heap_bytes=payload.free_heap_bytes,
        uptime_seconds=payload.uptime_seconds,
        received_at=now
    )
    db.add(telemetry)
    
    # 4. Gestão de Incidentes (Auto-recovery ou abertura)
    if status_code == STATE_LAN_FAILURE:
        # Verifica se já existe incidente de LAN aberto
        inc_q = select(Incident).where(
            and_(Incident.device_id == payload.device_id, Incident.status == "OPEN")
        )
        inc_res = await db.execute(inc_q)
        if not inc_res.scalars().first():
            inc = Incident(
                device_id=payload.device_id,
                incident_type="GATEWAY_LAN_FAILURE",
                status="OPEN",
                description=f"Gateway Dragino ({payload.local_target_ip}) inacessivel na rede local de '{payload.location_name}'.",
                opened_at=now
            )
            db.add(inc)
    elif status_code == STATE_ONLINE:
        # Auto-Recovery: fecha qualquer incidente em aberto para esta sonda
        inc_q = select(Incident).where(
            and_(Incident.device_id == payload.device_id, Incident.status == "OPEN")
        )
        inc_res = await db.execute(inc_q)
        for inc in inc_res.scalars().all():
            inc.status = "RESOLVED"
            inc.resolved_at = now
            
    await db.commit()
    
    return TelemetryResponse(
        status="OK",
        message=f"Telemetria processada. Estado: {status_code}",
        device_id=payload.device_id,
        server_time=now
    )
