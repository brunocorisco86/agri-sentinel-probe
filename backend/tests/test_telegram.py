import pytest
from unittest.mock import patch, AsyncMock
from app.services.telegram_bot import send_telegram_alert
from app.core.config import settings

@pytest.mark.asyncio
async def test_send_telegram_alert_disabled():
    # Sem tokens configurados deve retornar False sem erro
    with patch.object(settings, "TELEGRAM_BOT_TOKEN", ""), patch.object(settings, "TELEGRAM_CHAT_ID", ""):
        res = await send_telegram_alert(
            event_type="WAN_TIMEOUT",
            location_name="Granja 01",
            device_id="SENTINEL-1",
            description="Queda de link rural"
        )
        assert res is False

@pytest.mark.asyncio
async def test_send_telegram_alert_success():
    with patch.object(settings, "TELEGRAM_BOT_TOKEN", "mock-token"),          patch.object(settings, "TELEGRAM_CHAT_ID", "mock-chat"),          patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        
        mock_post.return_value.status_code = 200
        
        res = await send_telegram_alert(
            event_type="GATEWAY_LAN_FAILURE",
            location_name="Granja Aviario 01",
            device_id="SENTINEL-GR01",
            description="Dragino inacessivel",
            extra_info={"IP Dragino": "192.168.1.50"}
        )
        assert res is True
        assert mock_post.called
