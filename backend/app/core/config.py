import os
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "CampusFlow"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./campusflow.db")
    
    # Authentication / JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-campusflow-agentic-jwt-key-2026")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock")  # "mock" or "openai"
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]
    
    # Optimization Scoring Weights (Configurable)
    WEIGHT_PRIORITY: float = 25.0
    WEIGHT_RESOURCE_MATCH: float = 20.0
    WEIGHT_TIME_MATCH: float = 15.0
    WEIGHT_EQUIPMENT_MATCH: float = 15.0
    WEIGHT_UTILIZATION: float = 15.0
    WEIGHT_FAIRNESS: float = 10.0
    PENALTY_CONFLICT: float = 100.0
    PENALTY_RESCHEDULING: float = 20.0

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
