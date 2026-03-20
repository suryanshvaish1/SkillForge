from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    app_name: str = "AdaptiveLearnEngine"
    app_env: str = "development"
    app_debug: bool = True
    log_level: str = "DEBUG"
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    host: str = "0.0.0.0"
    port: int = 8000
    spacy_model: str = "en_core_web_sm"
    course_catalog_path: str = "data/course_catalog.json"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def catalog_abs_path(self) -> Path:
        base = Path(__file__).resolve().parent.parent
        return base / self.course_catalog_path

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
