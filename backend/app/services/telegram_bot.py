import httpx
from typing import Optional
from app.core.config import settings

async def send_telegram_alert(
    event_type: str,
    location_name: str,
    device_id: str,
    description: str,
    extra_info: Optional[dict] = None
) -> bool:
    """
    Dispara notificações formatadas em HTML para o grupo de TI/Manutenção via Telegram Bot.
    """
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_CHAT_ID:
        return False
        
    icons = {
        "WAN_TIMEOUT": "🚨 <b>[ALERTA DE QUEDA WAN / LINK RURAL]</b>",
        "GATEWAY_LAN_FAILURE": "⚠️ <b>[FALHA LOCAL NO GATEWAY DRAGINO]</b>",
        "BLACKOUT_GENERAL": "⚡ <b>[ALERTA CRÍTICO: SUSPEITA DE BLECAUTE]</b>",
        "RECOVERY": "🟢 <b>[CONEXÃO RESTABELECIDA - AUTO RECOVERY]</b>"
    }
    
    header = icons.get(event_type, "ℹ️ <b>[NOTIFICAÇÃO DE TELEMETRIA]</b>")
    
    msg_lines = [
        header + "\n",
        f"📍 <b>Ponto / Granja:</b> <code>{location_name}</code>",
        f"📟 <b>ID da Sonda:</b> <code>{device_id}</code>",
        f"📝 <b>Diagnóstico:</b> {description}\n"
    ]
    
    if extra_info:
        for k, v in extra_info.items():
            msg_lines.append(f"• <b>{k}:</b> <code>{v}</code>")
            
    text = "\n".join(msg_lines)
    
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.post(url, json=payload)
            return res.status_code == 200
    except Exception as e:
        print(f"[Telegram Alert Error] Falha ao enviar alerta: {e}")
        return False
