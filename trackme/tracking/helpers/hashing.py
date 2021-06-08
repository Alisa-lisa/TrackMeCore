from passlib.context import CryptContext
from trackme.config import Configuration
from trackme.tracking.types.user import UserInput


config = Configuration()

hash_manager = CryptContext(schemes=[config.HASH_ALGO], deprecated="auto")


def hasher(user: UserInput) -> str:
    return str(hash_manager.hash(f"{user.name}{user.password}"))


def verify(pwhash: str, origin: UserInput) -> bool:
    return hash_manager.verify(f"{origin.name}{origin.password}", pwhash)
