from pydantic_settings import BaseSettings


class BaseServiceSettings(BaseSettings):
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str | None = None
    ENVIRONMENT: str = "development"
    CORS_ORIGIN: str | None = None  # comma-separated

    class Config:
        env_file = ".env"
        extra = "allow"

