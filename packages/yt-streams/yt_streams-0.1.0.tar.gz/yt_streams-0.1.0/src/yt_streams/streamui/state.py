"""Shared UI state & cached data accessors for :mod:`yt_streams` Streamlit app.

Purpose:
    Provide a small, typed “state layer” the Streamlit UI can rely on:
    - Resolve the **data directory**, default URL, and user preferences
      from env → on-disk prefs → sensible defaults.
    - Expose **cached readers** for ledger, schedules, and catalog files.
    - Offer small **action helpers** (append pulse) that write to the
      file-based control channel.

Design:
    - :class:`UiState` is a light, general-purpose container (Pydantic v2).
      It is independent from Streamlit and safe to import anywhere.
    - Persistence:
        * UI preferences (like default URL) are stored at
          ``<data_dir>/ui_prefs.json``.
        * The *data_dir* itself is discovered via env var
          ``YT_STREAMS_DATA_DIR`` or defaults to ``data/yt_streams``.
    - Caching:
        * If Streamlit is present, readers are wrapped with
          :func:`streamlit.cache_data` (TTL-based).
        * Otherwise, readers fall back to an LRU cache for the process.
    - Catalog resolution:
        * Preferred file: ``$YT_STREAMS_CATALOG`` (CSV/JSONL),
          else ``<data_dir>/catalog.csv`` or ``catalog.jsonl`` (first active
          entry with highest weight).

Attributes:
    DEFAULT_DATA_DIR (Path): ``data/yt_streams``.
    UI_PREFS_NAME (str): ``ui_prefs.json``.

Examples:
    Minimal usage inside Streamlit::

        >>> # doctest: +SKIP
        >>> from yt_streams.streamui.state import get_state, tail_ledger_df
        >>> ui = get_state()  # resolves data_dir, default_url
        >>> df = tail_ledger_df(ui.data_dir, n=2000)

    Programmatic pulse append (no Streamlit required)::

        >>> # doctest: +SKIP
        >>> from yt_streams.streamui.state import get_state, append_pulse
        >>> ui = get_state()
        >>> append_pulse(ui, play_seconds=30, url=ui.default_url)

Notes:
    *Purity*: This module creates directories lazily, reads/writes small JSON
    and CSV/JSONL files, and never opens long-lived file handles.
"""
from __future__ import annotations

from dataclasses import dataclass  # noqa: F401  (kept for future extensions)
from functools import lru_cache
from pathlib import Path
from typing import Final

import json
import os
import time

from pydantic import BaseModel, Field

try:  # optional for UI-only conveniences; imported lazily inside functions too
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover
    pd = None  # type: ignore

# Local package imports (no Streamlit dependency here)
from yt_streams.control import ControlCommand, append_command

# ----------------------------- constants & paths ------------------------------

DEFAULT_DATA_DIR: Final[Path] = Path("data/yt_streams")
UI_PREFS_NAME: Final[str] = "ui_prefs.json"
LEDGER_FILE: Final[str] = "runs.csv"
SCHEDULES_FILE: Final[str] = "schedules.jsonl"

__all__ = [
    # ui helpers
    "section", "hr", "badge", "pill", "json_expander",
    # formatting
    "fmt_ts", "time_ago", "fmt_bytes",
    # toasts
    "toast_success", "toast_info", "toast_warn", "toast_error",
]

# ------------------------------- data models ----------------------------------

class UiPrefs(BaseModel):
    """Persisted preferences for the UI (per data_dir).

    Args:
        default_url: Preferred default URL for pulses (overrides catalog).
        lookback_minutes: Default lookback window for views.
        auto_refresh: Whether to auto-refresh dashboards by default.

    Returns:
        A validated preference object.

    Examples:
        ::
            >>> UiPrefs(default_url=None).model_dump()["auto_refresh"]
            True
    """
    default_url: str | None = Field(default=None)
    lookback_minutes: int = Field(default=120, ge=1)
    auto_refresh: bool = Field(default=True)


