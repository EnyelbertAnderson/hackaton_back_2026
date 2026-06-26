# app/config.py
"""Carga de variables de entorno con Pydantic Settings."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    google_api_key: str = ""
    openai_api_key: str = ""
    chroma_data_dir: str = "./chroma_data"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
