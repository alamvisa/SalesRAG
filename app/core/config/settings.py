from pydantic_settings import BaseSettings
from pathlib import Path

class Config(BaseSettings):
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[3]
    DATA_RAW_DIR: Path = PROJECT_ROOT / "data" / "raw"
    DATA_PROCESSED_DIR: Path = PROJECT_ROOT / "data" / "processed"
    EMBEDDING_MODEL: str = "BAAI/bge-base-en-v1.5"
    DB_NAME: str = "chroma"
    DB_INITIALIZED: bool = False

config = Config()