"""Configuration management for the dashboard."""
import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # API Configuration
    api_title: str = "Kaggler Dashboard API"
    api_version: str = "1.0.0"
    api_description: str = "Real-time monitoring dashboard for GEPA evolution"

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False
    log_level: str = "info"

    # CORS Configuration
    cors_origins: List[str] = ["*"]
    cors_credentials: bool = True
    cors_methods: List[str] = ["*"]
    cors_headers: List[str] = ["*"]

    # WebSocket Configuration
    ws_heartbeat_interval: int = 30
    ws_max_message_size: int = 10 * 1024 * 1024  # 10MB

    # Database Configuration (optional)
    database_url: str | None = None
    db_pool_size: int = 10
    db_max_overflow: int = 20

    # Redis Configuration (optional)
    redis_url: str | None = None
    redis_cache_ttl: int = 300  # 5 minutes

    # Competition Configuration
    max_concurrent_competitions: int = 10
    max_competition_duration: int = 86400  # 24 hours
    default_population_size: int = 50
    default_generations: int = 100

    # Performance Configuration
    metrics_update_interval: int = 5  # seconds
    history_retention_days: int = 30

    # Security Configuration
    api_key_header: str = "X-API-Key"
    api_key: str | None = None
    enable_authentication: bool = False

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
