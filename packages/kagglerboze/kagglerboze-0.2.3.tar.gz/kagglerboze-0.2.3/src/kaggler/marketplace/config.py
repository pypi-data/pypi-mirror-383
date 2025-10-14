"""Configuration management for the Prompt Marketplace."""

import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application Settings
    APP_NAME: str = "Kaggler Prompt Marketplace"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False)
    ENVIRONMENT: str = Field(default="development")

    # Database Settings
    DATABASE_URL: str = Field(
        default="sqlite:///./marketplace.db",
        description="Database connection URL",
    )
    DATABASE_ECHO: bool = Field(default=False, description="Echo SQL queries")
    DATABASE_POOL_SIZE: int = Field(default=5, description="Connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, description="Max overflow connections")

    # JWT Settings
    JWT_SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT token signing",
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    JWT_EXPIRATION_MINUTES: int = Field(
        default=60 * 24 * 7,  # 7 days
        description="JWT token expiration time in minutes",
    )

    # OAuth Settings - GitHub
    GITHUB_CLIENT_ID: Optional[str] = Field(default=None, description="GitHub OAuth client ID")
    GITHUB_CLIENT_SECRET: Optional[str] = Field(
        default=None, description="GitHub OAuth client secret"
    )
    GITHUB_REDIRECT_URI: str = Field(
        default="http://localhost:8000/auth/github/callback",
        description="GitHub OAuth redirect URI",
    )

    # OAuth Settings - Google
    GOOGLE_CLIENT_ID: Optional[str] = Field(default=None, description="Google OAuth client ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = Field(
        default=None, description="Google OAuth client secret"
    )
    GOOGLE_REDIRECT_URI: str = Field(
        default="http://localhost:8000/auth/google/callback",
        description="Google OAuth redirect URI",
    )

    # API Settings
    API_V1_PREFIX: str = Field(default="/api/v1", description="API version 1 prefix")
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="CORS allowed origins",
    )
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True)
    CORS_ALLOW_METHODS: list[str] = Field(default=["*"])
    CORS_ALLOW_HEADERS: list[str] = Field(default=["*"])

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_REQUESTS: int = Field(default=100, description="Max requests per window")
    RATE_LIMIT_WINDOW: int = Field(default=60, description="Rate limit window in seconds")

    # Pagination
    DEFAULT_PAGE_SIZE: int = Field(default=20, description="Default page size")
    MAX_PAGE_SIZE: int = Field(default=100, description="Maximum page size")

    # Search Settings
    SEARCH_MIN_QUERY_LENGTH: int = Field(default=3, description="Minimum search query length")
    SEARCH_MAX_RESULTS: int = Field(default=1000, description="Maximum search results")

    # File Upload Settings
    MAX_PROMPT_LENGTH: int = Field(default=50000, description="Maximum prompt content length")
    MAX_DESCRIPTION_LENGTH: int = Field(
        default=2000, description="Maximum description length"
    )
    MAX_REVIEW_LENGTH: int = Field(default=5000, description="Maximum review length")

    # Cache Settings
    CACHE_ENABLED: bool = Field(default=True, description="Enable caching")
    CACHE_TTL: int = Field(default=300, description="Cache TTL in seconds")

    # Logging Settings
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string",
    )

    @validator("DATABASE_URL")
    def validate_database_url(cls, v: str) -> str:
        """Validate database URL format."""
        if not v:
            raise ValueError("DATABASE_URL cannot be empty")
        valid_prefixes = ["sqlite://", "postgresql://", "mysql://"]
        if not any(v.startswith(prefix) for prefix in valid_prefixes):
            raise ValueError(
                f"DATABASE_URL must start with one of: {', '.join(valid_prefixes)}"
            )
        return v

    @validator("JWT_SECRET_KEY")
    def validate_jwt_secret(cls, v: str, values: dict) -> str:
        """Validate JWT secret key in production."""
        if values.get("ENVIRONMENT") == "production" and v == "your-secret-key-change-in-production":
            raise ValueError("JWT_SECRET_KEY must be changed in production")
        return v

    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v) -> list[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"

    def is_testing(self) -> bool:
        """Check if running in test environment."""
        return self.ENVIRONMENT == "testing"

    def get_github_oauth_url(self, state: str) -> str:
        """Get GitHub OAuth authorization URL.

        Args:
            state: CSRF protection state parameter

        Returns:
            GitHub OAuth authorization URL
        """
        if not self.GITHUB_CLIENT_ID:
            raise ValueError("GITHUB_CLIENT_ID not configured")

        base_url = "https://github.com/login/oauth/authorize"
        params = f"client_id={self.GITHUB_CLIENT_ID}&redirect_uri={self.GITHUB_REDIRECT_URI}&state={state}"
        return f"{base_url}?{params}"

    def get_google_oauth_url(self, state: str) -> str:
        """Get Google OAuth authorization URL.

        Args:
            state: CSRF protection state parameter

        Returns:
            Google OAuth authorization URL
        """
        if not self.GOOGLE_CLIENT_ID:
            raise ValueError("GOOGLE_CLIENT_ID not configured")

        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = (
            f"client_id={self.GOOGLE_CLIENT_ID}"
            f"&redirect_uri={self.GOOGLE_REDIRECT_URI}"
            f"&response_type=code"
            f"&scope=openid%20email%20profile"
            f"&state={state}"
        )
        return f"{base_url}?{params}"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get settings instance for dependency injection.

    Returns:
        Settings instance
    """
    return settings
