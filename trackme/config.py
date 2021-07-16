""" configuration preparation """
from pydantic import BaseSettings
from typing import Optional


class Configuration(BaseSettings):
    DB_URI: str
    HASH_ALGO: Optional[str] = "argon2"
    CORS_ORIGIN: str = "*"  # per comma separated origins, default allows everything

    class Config:
        env_file = ".env"
