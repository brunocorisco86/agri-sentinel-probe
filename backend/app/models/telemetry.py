import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Telemetry(Base):
    __tablename__ = "telemetries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(64), ForeignKey("devices.device_id"), index=True, nullable=False)
    
    wifi_rssi_dbm = Column(Integer, nullable=True)
    local_target_online = Column(Boolean, default=True)
    local_target_rtt_ms = Column(Float, default=0.0)
    free_heap_bytes = Column(Integer, default=0)
    uptime_seconds = Column(Integer, default=0)
    received_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    
    device = relationship("Device", back_populates="telemetries")
