import asyncio
import datetime
from sqlalchemy import select
from app.core.config import settings
from app.core.database import async_session_factory
from app.models.device import Device
from app.models.incident import Incident
from app.services.classifier import STATE_WAN_TIMEOUT, STATE_ONLINE, STATE_LAN_FAILURE
from app.services.telegram_bot import send_telegram_alert

async def check_deadman_switch_cycle():
    """Executa uma rodada de verificação de timeouts adaptativa para cada sonda."""
    async with async_session_factory() as session:
        now = datetime.datetime.utcnow()
        
        query = select(Device).where(
            Device.status.in_([STATE_ONLINE, STATE_LAN_FAILURE])
        )
        result = await session.execute(query)
        active_devices = result.scalars().all()
        
        timed_out_devices = []
        for dev in active_devices:
            device_timeout = max((dev.check_interval_seconds or 300) * 2.5, 60.0)
            threshold = now - datetime.timedelta(seconds=device_timeout)
            
            if dev.last_seen_at < threshold:
                dev.status = STATE_WAN_TIMEOUT
                timed_out_devices.append(dev)
                
                inc_query = select(Incident).where(
                    (Incident.device_id == dev.device_id) & (Incident.status == "OPEN")
                )
                inc_res = await session.execute(inc_query)
                if not inc_res.scalars().first():
                    desc = f"Sonda sem resposta na nuvem ha mais de {int(device_timeout/60)} minutos (timeout de telemetria)."
                    incident = Incident(
                        device_id=dev.device_id,
                        incident_type="WAN_TIMEOUT",
                        status="OPEN",
                        description=desc,
                        opened_at=now
                    )
                    session.add(incident)
                    
                    # Dispara alerta assíncrono no Telegram
                    asyncio.create_task(send_telegram_alert(
                        event_type="WAN_TIMEOUT",
                        location_name=dev.location_name,
                        device_id=dev.device_id,
                        description=desc,
                        extra_info={
                            "Hardware": dev.hardware_model,
                            "Ultimo RSSI": f"{dev.wifi_rssi_dbm} dBm" if dev.wifi_rssi_dbm else "N/A",
                            "Intervalo": f"{int((dev.check_interval_seconds or 300)/60)} min"
                        }
                    ))
                    
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
