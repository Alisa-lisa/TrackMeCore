""" configuration preparation """
from pydantic import BaseSettings
from typing import Optional


class Configuration(BaseSettings):
    DB_URI: str
    DB_MIGRATION: str
    HASH_ALGO: Optional[str] = "argon2"

    class Config:
        env_file = ".env"
