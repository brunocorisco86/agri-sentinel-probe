from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, computed_field

def format_uptime(seconds: int) -> str:
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    mins, secs = divmod(rem, 60)
    if days > 0:
        return f"{days}d {hours:02d}h {mins:02d}m"
    elif hours > 0:
        return f"{hours}h {mins:02d}m {secs:02d}s"
    elif mins > 0:
        return f"{mins}m {secs:02d}s"
    return f"{secs}s"

class DeviceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    device_id: str
    device_mac: str
    location_name: str
    hardware_model: str
    firmware_version: str
    status: str
    last_seen_at: datetime
    check_interval_seconds: int = 300
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

    @computed_field
    @property
    def uptime_formatted(self) -> str:
        return format_uptime(self.uptime_seconds)

class DeviceSummary(BaseModel):
    total_devices: int
    online_count: int
    lan_failure_count: int
    wan_timeout_count: int
    devices: List[DeviceResponse]
