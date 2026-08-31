import asyncio
import datetime
from sqlalchemy import select
from app.core.config import settings
from app.core.database import async_session_factory
from app.models.device import Device
from app.models.incident import Incident
from app.services.classifier import STATE_WAN_TIMEOUT, STATE_ONLINE, STATE_LAN_FAILURE

async def check_deadman_switch_cycle():
    """Executa uma rodada de verificação de timeouts adaptativa para cada sonda."""
    async with async_session_factory() as session:
        now = datetime.datetime.utcnow()
        
        # Busca todos os dispositivos atualmente online ou com falha LAN
        query = select(Device).where(
            Device.status.in_([STATE_ONLINE, STATE_LAN_FAILURE])
        )
        result = await session.execute(query)
        active_devices = result.scalars().all()
        
        timed_out_devices = []
        for dev in active_devices:
            # Tolerância dinâmica: 2.5x o intervalo de heartbeat configurado (mínimo 60s)
            device_timeout = max((dev.check_interval_seconds or 300) * 2.5, 60.0)
            threshold = now - datetime.timedelta(seconds=device_timeout)
            
            if dev.last_seen_at < threshold:
                dev.status = STATE_WAN_TIMEOUT
                timed_out_devices.append(dev)
                
                # Abre incidente se não houver um incidente aberto
                inc_query = select(Incident).where(
                    (Incident.device_id == dev.device_id) & (Incident.status == "OPEN")
                )
                inc_res = await session.execute(inc_query)
                if not inc_res.scalars().first():
                    incident = Incident(
                        device_id=dev.device_id,
                        incident_type="WAN_TIMEOUT",
                        status="OPEN",
                        description=f"Sonda em '{dev.location_name}' sem resposta ha mais de {int(device_timeout/60)} minutos.",
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
