from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "NEXUS API"
    api_prefix: str = "/api"
    environment: str = "development"
    frontend_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://your-nexus-frontend.vercel.app",
    ]
    data_dir: Path = Path("app/data/raw")
    gemini_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("GEMINI_API_KEY", "GOOGLE_API_KEY"),
    )
    gemini_model: str = "gemini-2.5-flash"
    ai_log_path: Path = Path("app/data/ai_interactions.csv")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="NEXUS_",
        env_nested_delimiter="__",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
