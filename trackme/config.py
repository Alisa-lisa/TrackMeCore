""" configuration preparation """
from pydantic import BaseSettings
from typing import Optional
import os


class Configuration(BaseSettings):
    DB_URI: str
    HASH_ALGO: Optional[str] = "argon2"
    CORS_ORIGIN: str = "*"  # per comma separated origins, default allows everything
    ACCESS_TOKEN: str = "test"

    class Config:
        environment = os.environ.get("ENV", "example")
        env_file = f".env.{environment}"