class UiState(BaseModel):
    """In-memory state used by Streamlit components.

    Args:
        data_dir: Root folder for artifacts (ledger, schedules, commands).
        default_url: Resolved “best” URL for pulses (env/prefs/catalog).
        prefs: Persisted UI preferences loaded from disk (mutable via helpers).

    Returns:
        A state object that is import-safe outside Streamlit.

    Examples:
        ::
            >>> UiState(data_dir=DEFAULT_DATA_DIR).data_dir.name
            'yt_streams'
    """
    data_dir: Path = Field(default=DEFAULT_DATA_DIR)
    default_url: str | None = Field(default=None)
    prefs: UiPrefs = Field(default_factory=UiPrefs)


# ------------------------------- small utilities ------------------------------

def _try_import_streamlit():
    """Return streamlit module if available, else None.

    Returns:
        The imported Streamlit module or ``None`` if unavailable.

    Examples:
        ::
            >>> _try_import_streamlit() is None in (True, False)
            True
    """
    try:  # pragma: no cover
        import streamlit as st  # type: ignore
        return st
    except Exception:  # pragma: no cover
        return None


def _ensure_dir(p: Path) -> None:
    """Ensure directory exists.

    Args:
        p: Directory path to create.

    Returns:
        None.
    """
    p.mkdir(parents=True, exist_ok=True)


def _prefs_path(root: Path) -> Path:
    """Compute UI prefs path.

    Args:
        root: Data directory.

    Returns:
        Path to ``ui_prefs.json``.
    """
    return root / UI_PREFS_NAME


def _load_prefs(root: Path) -> UiPrefs:
    """Load UI preferences from disk.

    Args:
        root: Data directory.

    Returns:
        Parsed :class:`UiPrefs`. Falls back to defaults on errors.
    """
    p = _prefs_path(root)
    if not p.exists():
        return UiPrefs()
    try:
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return UiPrefs.model_validate(data)
    except Exception:
        return UiPrefs()  # tolerant


def _save_prefs(root: Path, prefs: UiPrefs) -> None:
    """Persist UI preferences to disk.

    Args:
        root: Data directory.
        prefs: Preferences to serialize.

    Returns:
        None.
    """
    _ensure_dir(root)
    with (root / UI_PREFS_NAME).open("w", encoding="utf-8") as f:
        json.dump(prefs.model_dump(), f, ensure_ascii=False, indent=2)


def _resolve_data_dir(env_var: str = "YT_STREAMS_DATA_DIR") -> Path:
    """Resolve data directory from env or fallback.

    Args:
        env_var: Environment variable name to consult.

    Returns:
        Resolved :class:`Path`.
    """
    raw = os.environ.get(env_var, "").strip()
    return Path(raw) if raw else DEFAULT_DATA_DIR


def _load_catalog_items(path: Path) -> list[dict]:
    """Read a CSV or JSONL catalog with columns: url, weight, active, note.

    Args:
        path: File path. Must exist.

    Returns:
        List of plain dict items.
    """
    if not path.exists():
        return []
    try:
        if path.suffix.lower() == ".csv":
            import csv
            out: list[dict] = []
            with path.open("r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    out.append(
                        {
                            "url": (row.get("url") or "").strip(),
                            "weight": float(row.get("weight") or 1.0),
                            "active": str(row.get("active") or "1").strip() not in {"0", "false", "False"},
                            "note": row.get("note") or None,
                        }
                    )
            return out
        # JSONL
        out = []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s:
                    continue
                try:
                    obj = json.loads(s)
                    out.append(
                        {
                            "url": (obj.get("url") or "").strip(),
                            "weight": float(obj.get("weight") or 1.0),
                            "active": bool(obj.get("active", True)),
                            "note": obj.get("note"),
                        }
                    )
                except Exception:
                    continue
        return out
    except Exception:
        return []


def _resolve_default_url_from_catalog(root: Path) -> str | None:
    """Choose a default URL from a catalog file.

    Args:
        root: Data directory for default catalog locations.

    Returns:
        Chosen URL or ``None`` if none available.
    """
    pref = os.environ.get("YT_STREAMS_CATALOG", "").strip()
    candidates = [Path(pref)] if pref else []
    for name in ("catalog.csv", "catalog.jsonl"):
        candidates.append(root / name)

    items: list[dict] = []
    for c in candidates:
        if c and c.exists():
            items = _load_catalog_items(c)
            if items:
                break

    active = [i for i in items if i.get("active", True) and (i.get("url") or "").strip()]
    if not active:
        return None
    try:
        return max(active, key=lambda i: float(i.get("weight", 1.0))).get("url")
    except Exception:
        return active[0].get("url")


