"""Configuration for :mod:`yt_streams` using **Pydantic Settings** (v2).

Purpose:
    Provide a robust, environment-driven configuration layer built on
    :class:`pydantic_settings.BaseSettings`. This lets you control ``yt_streams``
    via a ``.env`` file, real environment variables, or explicit kwargs from
    the CLI—all with type-safe defaults and validation.

Design:
    - The root settings model is :class:`AppSettings` (:class:`BaseSettings`).
    - Sub-sections are composed as nested models:
        - :class:`BrowserSettings` — Chromium/headless, viewport, UA, proxy.
        - :class:`StorageSettings` — data directory & file names.
        - :class:`ScheduleSettings` — default play window and timezone.
    - A single **env prefix** ``YT_STREAMS_`` is used for all settings. Nested
      fields map with double underscores, e.g. ``YT_STREAMS_BROWSER__HEADLESS=true``.
    - Reads from ``.env`` by default; extra/unknown env vars are ignored.

Attributes:
    DEFAULT_DATA_DIR (Path): Default folder for local artifacts.

Examples:
    Minimal construction (kwargs)::

        >>> from yt_streams.config import AppSettings
        >>> s = AppSettings(url="https://www.youtube.com/watch?v=abc", workers=3)
        >>> s.workers
        3

    ``.env`` example (paste into project root)::

        YT_STREAMS_URL=https://www.youtube.com/watch?v=dQw4w9WgXcQ
        YT_STREAMS_WORKERS=6
        YT_STREAMS_SCHEDULE__PLAY_SECONDS=90
        YT_STREAMS_BROWSER__HEADLESS=false
        YT_STREAMS_STORAGE__DATA_DIR=./data/yt_streams

    Programmatic load that respects env + ``.env`` + kwargs::

        >>> AppSettings(workers=2).workers in (2, 6)
        True
"""
from __future__ import annotations

from pathlib import Path
from typing import Tuple

from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_DATA_DIR: Path = Path("data/yt_streams")


class BrowserSettings(BaseModel):
    """Browser/runtime options for Playwright.

    Args:
        headless: Launch Chromium in headless mode.
        viewport: (width, height) for the browser context.
        user_agent: Optional UA override per context (``None`` = Chromium default).
        proxy: Optional proxy URL (e.g., ``http://user:pass@host:port``).

    Examples:
        ::
            >>> BrowserSettings().headless
            False
    """

    headless: bool = Field(False, description="Launch Chromium headless")
    viewport: Tuple[int, int] = Field((1280, 720), description="Viewport size (w,h)")
    user_agent: str | None = Field(None, description="Override User-Agent string")
    proxy: str | None = Field(None, description="Proxy URL for Chromium")


class StorageSettings(BaseModel):
    """Local artifact storage settings.

    Args:
        data_dir: Root directory for artifacts.
        ledger_csv: File name for the run ledger CSV.
        meta_jsonl: File name for the metadata cache JSONL.

    Examples:
        ::
            >>> StorageSettings().data_dir == DEFAULT_DATA_DIR
            True
    """

    data_dir: Path = Field(DEFAULT_DATA_DIR, description="Local data directory root")
    ledger_csv: str = Field("runs.csv", description="Run ledger CSV filename")
    meta_jsonl: str = Field("meta.jsonl", description="Metadata cache JSONL filename")


class ScheduleSettings(BaseModel):
    """Defaults influencing playback and scheduling.

    Args:
        play_seconds: Default play window per cycle before refresh.
        timezone: IANA tz string used by the scheduler/UI.

    Raises:
        ValueError: If ``play_seconds`` < 5.

    Examples:
        ::
            >>> ScheduleSettings().play_seconds
            60
    """

    play_seconds: int = Field(60, ge=5, description="Play duration per cycle")
    timezone: str = Field("UTC", description="Scheduler timezone")


class AppSettings(BaseSettings):
    """Root settings model for :mod:`yt_streams` (env-driven).

    Args:
        url: Optional canonical YouTube watch URL. If ``None``, pulses must carry
            a URL (the Streamlit Controls and CLI both support per-pulse URLs).
        workers: Number of worker threads (>= 1).
        browser: Browser options (headless, viewport, UA, proxy).
        storage: Paths and file names for artifacts.
        schedule: Defaults for play window & timezone.

    Environment:
        - Prefix: ``YT_STREAMS_``
        - Nested mapping uses double underscores:
          ``YT_STREAMS_STORAGE__DATA_DIR=/tmp/yt``.
        - A ``.env`` file in the working directory is loaded automatically.

    Returns:
        AppSettings: A validated settings object. Env vars > .env > code defaults.

    Examples:
        ::
            >>> AppSettings(workers=2).workers
            2
    """

    model_config = SettingsConfigDict(
        env_prefix="YT_STREAMS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # NOTE: url is optional; empty strings are normalized to None
    url: str | None = Field(default=None, description="Default YouTube watch URL")
    workers: int = Field(4, ge=1, description="Number of worker threads")

    browser: BrowserSettings = Field(default_factory=BrowserSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    schedule: ScheduleSettings = Field(default_factory=ScheduleSettings)

    @field_validator("url", mode="before")
    @classmethod
    def _empty_to_none(cls, v: str | None) -> str | None:
        """Normalize empty values to ``None``.

        Args:
            v: Raw value from env/kwargs.

        Returns:
            str | None: ``None`` if empty/whitespace; otherwise the stripped string.

        Examples:
            ::
                >>> AppSettings(url=" ").url is None
                True
        """
        v = (v or "").strip()
        return v or None
