"""
CloudRun IDE - Configuration
Application settings loaded from environment variables.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]
    
    # Google Gemini API
    GEMINI_API_KEY: str = ""
    
    # Docker Container Limits
    MAX_EXECUTION_TIME: int = 60  # seconds
    MAX_MEMORY: str = "1g"
    MAX_CPU_QUOTA: int = 100000
    MAX_CPU_PERIOD: int = 100000
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 10
    
    # Advanced Mode
    ALLOW_ADVANCED_MODE: bool = True
    
    # File Upload Limits
    MAX_FILE_SIZE_MB: int = 10
    MAX_FILES_PER_UPLOAD: int = 10
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()
