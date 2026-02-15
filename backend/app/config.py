"""
CloudRun IDE - Configuration
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    CORS_ORIGINS: str = "*"
    MAX_EXECUTION_TIME: int = 30
    MAX_MEMORY: str = "256m"
    MAX_CPU_QUOTA: int = 50000
    MAX_CPU_PERIOD: int = 100000
    MAX_REQUESTS_PER_MINUTE: int = 30
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    PRE_PULL_IMAGES: bool = False
    MAX_UPLOAD_SIZE: int = 10485760
    MAX_FILES_PER_REQUEST: int = 5
    LOG_LEVEL: str = "INFO"
    JWT_SECRET: str = "cloudrun-ide-secret-change-me-in-production"
    DATABASE_URL: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
