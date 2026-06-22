from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/darkatlas"

    # API Key Auth
    API_KEY: str = "changeme-secret-api-key"

    # App
    APP_NAME: str = "DarkAtlas Asset Management"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()