from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

class TelemetryPayload(BaseModel):
    device_id: str = Field(..., description="Identificador único da sonda (Ex: SENTINEL-A1B2)")
    device_mac: str = Field(..., description="Endereço MAC físico da interface Wi-Fi")
    location_name: str = Field("Ponto Nao Identificado", description="Nome amigável da localidade")
    hardware_model: str = Field("ESP32 Generic", description="Modelo da placa (LilyGO / C3)")
    firmware_version: str = Field("1.0.0", description="Versão do firmware")
    uptime_seconds: int = Field(0, ge=0, description="Tempo de atividade em segundos")
    wifi_ssid: Optional[str] = None
    wifi_rssi_dbm: Optional[int] = None
    local_target_enabled: bool = False
    local_target_ip: Optional[str] = None
    local_target_online: bool = True
    local_target_rtt_ms: float = 0.0
    local_target_mac: Optional[str] = None
    free_heap_bytes: int = Field(0, ge=0)

class TelemetryResponse(BaseModel):
    status: str
    message: str
    device_id: str
    server_time: datetime
