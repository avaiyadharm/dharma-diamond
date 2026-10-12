import os
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "Dharma Diamond Inventory & Record Management"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dharma-secret-key-change-in-production-2026-jewellery-vault")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./dharma_diamond.db")
    
    # Business Defaults
    CURRENCY_CODE: str = "INR"
    CURRENCY_SYMBOL: str = "₹"
    DEFAULT_GST_RATE: float = 3.0  # 3% for finished jewellery and cut diamonds
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
