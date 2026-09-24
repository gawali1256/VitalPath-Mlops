from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        protected_namespaces=(),
    )

    app_name: str = "VitalPath API"
    model_path: Path = Path("/models/current/model.joblib")
    log_path: Path = Path("/logs/predictions.jsonl")
    allow_origins: str = "*"


settings = Settings()
