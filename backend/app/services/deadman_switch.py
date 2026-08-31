import asyncio
import datetime
from sqlalchemy import select, and_
from app.core.config import settings
from app.core.database import async_session_factory
from app.models.device import Device
from app.models.incident import Incident
from app.services.classifier import STATE_WAN_TIMEOUT, STATE_ONLINE, STATE_LAN_FAILURE

async def check_deadman_switch_cycle():
    """Executa uma rodada de verificação de timeouts nas sondas."""
    async with async_session_factory() as session:
        now = datetime.datetime.utcnow()
        timeout_threshold = now - datetime.timedelta(seconds=settings.DEADMAN_TIMEOUT_SECONDS)
        
        # Busca dispositivos que não enviaram heartbeat e não estão marcados como WAN_TIMEOUT
        query = select(Device).where(
            and_(
                Device.last_seen_at < timeout_threshold,
                Device.status.in_([STATE_ONLINE, STATE_LAN_FAILURE])
            )
        )
        result = await session.execute(query)
        timed_out_devices = result.scalars().all()
        
        for dev in timed_out_devices:
            dev.status = STATE_WAN_TIMEOUT
            
            # Abre incidente se não houver um incidente aberto
            inc_query = select(Incident).where(
                and_(
                    Incident.device_id == dev.device_id,
                    Incident.status == "OPEN"
                )
            )
            inc_res = await session.execute(inc_query)
            existing_inc = inc_res.scalars().first()
            
            if not existing_inc:
                incident = Incident(
                    device_id=dev.device_id,
                    incident_type="WAN_TIMEOUT",
                    status="OPEN",
                    description=f"Sonda em '{dev.location_name}' parou de se comunicar com a VPS ha mais de {settings.DEADMAN_TIMEOUT_SECONDS}s.",
                    opened_at=now
                )
                session.add(incident)
                
        if timed_out_devices:
            await session.commit()

async def deadman_switch_worker():
    """Worker em background contínuo."""
    while True:
        try:
            await check_deadman_switch_cycle()
        except Exception as e:
            print(f"[DeadMan Worker Error] {e}")
        await asyncio.sleep(settings.DEADMAN_INTERVAL_SECONDS)
