from pydantic_settings import BaseSettings
from pathlib import Path

class Config(BaseSettings):
    PROJECT_ROOT: Path = Path(__file__).resolve().parents[3]
    DATA_RAW_DIR: Path = PROJECT_ROOT / "data" / "raw"
    DATA_PROCESSED_DIR: Path = PROJECT_ROOT / "data" / "processed"
    EMBEDDING_MODEL: str = "BAAI/bge-base-en-v1.5"
    DB_NAME: str = "chroma"
    TRESHOLD: float = 0.4
    N_RESULTS: int = 12
    MAX_TOKENS: int = 256
    LLM_TEMPERATURE: float = 0
    SYSTEM_STYLE: str = "You are a retail sales analyst for Superstore (2014-2017). You answer the question provided by the user. "
    SYSTEM_RULES: str = "If the context provided does not contain the requiered infomation, tell the user the data is insufficent."
    SYSTEM_PROMPT: str = SYSTEM_STYLE + SYSTEM_RULES

config = Config()