import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Incident(Base):
    __tablename__ = "incidents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String(64), ForeignKey("devices.device_id"), index=True, nullable=False)
    
    # Tipos: "WAN_TIMEOUT", "GATEWAY_LAN_FAILURE", "BLACKOUT_GENERAL"
    incident_type = Column(String(64), index=True, nullable=False)
    
    # Status: "OPEN", "RESOLVED"
    status = Column(String(32), default="OPEN", index=True, nullable=False)
    
    description = Column(String(255), nullable=True)
    opened_at = Column(DateTime, default=datetime.datetime.utcnow, index=True, nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    
    device = relationship("Device", back_populates="incidents")
