from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """تنظیمات امن برنامه که از متغیرهای محیطی خوانده می‌شوند."""

    bot_token: str = Field(min_length=20)
    api_id: int = Field(gt=0)
    api_hash: str = Field(min_length=20)
    session_string: str = Field(min_length=20)
    owner_id: int = Field(gt=0)
    log_level: str = "INFO"
    max_queue_size: int = Field(default=50, ge=1, le=500)
    max_track_minutes: int = Field(default=180, ge=1, le=1440)
    cookies_file: Path | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("bot_token")
    @classmethod
    def reject_placeholder(cls, value: str) -> str:
        if value.strip().lower() in {"token", "your_token", "changeme"}:
            raise ValueError("BOT_TOKEN معتبر وارد کنید")
        return value.strip()

    @field_validator("cookies_file")
    @classmethod
    def validate_cookie_path(cls, value: Path | None) -> Path | None:
        if value is not None and not value.exists():
            raise ValueError(f"فایل کوکی پیدا نشد: {value}")
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
