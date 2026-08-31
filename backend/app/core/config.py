import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Keepalive Foresight API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Banco de Dados (SQLite com suporte assíncrono aiosqlite por padrão)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./keepalive.db")
    
    # Autenticação da Sonda
    API_SECRET_TOKEN: str = os.getenv("API_SECRET_TOKEN", "keepalive-secret-token-123")
    
    # Configurações do Dead Man's Switch
    DEADMAN_INTERVAL_SECONDS: int = 10
    DEADMAN_TIMEOUT_SECONDS: int = 30  # 30 segundos sem heartbeat = incidente de timeout
    
    # Telegram Bot Alerter
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    
    # Google Gemini Flash API (Relatórios Executivos)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "blurbang")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
