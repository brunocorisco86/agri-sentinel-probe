import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.device import Device
from app.models.incident import Incident
from app.services.telegram_bot import send_telegram_alert

router = APIRouter(prefix="/reports", tags=["Relatórios"])

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
