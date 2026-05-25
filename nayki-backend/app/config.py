from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "local"
    API_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # Database URLs
    DATABASE_URL: str = "postgresql+asyncpg://nayki_user:nayki_password@postgres:5432/nayki_db"
    # SYNC_DATABASE_URL is used for Alembic migrations, which require sync driver
    SYNC_DATABASE_URL: str = "postgresql+psycopg://nayki_user:nayki_password@postgres:5432/nayki_db"

    # Redis URL
    REDIS_URL: str = "redis://redis:6379/0"

    # Security Configuration
    DEV_AUTH_ENABLED: bool = False
    JWT_ISSUER: str = "https://securetoken.google.com/nayki-production"
    FIREBASE_PROJECT_ID: str = "nayki-production"
    FIREBASE_CREDENTIALS_JSON: str | None = None

    # H3 config
    H3_RESOLUTION: int = 9

    # Integration Configuration Keys
    GRAPHHOPPER_BASE_URL: str | None = None
    GOOGLE_PLACES_API_KEY: str | None = None
    GOOGLE_ROUTES_API_KEY: str | None = None
    FCM_SERVER_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Allow loading from environment variable configuration overrides
settings = Settings()
