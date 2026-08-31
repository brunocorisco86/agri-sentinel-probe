import datetime
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base

class Device(Base):
    __tablename__ = "devices"
    
    device_id = Column(String(64), primary_key=True, index=True)
    device_mac = Column(String(32), unique=True, index=True, nullable=False)
    location_name = Column(String(128), default="Ponto Nao Identificado", index=True)
    hardware_model = Column(String(64), default="ESP32 Generic")
    firmware_version = Column(String(32), default="1.0.0")
    
    # Status Operacional: "ONLINE", "LAN_FAILURE", "WAN_TIMEOUT", "OFFLINE"
    status = Column(String(32), default="ONLINE", index=True)
    last_seen_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    
    # Intervalo de Envio Configurado
    check_interval_seconds = Column(Integer, default=300)
    
    # Métricas de Conectividade
    wifi_ssid = Column(String(64), nullable=True)
    wifi_rssi_dbm = Column(Integer, nullable=True)
    
    # Alvo Local LAN (Gateway Dragino)
    local_target_enabled = Column(Boolean, default=False)
    local_target_ip = Column(String(32), nullable=True)
    local_target_online = Column(Boolean, default=True)
    local_target_rtt_ms = Column(Float, default=0.0)
    local_target_mac = Column(String(32), nullable=True)
    
    # Métricas do Sistema
    uptime_seconds = Column(Integer, default=0)
    free_heap_bytes = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    telemetries = relationship("Telemetry", back_populates="device", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="device", cascade="all, delete-orphan")