def _resolve_default_url(data_dir: Path, prefs: UiPrefs) -> str | None:
    """Flag → env → prefs → catalog. Return None if nothing found.

    Args:
        data_dir: Data directory.
        prefs: Loaded UI preferences.

    Returns:
        URL string or ``None``.
    """
    env = os.environ.get("YT_STREAMS_DEFAULT_URL", "").strip()
    if env:
        return env
    if prefs.default_url:
        return prefs.default_url
    return _resolve_default_url_from_catalog(data_dir)


# --------------------------------- public API ---------------------------------

def get_state(*, data_dir: Path | None = None, persist_defaults: bool = True) -> UiState:
    """Construct a :class:`UiState` using env/prefs/catalog resolution.

    Args:
        data_dir: Explicit data dir. If ``None``, env var
            ``YT_STREAMS_DATA_DIR`` or :data:`DEFAULT_DATA_DIR` is used.
        persist_defaults: If True, write back resolved default URL to prefs
            when none existed yet (makes the UI sticky across restarts).

    Returns:
        UiState with ``data_dir``, ``default_url``, and loaded ``prefs``.

    Examples:
        ::
            >>> # ui = get_state()  # doctest: +SKIP
            >>> # isinstance(ui.data_dir, Path)  # doctest: +SKIP
            True
    """
    root = data_dir or _resolve_data_dir()
    _ensure_dir(root)
    prefs = _load_prefs(root)
    resolved = _resolve_default_url(root, prefs)
    ui = UiState(data_dir=root, default_url=resolved, prefs=prefs)
    if persist_defaults and prefs.default_url is None and resolved:
        prefs.default_url = resolved
        _save_prefs(root, prefs)
    return ui


def set_default_url(ui: UiState, url: str | None) -> None:
    """Update the default URL in memory and persist to disk.

    Args:
        ui: The current UI state.
        url: The new default URL (or ``None`` to clear).

    Returns:
        None.
    """
    ui.default_url = (url or None)
    prefs = _load_prefs(ui.data_dir)
    prefs.default_url = ui.default_url
    _save_prefs(ui.data_dir, prefs)


# --------------------------- cached file readers ------------------------------

def _cache_data(func):
    """Decorate function with streamlit.cache_data if available, else LRU.

    Args:
        func: Callable to wrap.

    Returns:
        Wrapped callable using Streamlit cache or process-local LRU.
    """
    st = _try_import_streamlit()
    if st and hasattr(st, "cache_data"):  # pragma: no cover
        return st.cache_data(show_spinner=False, ttl=10.0)(func)
    return lru_cache(maxsize=16)(func)


@_cache_data
def tail_ledger_df(root: Path, n: int = 20_000) -> "pd.DataFrame | None":
    """Return a pandas DataFrame with up to the last *n* rows of the ledger.

    Args:
        root: Data directory.
        n: Maximum number of rows (tail).

    Returns:
        DataFrame or ``None`` if pandas missing or file absent.

    Examples:
        ::
            >>> # tail_ledger_df(Path('data/yt_streams'), n=1000)  # doctest: +SKIP
    """
    if pd is None:
        return None
    p = root / LEDGER_FILE
    if not p.exists():
        return None
    try:
        size = p.stat().st_size
        with p.open("rb") as f:
            if size > 2_000_000:  # ~2MB window
                f.seek(size - 2_000_000)
            buf = f.read().decode("utf-8", errors="ignore")
        lines = buf.splitlines()
        # keep only the last header onward
        header_idx = 0
        for i, ln in enumerate(lines):
            if ln.startswith("ts,wid,phase,play_seconds,refreshes,error"):
                header_idx = i
        tail = lines[header_idx:]
        if len(tail) > n + 1:
            tail = [tail[0]] + tail[-n:]
        import io as _io
        df = pd.read_csv(_io.StringIO("\n".join(tail)))
        # Normalize
        if "ts" in df:
            df["ts"] = pd.to_numeric(df["ts"], errors="coerce")
            df["when"] = pd.to_datetime(df["ts"], unit="s", errors="coerce")
        if "wid" in df:
            with pd.option_context("future.no_silent_downcasting", True):
                df["wid"] = pd.to_numeric(df["wid"], errors="coerce").astype("Int64")
        if "refreshes" in df:
            with pd.option_context("future.no_silent_downcasting", True):
                df["refreshes"] = pd.to_numeric(df["refreshes"], errors="coerce").fillna(0).astype("Int64")
        if "error" in df:
            df["error"] = df["error"].astype(str).replace({"": None, "nan": None})
        return df
    except Exception:
        return None


