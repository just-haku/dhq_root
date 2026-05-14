from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    AES_KEY: str
    DEV_KEY: str
    
    # Routes (Obfuscation)
    REAL_LOGIN_ROUTE: str
    REAL_REGISTER_ROUTE: str
    
    # Database
    MONGODB_URI: str
    
    # SMTP
    SMTP_USER: str
    SMTP_PASS: str
    
    # OP Credentials (Bootstrap)
    OP_INIT_USER: str
    OP_INIT_PASS: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Storage Drives
    NUMBER_OF_STORAGES: int = 1
    STORAGE1: Optional[str] = "/home/haku/storage"
    STORAGE2: Optional[str] = None
    STORAGE3: Optional[str] = None
    STORAGE4: Optional[str] = None
    
    # Vault
    vault_master_key: str

    # Creator Intelligence
    CI_WORKER_REGISTRATION_TOKEN: Optional[str] = None
    CI_MODEL_SCAN_ROOTS: str = "/home/haku/models,/home/haku/Models,/models"
    CI_QDRANT_URL: str = "http://localhost:6333"
    CI_QDRANT_COLLECTION: str = "dhq_creator_intelligence"
    CI_WORKER_HEARTBEAT_STALE_SECONDS: int = 45
    CI_WORKER_HEARTBEAT_OFFLINE_SECONDS: int = 90
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
