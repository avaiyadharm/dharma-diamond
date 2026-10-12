import os
from typing import List
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="ignore",
    )

    PROJECT_NAME: str = "Dharma Diamond Inventory & Record Management"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY") or "change-this-dev-secret-key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Single-admin bootstrap configuration
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL") or "admin@dharmadiamond.local"
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD") or "change-me-please"
    ADMIN_FULL_NAME: str = os.getenv("ADMIN_FULL_NAME") or "Dharma Diamond Admin"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL") or "sqlite:///./dharma_diamond.db"

    # Business defaults
    CURRENCY_CODE: str = "INR"
    CURRENCY_SYMBOL: str = "₹"
    DEFAULT_GST_RATE: float = 3.0  # 3% for finished jewellery and cut diamonds

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]


settings = Settings()
