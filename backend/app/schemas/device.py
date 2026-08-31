from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class DeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    device_id: str
    device_mac: str
    location_name: str
    hardware_model: str
    firmware_version: str
    status: str
    last_seen_at: datetime
    wifi_ssid: Optional[str] = None
    wifi_rssi_dbm: Optional[int] = None
    local_target_enabled: bool
    local_target_ip: Optional[str] = None
    local_target_online: bool
    local_target_rtt_ms: float
    local_target_mac: Optional[str] = None
    uptime_seconds: int
    free_heap_bytes: int
    created_at: datetime

class DeviceSummary(BaseModel):
    total_devices: int
    online_count: int
    lan_failure_count: int
    wan_timeout_count: int
    devices: List[DeviceResponse]