@_cache_data
def read_schedules_jsonl(root: Path) -> list[dict]:
    """Load the schedules mirror JSONL (append-only) into a list of dicts.

    Args:
        root: Data directory.

    Returns:
        List of schedule dicts (possibly empty).
    """
    p = root / SCHEDULES_FILE
    if not p.exists():
        return []
    out: list[dict] = []
    try:
        with p.open("r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s:
                    continue
                try:
                    out.append(json.loads(s))
                except Exception:
                    continue
        return out
    except Exception:
        return []


@_cache_data
def read_catalog(root: Path) -> list[dict]:
    """Resolve and load a catalog from env or default paths as item dicts.

    Args:
        root: Data directory used to look for catalog files.

    Returns:
        List of catalog items (possibly empty).
    """
    pref = os.environ.get("YT_STREAMS_CATALOG", "").strip()
    candidates = ([Path(pref)] if pref else []) + [root / "catalog.csv", root / "catalog.jsonl"]
    for c in candidates:
        if c.exists():
            return _load_catalog_items(c)
    return []


# ----------------------------- action conveniences ----------------------------

def append_pulse(
    ui: UiState,
    *,
    play_seconds: int | None = None,
    play_min: int | None = None,
    play_max: int | None = None,
    url: str | None = None,
    note: str | None = "ui:pulse",
) -> None:
    """Append a one-off pulse to the control channel.

    Precedence:
        1) ``url`` argument
        2) ``ui.default_url``
        3) no URL (allowed if controller started without one and workers handle defaults)

    If a fixed ``play_seconds`` is omitted, but a range is provided, a random
    value within [min,max] is chosen *at broker time*. Providing a fixed value
    here makes the choice explicit in the command itself.

    Args:
        ui: UI state providing the data directory and default URL.
        play_seconds: Fixed play window.
        play_min: Lower bound for random play window (inclusive).
        play_max: Upper bound for random play window (inclusive).
        url: URL override.
        note: Annotation for audit/debug.

    Returns:
        None.

    Examples:
        ::
            >>> # append_pulse(get_state(), play_min=45, play_max=90)  # doctest: +SKIP
    """
    args: dict[str, int | str] = {}
    if play_seconds is not None:
        args["play_seconds"] = int(play_seconds)
    else:
        if play_min is not None:
            args["play_min"] = int(play_min)
        if play_max is not None:
            args["play_max"] = int(play_max)

    chosen_url = (url or ui.default_url or "").strip()
    if chosen_url:
        args["url"] = chosen_url  # broker can choose to honor/override

    append_command(ui.data_dir, ControlCommand(verb="pulse", args=args, note=note))


# ----------------------------------- misc -------------------------------------

def infer_worker_count_from_ledger(ui: UiState) -> int | None:
    """Best-effort inference of worker pool size from recent ledger rows.

    Args:
        ui: UI state.

    Returns:
        Number of distinct workers inferred (``wid`` max + 1) or ``None``.
    """
    df = tail_ledger_df(ui.data_dir, n=5000)
    if df is None or df.empty or "wid" not in df:
        return None
    try:
        wids = [int(x) for x in df["wid"].dropna().unique().tolist()]
        return (max(wids) + 1) if wids else None
    except Exception:
        return None


def now_ts() -> float:
    """Return POSIX seconds (float).

    Returns:
        Current POSIX timestamp as ``float``.

    Examples:
        ::
            >>> isinstance(now_ts(), float)
            True
    """
    return time.time()


__all__ = [
    "UiState",
    "UiPrefs",
    "DEFAULT_DATA_DIR",
    "UI_PREFS_NAME",
    "get_state",
    "set_default_url",
    "tail_ledger_df",
    "read_schedules_jsonl",
    "read_catalog",
    "append_pulse",
    "infer_worker_count_from_ledger",
    "now_ts",
]
