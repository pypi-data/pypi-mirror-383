"""Ledger visualization component for :mod:`yt_streams` Streamlit UI.

Purpose:
    Read and visualize the append-only run ledger (``runs.csv``) that the
    controller/workers write. Provide quick health KPIs, filtering, a timeline
    chart, and a downloadable slice for offline analysis.

Design:
    - Input: CSV with stable columns:
        * ts (float seconds), wid (int), phase (str), play_seconds (int),
          refreshes (int), error (str|blank)
    - We ingest with pandas (if available) and apply in-memory filters only.
      No mutation. When pandas isn’t available, we degrade gracefully.

Public API:
    - :func:`render_ledger`

Columns expected:
    ts,wid,phase,play_seconds,refreshes,error

Examples:
    Minimal integration (inside Streamlit app)::

        >>> # doctest: +SKIP
        >>> from yt_streams.streamui.state import UiState
        >>> from yt_streams.streamui.components.ledger import render_ledger
        >>> ui: UiState = ...
        >>> render_ledger(ui)
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final, Iterable

import json
import time

import streamlit as st

try:
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover
    pd = None  # type: ignore

try:  # plotly is optional; Streamlit will render it inline
    import plotly.express as px  # type: ignore
except Exception:  # pragma: no cover
    px = None  # type: ignore

from yt_streams.streamui.state import UiState


LEDGER_FILENAME: Final[str] = "runs.csv"
DEFAULT_LOOKBACK_ROWS: Final[int] = 50_000


# ------------------------------- helpers & types -------------------------------

@dataclass(slots=True)
class _Filters:
    """Filtering options selected in the UI.

    Args:
        since_ts: POSIX timestamp lower bound (None = unbounded).
        wid_in: Acceptable worker ids (None/empty = no filter).
        phase_in: Acceptable phases (None/empty = no filter).
        errors_only: If True, keep rows with non-empty error.
        max_rows: Upper bound on rows after filtering (for perf).
    """
    since_ts: float | None
    wid_in: set[int] | None
    phase_in: set[str] | None
    errors_only: bool
    max_rows: int


def _ledger_path(root: Path) -> Path:
    return root / LEDGER_FILENAME


def _load_ledger_df(path: Path, *, approx_tail_rows: int = DEFAULT_LOOKBACK_ROWS) -> pd.DataFrame | None:
    """Load (roughly) the last N rows of the ledger as a DataFrame.

    We do a fast tail by reading the file and letting pandas parse. If the file
    is small, it loads everything. Returns ``None`` if pandas is unavailable or
    the file is missing/empty.
    """
    if pd is None:
        return None
    if not path.exists():
        return None
    try:
        # Let pandas read the CSV; if the file is large, we can sample the tail
        # via python first to reduce memory (cheap heuristic).
        size = path.stat().st_size
        if size > 8_000_000:  # ~8 MB → tail read
            # Read last ~approx_tail_rows lines
            with path.open("rb") as f:
                f.seek(max(0, size - 2_000_000))  # ~2MB window; adjust as needed
                buf = f.read().decode("utf-8", errors="ignore")
            lines = buf.splitlines()
            # Keep header (first line that starts with the known header prefix)
            header_idx = 0
            for i, ln in enumerate(lines):
                if ln.startswith("ts,wid,phase,play_seconds,refreshes,error"):
                    header_idx = i
                    break
            lines = lines[header_idx:]
            if len(lines) > approx_tail_rows + 1:
                lines = [lines[0]] + lines[-approx_tail_rows:]
            df = pd.read_csv(pd.compat.StringIO("\n".join(lines)))
        else:
            df = pd.read_csv(path)
    except Exception:
        return None

    if df.empty:
        return None

    # Normalize dtypes
    for col in ("ts", "play_seconds"):
        if col in df.columns:
            with pd.option_context("future.no_silent_downcasting", True):
                df[col] = pd.to_numeric(df[col], errors="coerce")
    if "wid" in df.columns:
        with pd.option_context("future.no_silent_downcasting", True):
            df["wid"] = pd.to_numeric(df["wid"], errors="coerce").astype("Int64")
    if "refreshes" in df.columns:
        with pd.option_context("future.no_silent_downcasting", True):
            df["refreshes"] = pd.to_numeric(df["refreshes"], errors="coerce").fillna(0).astype("Int64")
    # Human time
    if "ts" in df.columns:
        df["when"] = pd.to_datetime(df["ts"], unit="s", errors="coerce")
    # Clean error blanks to NaN for convenience
    if "error" in df.columns:
        df["error"] = df["error"].astype(str).replace({"": None, "nan": None})
    return df


def _apply_filters(df: pd.DataFrame, f: _Filters) -> pd.DataFrame:
    out = df
    if f.since_ts is not None and "ts" in out:
        out = out[out["ts"] >= float(f.since_ts)]
    if f.wid_in:
        out = out[out["wid"].isin(list(f.wid_in))]
    if f.phase_in and "phase" in out:
        out = out[out["phase"].isin(list(f.phase_in))]
    if f.errors_only and "error" in out:
        out = out[out["error"].notna() & (out["error"].astype(str) != "")]
    if f.max_rows > 0 and len(out) > f.max_rows:
        out = out.tail(f.max_rows)
    return out


def _kpi(df: pd.DataFrame) -> tuple[int, float, int]:
    """Return (rows, avg_play_seconds, sum_refreshes)."""
    rows = int(len(df))
    avg_ps = float(df["play_seconds"].mean()) if "play_seconds" in df and rows else 0.0
    ref_sum = int(df["refreshes"].fillna(0).sum()) if "refreshes" in df else 0
    return rows, avg_ps, ref_sum


def _timeline_chart(df: pd.DataFrame):
    """Build a Plotly timeline-like scatter of plays over time (if plotly present)."""
    if px is None:
        return None
    if df.empty or "when" not in df or "wid" not in df:
        return None
    # We’ll plot points at when, colored by phase, faceted by worker count if small.
    data = df.copy()
    data = data.sort_values("when")
    data["wid_str"] = data["wid"].astype(str)
    fig = px.scatter(
        data_frame=data,
        x="when",
        y="wid_str",
        color=("phase" if "phase" in data else None),
        size=("play_seconds" if "play_seconds" in data else None),
        hover_data=["play_seconds", "refreshes", "error"],
        title="Runs over time",
    )
    fig.update_layout(height=340, margin=dict(l=10, r=10, t=40, b=10))
    return fig


# ----------------------------------- render -----------------------------------

def render_ledger(
    ui: UiState,
    *,
    default_lookback_minutes: int = 120,
    max_rows: int = 20_000,
    key_prefix: str = "ledger",
) -> None:
    """Render the ledger KPI bar, filters, timeline chart, and table.

    Args:
        ui: UI state with ``data_dir``.
        default_lookback_minutes: Initial time window for filtering.
        max_rows: Max rows to keep after filters (performance guardrail).
        key_prefix: Streamlit widget namespace.

    Returns:
        ``None``; renders into the Streamlit page.

    Raises:
        RuntimeError: If Streamlit or pandas imports are missing.
    """
    if pd is None:
        st.warning("pandas is required for the ledger view.")
        return

    st.subheader("Ledger")

    p = _ledger_path(ui.data_dir)
    st.caption(f"Ledger file: `{p}`")

    # Auto-refresh
    auto = st.toggle("Auto-refresh", value=True, key=f"{key_prefix}-auto")
    if auto:
        st.autorefresh(interval=10_000, key=f"{key_prefix}-refresh")

    df = _load_ledger_df(p)
    if df is None or df.empty:
        st.info("No ledger data yet.")
        return

    # ------------------------------ Filter panel ------------------------------
    with st.expander("Filters", expanded=True):
        cols1 = st.columns([1, 1, 1, 1, 2])
        now_ts = time.time()
        lookback_min = cols1[0].number_input(
            "Lookback (minutes)",
            min_value=1,
            max_value=24 * 60,
            value=int(default_lookback_minutes),
            step=5,
            key=f"{key_prefix}-lookback",
        )
        since_ts = now_ts - (lookback_min * 60)

        # Distinct workers & phases
        wids = sorted(x for x in df["wid"].dropna().unique().tolist() if x is not None)
        phases = sorted([str(x) for x in df.get("phase", pd.Series(dtype=str)).dropna().unique().tolist()])

        wid_sel = cols1[1].multiselect("Workers", options=wids, default=wids, key=f"{key_prefix}-wids")
        ph_sel = cols1[2].multiselect("Phases", options=phases, default=phases, key=f"{key_prefix}-phases")
        errors_only = cols1[3].toggle("Errors only", value=False, key=f"{key_prefix}-errors")
        max_rows_sel = cols1[4].slider(
            "Max rows after filtering",
            min_value=1_000,
            max_value=max_rows,
            value=min(max_rows, 10_000),
            step=1_000,
            key=f"{key_prefix}-maxrows",
        )

    filt = _Filters(
        since_ts=since_ts,
        wid_in=set(int(w) for w in wid_sel) if wid_sel else None,
        phase_in=set(str(p) for p in ph_sel) if ph_sel else None,
        errors_only=bool(errors_only),
        max_rows=int(max_rows_sel),
    )
    view = _apply_filters(df, filt)

    # ----------------------------------- KPIs ---------------------------------
    rows, avg_ps, ref_sum = _kpi(view)
    k1, k2, k3 = st.columns(3)
    k1.metric("Rows", rows)
    k2.metric("Avg play (s)", f"{avg_ps:0.1f}")
    k3.metric("Refreshes (sum)", ref_sum)

    # --------------------------------- Timeline --------------------------------
    fig = _timeline_chart(view)
    if fig is not None:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.caption("Install plotly to see the timeline chart.")

    # ---------------------------------- Table ----------------------------------
    show_cols = [c for c in ("when", "ts", "wid", "phase", "play_seconds", "refreshes", "error") if c in view.columns]
    st.dataframe(
        view[show_cols].sort_values("when", ascending=False),
        hide_index=True,
        use_container_width=True,
        height=360,
    )

    # -------------------------------- Download ---------------------------------
    csv_bytes = view[show_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered CSV",
        data=csv_bytes,
        file_name="yt_streams_ledger_filtered.csv",
        mime="text/csv",
        use_container_width=False,
        type="secondary",
        key=f"{key_prefix}-dl",
    )


__all__: Final[list[str]] = ["render_ledger", "LEDGER_FILENAME", "DEFAULT_LOOKBACK_ROWS"]
