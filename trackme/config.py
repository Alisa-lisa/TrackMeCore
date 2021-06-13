""" configuration preparation """
from pydantic import BaseSettings
from typing import Optional


class Configuration(BaseSettings):
    DB_URI: str
    HASH_ALGO: Optional[str] = "argon2"

    class Config:
        env_file = ".env"
