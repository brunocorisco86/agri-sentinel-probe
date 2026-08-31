import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_healthcheck(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_telemetry_without_auth(client: AsyncClient):
    payload = {
        "device_id": "SENTINEL-TEST1",
        "device_mac": "AA:BB:CC:DD:EE:01"
    }
    response = await client.post("/api/v1/telemetry", json=payload)
    assert response.status_code in [401, 403]

@pytest.mark.asyncio
async def test_telemetry_ingestion_and_devices(client: AsyncClient, auth_headers: dict):
    payload = {
        "device_id": "SENTINEL-TEST1",
        "device_mac": "AA:BB:CC:DD:EE:01",
        "location_name": "Granja Aviario 01",
        "hardware_model": "LilyGO T-Display-S3",
        "firmware_version": "1.0.0",
        "uptime_seconds": 120,
        "wifi_ssid": "Granja_WiFi",
        "wifi_rssi_dbm": -65,
        "local_target_enabled": True,
        "local_target_ip": "192.168.1.50",
        "local_target_online": True,
        "local_target_rtt_ms": 4.5,
        "free_heap_bytes": 180000
    }
    
    # Ingestão
    response = await client.post("/api/v1/telemetry", json=payload, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "OK"
    assert data["device_id"] == "SENTINEL-TEST1"
    
    # Listagem de Dispositivos
    dev_res = await client.get("/api/v1/devices")
    assert dev_res.status_code == 200
    devices = dev_res.json()
    assert len(devices) == 1
    assert devices[0]["device_id"] == "SENTINEL-TEST1"
    assert devices[0]["status"] == "ONLINE"
    assert devices[0]["location_name"] == "Granja Aviario 01"

@pytest.mark.asyncio
async def test_telemetry_lan_failure_incident(client: AsyncClient, auth_headers: dict):
    payload = {
        "device_id": "SENTINEL-TEST2",
        "device_mac": "AA:BB:CC:DD:EE:02",
        "location_name": "Granja Aviario 02",
        "hardware_model": "ESP32-C3 SuperMini",
        "firmware_version": "1.0.0",
        "uptime_seconds": 300,
        "local_target_enabled": True,
        "local_target_ip": "192.168.1.50",
        "local_target_online": False,  # Falha no gateway Dragino
        "local_target_rtt_ms": -1.0,
        "free_heap_bytes": 150000
    }
    
    response = await client.post("/api/v1/telemetry", json=payload, headers=auth_headers)
    assert response.status_code == 200
    
    # Verifica que incidente foi criado
    inc_res = await client.get("/api/v1/incidents")
    assert inc_res.status_code == 200
    incidents = inc_res.json()
    assert len(incidents) == 1
    assert incidents[0]["incident_type"] == "GATEWAY_LAN_FAILURE"
    assert incidents[0]["status"] == "OPEN"
    
    # Summary
    summary_res = await client.get("/api/v1/devices/summary")
    assert summary_res.status_code == 200
    summary = summary_res.json()
    assert summary["total_devices"] == 1
    assert summary["lan_failure_count"] == 1
