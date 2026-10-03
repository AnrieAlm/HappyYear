"""Application settings, read from environment / .env."""
from __future__ import annotations

import json
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "study_duel"

    jwt_secret: str = "dev-only-secret-change-me-this-is-32-bytes-plus"
    jwt_ttl_days: int = 60

    users: str = '{"farmerB":"changeme","maya":"changeme"}'
    allowed_origins: str = "*"

    day_tz: str = "UTC"
    daily_size: int = 20
    review_size: int = 10

    @property
    def users_map(self) -> dict[str, str]:
        try:
            data = json.loads(self.users)
        except json.JSONDecodeError as exc:  # pragma: no cover
            raise RuntimeError("USERS must be a JSON object of name -> passcode") from exc
        if not isinstance(data, dict) or not data:
            raise RuntimeError("USERS must be a non-empty JSON object of name -> passcode")
        return {str(k): str(v) for k, v in data.items()}

    @property
    def origins(self) -> list[str]:
        raw = self.allowed_origins.strip()
        if raw == "*":
            return ["*"]
        return [o.strip() for o in raw.split(",") if o.strip()]


@lru_cache
def settings() -> Settings:
    return Settings()
