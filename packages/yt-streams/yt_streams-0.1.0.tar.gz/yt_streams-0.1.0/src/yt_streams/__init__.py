"""yt_streams — Multi-session YouTube runner with scheduling and UIs.

Purpose:
    Run N isolated Chromium sessions (Playwright) that perform play→wait→refresh
    cycles on demand or via schedules. Observe and steer the system through a
    Textual TUI or Streamlit dashboard. Persist a durable ledger (CSV/Parquet)
    and a small metadata cache. A lightweight file control channel enables
    external schedulers (e.g., Airflow) and UIs to enqueue actions safely.

Design:
    The package is split into small, composable modules:

    - :mod:`~yt_streams.models` —
      Data records (Pydantic v2): ``VideoInfo``, ``WorkerState``, ``RunRecord``,
      ``Command``, ``IntervalSpec``, ``CronSpec``.
    - :mod:`~yt_streams.config` —
      Env-driven :class:`~yt_streams.config.AppSettings` (Pydantic Settings).
    - :mod:`~yt_streams.meta` —
      Thin :mod:`yt_dlp` wrapper → :class:`~yt_streams.models.VideoInfo`.
    - :mod:`~yt_streams.worker` —
      Thread hosting an asyncio loop that drives Playwright Chromium.
    - :mod:`~yt_streams.controller` —
      Pool orchestration + APScheduler (interval/cron) + broadcast.
    - :mod:`~yt_streams.ratelimit` —
      :class:`~yt_streams.ratelimit.RateLimitMixin` (token-bucket) to guard bursts.
    - :mod:`~yt_streams.storage` —
      Append-only CSV/JSONL; optional Parquet export.
    - :mod:`~yt_streams.control` —
      File-based control channel (JSONL) for Streamlit/Airflow → controller.
    - :mod:`~yt_streams.streamui` —
      Streamlit UI (components + app wiring), purely file-driven.
    - :mod:`~yt_streams.tui` —
      Textual terminal UI (optional).
    - :mod:`~yt_streams.cli` —
      Typer CLI (service launchers, schedules, exports).
    - :mod:`~yt_streams.airflow` (optional) —
      Helpers DAGs can import to append commands and pick from a URL catalog.
    - :mod:`~yt_streams.stealth` —
      Advanced stealth utilities for anti-detection measures.
    - :mod:`~yt_streams.robots_config` —
      Robots.txt compliance and configuration management.
    - :mod:`~yt_streams.http_client` —
      Stealth HTTP client with anti-detection capabilities.
    - :mod:`~yt_streams.url_handler` —
      Universal URL handling and platform detection.
    - :mod:`~yt_streams.proxy_manager` —
      Advanced proxy management and health monitoring.

Attributes:
    __version__ (str): Installed package version (best effort via metadata).
    __all__ (list[str]): Stable public API (re-exports).

Examples:
    Minimal CLI run (Textual)::

        >>> # pdm run yt-streams run --url "https://www.youtube.com/watch?v=VIDEOID" --workers 3  # doctest: +SKIP

    Programmatic orchestration::

        >>> from yt_streams.controller import PoolController  # doctest: +SKIP
        >>> from yt_streams.models import Command  # doctest: +SKIP
        >>> ctl = PoolController(url="https://youtu.be/VIDEOID", workers=2)  # doctest: +SKIP
        >>> ctl.start(); ctl.broadcast(Command(play_seconds=15)); ctl.stop()  # doctest: +SKIP

Notes:
    *Compliance*: Use for testing your own content; automated viewing intended to
    manipulate counters may violate YouTube ToS.

    *Purity & side effects*: Models are pure. Browser/network I/O is isolated in
    ``worker`` and ``meta``. The control channel is append-only; ledger writes
    are append-only; schedulers operate in-process (APScheduler) or externally
    via Airflow writing to ``commands.jsonl``.
"""
from __future__ import annotations

from importlib import metadata as _metadata
from typing import Final

# Re-exports (public API)
from .config import AppSettings
from .control import ControlBroker, ControlCommand
from .controller import PoolController
from .meta import YtInfoService
from .models import Command, CronSpec, IntervalSpec, RunRecord, VideoInfo, WorkerState
from .storage import Storage
from .worker import BrowserOptions
from .ratelimit import RateLimitMixin

# Stealth and configuration modules
from .stealth import stealth_utils
from .robots_config import config_manager, can_fetch_url, get_crawl_delay, wait_for_crawl_delay
from .http_client import StealthHTTPClient, stealth_request
from .url_handler import URLHandler, URLType, ProxyConfig, ProxyChain, url_handler
from .proxy_manager import ProxyManager, proxy_manager


def _version() -> str:
    """Return the installed package version.

    Returns:
        str: Version string if available, else ``"0"`` (best effort).

    Examples:
        ::
            >>> isinstance(_version(), str)
            True
    """
    try:
        return _metadata.version("yt_streams")
    except Exception:
        return "0"


__version__: Final[str] = _version()

__all__: Final[list[str]] = [
    # meta/info
    "__version__",
    # settings & data models
    "AppSettings",
    "VideoInfo",
    "WorkerState",
    "RunRecord",
    "IntervalSpec",
    "CronSpec",
    "Command",
    # services & utilities
    "YtInfoService",
    "Storage",
    "BrowserOptions",
    "PoolController",
    "ControlCommand",
    "ControlBroker",
    "RateLimitMixin",
    # stealth & configuration
    "stealth_utils",
    "config_manager",
    "can_fetch_url",
    "get_crawl_delay",
    "wait_for_crawl_delay",
    "StealthHTTPClient",
    "stealth_request",
    # URL handling and proxy management
    "URLHandler",
    "URLType",
    "ProxyConfig",
    "ProxyChain",
    "url_handler",
    "ProxyManager",
    "proxy_manager",
]
