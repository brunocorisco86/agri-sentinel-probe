import io
import datetime
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.core.database import get_db
from app.models.device import Device
from app.models.telemetry import Telemetry
from app.models.incident import Incident
from app.services.telegram_bot import send_telegram_alert
from app.services.pdf_generator import generate_executive_pdf_report

router = APIRouter(prefix="/reports", tags=["Relatórios"])

@router.get("/pdf")
async def get_executive_pdf_report(
    days: int = Query(7, description="Período em dias para o relatório (Ex: 7 ou 30)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Gera e exporta relatório executivo em formato PDF para os últimos 7 ou 30 dias (1 sonda por página com série temporal e IA).
    """
    now = datetime.datetime.utcnow()
    since_date = now - datetime.timedelta(days=days)
    
    # 1. Busca dispositivos
    dev_query = select(Device)
    dev_res = await db.execute(dev_query)
    devices = dev_res.scalars().all()
    
    devices_data = []
    for dev in devices:
        # Busca telemetrias recentes do dispositivo
        tel_query = select(Telemetry).where(
            and_(
                Telemetry.device_id == dev.device_id,
                Telemetry.received_at >= since_date
            )
        ).order_by(Telemetry.received_at.asc())
        tel_res = await db.execute(tel_query)
        telemetries = [
            {
                "received_at": t.received_at,
                "local_target_rtt_ms": t.local_target_rtt_ms,
                "wifi_rssi_dbm": t.wifi_rssi_dbm,
                "local_target_online": t.local_target_online
            }
            for t in tel_res.scalars().all()
        ]
        
        # Busca incidentes no período
        inc_query = select(Incident).where(
            and_(
                Incident.device_id == dev.device_id,
                Incident.opened_at >= since_date
            )
        )
        inc_res = await db.execute(inc_query)
        incidents = inc_res.scalars().all()
        
        devices_data.append({
            "device": dev,
            "device_id": dev.device_id,
            "location_name": dev.location_name,
            "hardware_model": dev.hardware_model,
            "telemetries": telemetries,
            "incidents": incidents
        })
        
    pdf_buffer = await generate_executive_pdf_report(devices_data, days=days)
    
    filename = f"keepalive_relatorio_executivo_{days}d.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/daily-telegram")
async def generate_daily_telegram_report(db: AsyncSession = Depends(get_db)):
    """
    Gera e dispara um relatório executivo de conectividade consolidado para o Telegram Bot.
    """
    now = datetime.datetime.utcnow()
    
    query = select(Device)
    result = await db.execute(query)
    devices = result.scalars().all()
    
    total = len(devices)
    online_count = sum(1 for d in devices if d.status == "ONLINE")
    lan_fail_count = sum(1 for d in devices if d.status == "LAN_FAILURE")
    wan_timeout_count = sum(1 for d in devices if d.status == "WAN_TIMEOUT")
    
    health_pct = (online_count / total * 100.0) if total > 0 else 100.0
    
    details = {
        "📊 Total de Pontos": f"{total} sondas",
        "🟢 100% Operacionais": f"{online_count}",
        "⚠️ Falhas de Dragino": f"{lan_fail_count}",
        "🚨 Quedas de Link WAN": f"{wan_timeout_count}",
        "📈 Índice de Saúde": f"{health_pct:.1f}%"
    }
    
    desc = f"Relatório executivo matinal de monitoramento das granjas e pontos C.Vale ({now.strftime('%d/%m/%Y %H:%M UTC')})."
    
    success = await send_telegram_alert(
        event_type="RECOVERY" if lan_fail_count == 0 and wan_timeout_count == 0 else "WAN_TIMEOUT",
        location_name="Consolidado Granja & NOC",
        device_id="NOC-REPORT-DAILY",
        description=desc,
        extra_info=details
    )
    
    return {
        "status": "OK" if success else "NOT_SENT",
        "message": "Relatório diário enviado para o Telegram com sucesso!" if success else "Falha ao enviar para o Telegram (verifique credenciais).",
        "metrics": {
            "total": total,
            "online": online_count,
            "lan_failures": lan_fail_count,
            "wan_timeouts": wan_timeout_count,
            "health_percentage": health_pct
        }
    }
