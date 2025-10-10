"""Core data models for :mod:`yt_streams`.

Purpose:
    This module defines the **pure data layer** used throughout the package. All
    classes are **typed**, **serializable**, and documented with Google‑style
    docstrings. These models do **not** perform I/O; they are safe to import in
    any context (CLI, TUI, Streamlit, workers, tests).

Design:
    * Built on :class:`pydantic.BaseModel` (v2) for validation and convenient
      (de-)serialization to JSON/CSV/Parquet via intermediate dicts.
    * Small, composable types with explicit responsibilities:
        - :class:`VideoInfo` — normalized YouTube metadata (id/title/duration/url).
        - :class:`WorkerPhase` — lifecycle phases for a worker.
        - :class:`WorkerState` — live telemetry suitable for UIs and logging.
        - :class:`Command` — controller → worker messages (e.g., ``play_cycle``).
        - :class:`IntervalSpec` / :class:`CronSpec` — scheduling specs.
        - :class:`RunRecord` — append‑only ledger row for durable history.

Attributes:
    DEFAULT_PLAY_SECONDS (int): Default play window used by commands.

Examples:
    Basic construction and validation::

        >>> VideoInfo(id="abc123", title="Demo", duration=42, url="https://youtu.be/abc123").id
        'abc123'
        >>> WorkerState(wid=0).phase.value
        'idle'
        >>> Command().model_dump()
        {'name': 'play_cycle', 'play_seconds': 60}

    Interval parsing helper::

        >>> IntervalSpec.from_text("0:02:00").model_dump()
        {'hours': 0, 'minutes': 2, 'seconds': 0}

    Cron usage with APScheduler trigger (illustrative)::

        >>> CronSpec(expr='*/5 * * * *').expr
        '*/5 * * * *'
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator

DEFAULT_PLAY_SECONDS: int = 60


class VideoInfo(BaseModel):
    """Normalized subset of YouTube metadata.

    Args:
        id: Canonical YouTube video id.
        title: Human‑readable title.
        duration: Total duration in seconds (``None`` for live/unknown).
        url: Canonical watch URL for the video.

    Examples:
        ::
            >>> VideoInfo(id="x", title="t", duration=None, url="https://x").title
            't'
    """

    id: str
    title: str
    duration: int | None = None
    url: str


class WorkerPhase(str, Enum):
    """Lifecycle phases for a worker.

    Values:
        idle: Thread created but not yet initialized.
        initialized: Browser/page ready; waiting for commands.
        working: Actively executing a command (e.g., play window).
        error: Encountered a non‑fatal error; still reporting state.
        stopped: Cleaned up and terminated.
    """

    idle = "idle"
    initialized = "initialized"
    working = "working"
    error = "error"
    stopped = "stopped"


class WorkerState(BaseModel):
    """Live telemetry snapshot for a worker.

    Args:
        wid: Worker id (0..N‑1).
        phase: Current lifecycle phase.
        play_seconds: Seconds progressed in the current play cycle.
        refreshes: Number of completed refresh cycles in this session.
        last_error: Last error string (if any) for quick diagnosis.
        heartbeat_ts: Monotonic timestamp (float) of the last update.

    Returns:
        A validated :class:`WorkerState` suitable for UI tables and logging.

    Examples:
        ::
            >>> s = WorkerState(wid=2, phase=WorkerPhase.working, play_seconds=7)
            >>> s.refreshes
            0
    """

    wid: int
    phase: WorkerPhase = WorkerPhase.idle
    play_seconds: int = 0
    refreshes: int = 0
    last_error: str | None = None
    heartbeat_ts: float = 0.0


class Command(BaseModel):
    """Controller → worker message.

    Currently a single operation is supported: ``play_cycle``.

    Args:
        name: Literal command name (``"play_cycle"``).
        play_seconds: Desired play window (seconds) for the cycle.

    Examples:
        ::
            >>> Command().play_seconds
            60
    """

    name: Literal["play_cycle"] = "play_cycle"
    play_seconds: int = Field(DEFAULT_PLAY_SECONDS, ge=1)


class IntervalSpec(BaseModel):
    """Interval schedule specification.

    Args:
        hours: Hours component (>= 0).
        minutes: Minutes component (>= 0).
        seconds: Seconds component (>= 0).

    Raises:
        ValueError: If any component is negative.

    Examples:
        ::
            >>> IntervalSpec(hours=0, minutes=1, seconds=30).seconds
            30
            >>> IntervalSpec.from_text("45").seconds
            45
    """

    hours: int = 0
    minutes: int = 0
    seconds: int = 0

    @field_validator("hours", "minutes", "seconds")
    @classmethod
    def _non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Interval fields must be non‑negative")
        return v

    @classmethod
    def from_text(cls, text: str) -> "IntervalSpec":
        """Parse ``HH:MM:SS``/``MM:SS``/``SS`` text into an :class:`IntervalSpec`.

        Args:
            text: A colon‑separated time like ``"0:02:00"``, ``"15:30"``, or
                just seconds ``"45"``.

        Returns:
            Parsed :class:`IntervalSpec`.

        Examples:
            ::
                >>> IntervalSpec.from_text("0:01:05").model_dump()
                {'hours': 0, 'minutes': 1, 'seconds': 5}
        """
        parts = [p for p in text.strip().split(":") if p]
        nums = [int(p) for p in parts]
        if len(nums) == 1:
            h, m, s = 0, 0, nums[0]
        elif len(nums) == 2:
            h, (m, s) = 0, (nums[0], nums[1])
        elif len(nums) == 3:
            h, m, s = nums
        else:
            raise ValueError("Expect 'SS', 'MM:SS', or 'HH:MM:SS'")
        return cls(hours=h, minutes=m, seconds=s)

    # Optional convenience for APScheduler users (import lazily to avoid hard dep).
    def to_trigger(self):  # -> apscheduler.triggers.interval.IntervalTrigger
        """Create an APScheduler ``IntervalTrigger``.

        Returns:
            An ``IntervalTrigger`` instance if APScheduler is installed; otherwise
            raises ``ImportError``.

        Examples:
            ::
                >>> trig = IntervalSpec.from_text('5').to_trigger()  # doctest: +SKIP
        """
        from apscheduler.triggers.interval import IntervalTrigger  # type: ignore

        return IntervalTrigger(hours=self.hours, minutes=self.minutes, seconds=self.seconds)


class CronSpec(BaseModel):
    """Cron schedule specification (standard 5‑field expression).

    Args:
        expr: A crontab expression like ``"*/5 * * * *"``.

    Examples:
        ::
            >>> CronSpec(expr="0,30 * * * *").expr
            '0,30 * * * *'
    """

    expr: str

    def to_trigger(self):  # -> apscheduler.triggers.cron.CronTrigger
        """Create an APScheduler ``CronTrigger`` from ``expr``.

        Returns:
            A ``CronTrigger`` instance if APScheduler is installed; otherwise
            raises ``ImportError``.
        """
        from apscheduler.triggers.cron import CronTrigger  # type: ignore

        return CronTrigger.from_crontab(self.expr)


class RunRecord(BaseModel):
    """Append‑only ledger row representing a worker heartbeat or event.

    Args:
        ts: POSIX timestamp when the event was recorded.
        wid: Worker id.
        phase: Worker phase string (use :class:`WorkerPhase`).
        play_seconds: Seconds progressed in the current play cycle.
        refreshes: Total refreshes completed so far.
        error: Optional error string for diagnostics.

    Examples:
        ::
            >>> RunRecord(ts=0.0, wid=1, phase='working', play_seconds=10, refreshes=2).wid
            1
    """

    ts: float
    wid: int
    phase: str
    play_seconds: int
    refreshes: int
    error: str | None = None
