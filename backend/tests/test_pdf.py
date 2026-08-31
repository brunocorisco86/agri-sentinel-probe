import pytest
from app.services.pdf_generator import generate_executive_pdf_report

@pytest.mark.asyncio
async def test_generate_executive_pdf():
    mock_data = [
        {
            "device_id": "SENTINEL-TEST1",
            "location_name": "Granja 01 - Silos",
            "hardware_model": "LilyGO T-Display-S3",
            "telemetries": [
                {"received_at": "2026-08-31T15:00:00", "local_target_rtt_ms": 3.2, "wifi_rssi_dbm": -42, "local_target_online": True}
            ],
            "incidents": []
        }
    ]
    
    pdf_buffer = await generate_executive_pdf_report(mock_data, days=7)
    pdf_bytes = pdf_buffer.getvalue()
    
    assert len(pdf_bytes) > 1000
    assert pdf_bytes.startswith(b"%PDF")
