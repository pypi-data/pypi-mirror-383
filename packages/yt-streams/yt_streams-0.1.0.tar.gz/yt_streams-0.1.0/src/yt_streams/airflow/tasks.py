"""Framework-agnostic task helpers for Airflow DAGs.

Purpose:
    Provide small, importable functions that Airflow tasks can call to
    **append control commands** for the long-lived :mod:`yt_streams` controller.
    These helpers do **not** import Airflow, so the package remains usable
    without Airflow installed.

Features:
    - Append a one-off pulse with fixed/Random play windows.
    - Append a pulse **for a specific URL** (overriding controller default).
    - Append pulses chosen from a **catalog** (CSV/JSONL) of URLs with weights
      and on/off flags; supports weighted random and round-robin.
    - Optional sharding across **multiple data directories** to distribute load.

Catalog format:
    CSV or JSONL with at least the column ``url``. Optional columns:
    - ``weight`` (float/int) — selection weight (defaults to 1.0)
    - ``active`` (bool/int) — 1/true to include; 0/false to skip (default: 1)
    - ``note`` (str) — added to control message for traceability

Examples:
    Airflow TaskFlow usage (in a DAG file)::

        from airflow.decorators import dag, task
        from yt_streams.airflow.tasks import append_random_pulse_from_catalog

        @dag(schedule="*/13 9-21 * * 1-5", start_date=datetime(2025,1,1), catchup=False)
        def yt_streams_catalog():
            @task
            def fire():
                return append_random_pulse_from_catalog(
                    catalog_path="/srv/yt_streams/catalog.csv",
                    data_dirs=["/srv/yt_streams/a", "/srv/yt_streams/b"],
                    strategy="weighted",
                    play_min=45,
                    play_max=90,
                )
            fire()
        dag = yt_streams_catalog()
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal, Sequence
import json
import os
import random

try:
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover - optional in non-Airflow envs
    pd = None  # type: ignore

from yt_streams.control import ControlCommand, append_command


# ------------------------------- Basic pulses --------------------------------

def append_random_pulse(
    *,
    data_dir: str | os.PathLike | None = None,
    play_seconds: int | None = None,
    play_min: int = 45,
    play_max: int = 90,
    note: str = "airflow:pulse",
) -> str:
    """Append a one-off pulse to the broker control file.

    Args:
        data_dir: Control directory (defaults to ``$YT_STREAMS_DATA_DIR`` or ``data/yt_streams``).
        play_seconds: Fixed window; if ``None`` use a random value.
        play_min: Minimum randomized window (inclusive).
        play_max: Maximum randomized window (inclusive).
        note: Optional annotation for traceability.

    Returns:
        A short string describing the action.
    """
    root = Path(data_dir or os.environ.get("YT_STREAMS_DATA_DIR", "data/yt_streams"))
    if play_seconds is None:
        lo, hi = sorted((int(play_min), int(play_max)))
        ps = random.randint(lo, hi)
    else:
        ps = int(play_seconds)
    append_command(root, ControlCommand.pulse(play_seconds=ps, note=note))
    return f"pulse {ps}s → {root}"


def append_pulse_for_url(
    *,
    url: str,
    data_dir: str | os.PathLike | None = None,
    play_seconds: int | None = None,
    play_min: int = 45,
    play_max: int = 90,
    note: str = "airflow:url",
) -> str:
    """Append a pulse **for a specific URL**.

    The controller must support per-pulse URL override. Our control broker
    includes the ``url`` in the command args; the controller can pass it into
    the play cycle.

    Args:
        url: YouTube watch URL.
        data_dir: Control directory.
        play_seconds: Fixed or randomized window.
        play_min: Random minimum.
        play_max: Random maximum.
        note: Annotation.
    """
    root = Path(data_dir or os.environ.get("YT_STREAMS_DATA_DIR", "data/yt_streams"))
    if play_seconds is None:
        lo, hi = sorted((int(play_min), int(play_max)))
        ps = random.randint(lo, hi)
    else:
        ps = int(play_seconds)
    # include URL as part of pulse args via note (and args)
    cmd = ControlCommand(verb="pulse", args={"play_seconds": ps, "url": url}, note=note)
    append_command(root, cmd)
    return f"pulse {ps}s for {url} → {root}"


# ------------------------------- Catalog pulses -------------------------------

@dataclass(slots=True)
class CatalogItem:
    url: str
    weight: float = 1.0
    active: bool = True
    note: str | None = None


def _load_catalog(path: str | os.PathLike) -> list[CatalogItem]:
    p = Path(path)
    if not p.exists():
        return []
    # JSONL first
    if p.suffix.lower() in {".jsonl", ".ndjson"}:
        items: list[CatalogItem] = []
        with p.open("r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s:
                    continue
                try:
                    o = json.loads(s)
                    items.append(
                        CatalogItem(
                            url=str(o.get("url", "")),
                            weight=float(o.get("weight", 1.0)),
                            active=bool(o.get("active", True)),
                            note=(o.get("note") if o.get("note") else None),
                        )
                    )
                except Exception:
                    continue
        return [i for i in items if i.url]
    # CSV via pandas (optional dep)
    if pd is None:
        # fallback: naive CSV reader
        items: list[CatalogItem] = []
        with p.open("r", encoding="utf-8") as f:
            header = f.readline().strip().split(",")
            idx = {k: i for i, k in enumerate(header)}
            for line in f:
                parts = line.strip().split(",")
                url = parts[idx.get("url", -1)] if idx.get("url", -1) >= 0 else ""
                if not url:
                    continue
                weight = float(parts[idx.get("weight", -1)]) if idx.get("weight", -1) >= 0 else 1.0
                active = parts[idx.get("active", -1)].lower() in {"1", "true", "yes"} if idx.get("active", -1) >= 0 else True
                note = parts[idx.get("note", -1)] if idx.get("note", -1) >= 0 else None
                items.append(CatalogItem(url=url, weight=weight, active=active, note=note))
        return [i for i in items if i.url]
    # pandas path
    try:
        df = pd.read_csv(p)
        df = df.fillna({"weight": 1.0, "active": 1})
        df["active"] = df["active"].astype(bool)
    except Exception:
        return []
    out: list[CatalogItem] = []
    for row in df.itertuples(index=False):
        url = getattr(row, "url", "")
        if not url:
            continue
        weight = float(getattr(row, "weight", 1.0))
        active = bool(getattr(row, "active", True))
        note = getattr(row, "note", None)
        out.append(CatalogItem(url=url, weight=weight, active=active, note=note))
    return out


def _choose_weighted(items: Sequence[CatalogItem]) -> CatalogItem | None:
    candidates = [i for i in items if i.active]
    if not candidates:
        return None
    weights = [max(0.0, i.weight) for i in candidates]
    if sum(weights) == 0.0:
        weights = [1.0] * len(candidates)
    return random.choices(candidates, weights=weights, k=1)[0]


def append_random_pulse_from_catalog(
    *,
    catalog_path: str | os.PathLike,
    data_dirs: Sequence[str | os.PathLike] | None = None,
    strategy: Literal["weighted", "first"] = "weighted",
    play_seconds: int | None = None,
    play_min: int = 45,
    play_max: int = 90,
    shard_choose: Literal["random", "round"] = "random",
    note_prefix: str = "airflow:catalog",
) -> str:
    """Select a URL from a catalog and append a targeted pulse.

    Args:
        catalog_path: CSV/JSONL catalog path.
        data_dirs: One or more control directories; if many, choose one.
        strategy: Selection policy: ``"weighted"`` or ``"first"`` active row.
        play_seconds: Fixed or randomized window.
        play_min: Random minimum if not fixed.
        play_max: Random maximum if not fixed.
        shard_choose: How to select among ``data_dirs`` when multiple supplied.
        note_prefix: Added to note for traceability.

    Returns:
        Human-readable description of the action.
    """
    items = _load_catalog(catalog_path)
    if not items:
        raise FileNotFoundError(f"empty or missing catalog: {catalog_path}")

    item: CatalogItem | None
    if strategy == "first":
        item = next((i for i in items if i.active), None)
    else:
        item = _choose_weighted(items)
    if item is None:
        raise RuntimeError("no active items in catalog")

    # choose a shard (data_dir)
    shard: Path
    if not data_dirs:
        shard = Path(os.environ.get("YT_STREAMS_DATA_DIR", "data/yt_streams"))
    else:
        choices = [Path(d) for d in data_dirs]
        shard = random.choice(choices) if shard_choose == "random" else choices[0]

    # choose play window
    if play_seconds is None:
        lo, hi = sorted((int(play_min), int(play_max)))
        ps = random.randint(lo, hi)
    else:
        ps = int(play_seconds)

    note = f"{note_prefix}:{item.note}" if item.note else note_prefix
    cmd = ControlCommand(verb="pulse", args={"play_seconds": ps, "url": item.url}, note=note)
    append_command(shard, cmd)
    return f"pulse {ps}s for {item.url} → {shard}"
