"""Schedules visualization component for :mod:`yt_streams` Streamlit UI.

Purpose:
    Read the append-only schedule mirror (``schedules.jsonl``) and render a
    compact, filterable view of currently registered schedules. This is a
    **read-only** visualization by default to avoid side effects from the UI.
    You may optionally enable light controls (pause/resume/remove) which append
    control commands; these require broker support for the ``schedule_ctl`` verb.

Design:
    - Input: append-only JSONL mirror written by :mod:`yt_streams.control`
      (each accepted registration appends a record like:
      ``{"ts": ..., "kind": "interval"|"cron", "job_id": "...", ...}``).
    - Folding: multiple mirror rows may exist for the same ``job_id`` (e.g.,
      re-register). We fold to the *latest* row per job id.
    - Optional controls: When ``enable_controls=True``, we render Pause/Resume/
      Remove buttons. Clicking appends a control command to
      ``commands.jsonl`` using :func:`yt_streams.control.append_command`.
      Your :class:`~yt_streams.control.ControlBroker` must implement the
      ``"schedule_ctl"`` verb (not required for visualization).

Public API:
    - :func:`render_schedules`

Attributes:
    MIRROR_FILENAME (str): Name of schedule mirror file (``schedules.jsonl``).
    DEFAULT_LOOKBACK (int): Maximum rows to consider from the tail (approx).

Examples:
    Minimal integration (read-only)::

        >>> # inside Streamlit app (doctest skipped)                         # doctest: +SKIP
        >>> from yt_streams.streamui.state import UiState                     # doctest: +SKIP
        >>> from yt_streams.streamui.components.schedules_viz import render_schedules  # doctest: +SKIP
        >>> ui: UiState = ...                                                # doctest: +SKIP
        >>> render_schedules(ui)                                             # doctest: +SKIP

    With controls enabled (requires broker handling ``schedule_ctl``)::

        >>> render_schedules(ui, enable_controls=True)                        # doctest: +SKIP
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final, Iterable, Literal, TypedDict

import json
import time

import streamlit as st

try:
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover
    pd = None  # type: ignore

from yt_streams.streamui.state import UiState
from yt_streams.control import ControlCommand, append_command


MIRROR_FILENAME: Final[str] = "schedules.jsonl"
DEFAULT_LOOKBACK: Final[int] = 5000  # approx tail rows to scan


# ------------------------------- typed helpers --------------------------------

class MirrorRow(TypedDict, total=False):
    ts: float
    kind: Literal["interval", "cron"]
    job_id: str
    text: str         # for interval
    expr: str         # for cron
    play_seconds: int | None
    note: str | None


@dataclass(slots=True)
class _Filters:
    """UI-side filters for visualization.

    Args:
        kind: Filter by schedule kind ("interval"|"cron"|None)
        q: Substring filter against text/expr/note/job_id (case-insensitive)
    """
    kind: str | None
    q: str | None


def _now() -> float:
    return time.time()


def _mirror_path(root: Path) -> Path:
    return root / MIRROR_FILENAME


def _load_mirror_rows(path: Path, *, approx_tail: int = DEFAULT_LOOKBACK) -> list[MirrorRow]:
    """Load the last ~N rows of the schedules mirror efficiently.

    Args:
        path: Path to ``schedules.jsonl``.
        approx_tail: Rough number of rows to read from the end.

    Returns:
        List of parsed ``MirrorRow`` dicts (best effort); malformed lines are ignored.
    """
    out: list[MirrorRow] = []
    if not path.exists():
        return out

    # read last ~N lines by bytes heuristic
    size = path.stat().st_size
    # assume ~140 bytes per JSON line → scale bytes to read
    chunk = min(size, max(4096, approx_tail * 140))
    with path.open("rb") as f:
        f.seek(max(0, size - chunk))
        buf = f.read().decode("utf-8", errors="ignore")
    lines = buf.splitlines()
    for ln in lines[-approx_tail:]:
        s = ln.strip()
        if not s:
            continue
        try:
            obj = json.loads(s)
        except Exception:
            continue
        mr: MirrorRow = {}
        mr["ts"] = float(obj.get("ts", 0.0))
        k = str(obj.get("kind", "")).strip()
        if k in ("interval", "cron"):
            mr["kind"] = k  # type: ignore[assignment]
        if "job_id" in obj and obj["job_id"]:
            mr["job_id"] = str(obj["job_id"])
        if "text" in obj and obj["text"]:
            mr["text"] = str(obj["text"])
        if "expr" in obj and obj["expr"]:
            mr["expr"] = str(obj["expr"])
        if "play_seconds" in obj:
            try:
                mr["play_seconds"] = int(obj["play_seconds"])
            except Exception:
                mr["play_seconds"] = None
        note = obj.get("note")
        mr["note"] = (str(note) if note is not None else None)
        out.append(mr)
    return out


def _fold_latest_by_job(rows: Iterable[MirrorRow]) -> list[MirrorRow]:
    """Keep only the latest row per job_id (stable sort by job_id)."""
    latest: dict[str, MirrorRow] = {}
    for r in rows:
        jid = str(r.get("job_id") or "")
        if not jid:
            # mirror rows without job ids are not actionable; keep but bucket under empty
            jid = ""
        prev = latest.get(jid)
        if (prev is None) or float(r.get("ts", 0.0)) >= float(prev.get("ts", 0.0)):
            latest[jid] = r
    # order by job_id then time desc for empty job_id bucket
    keyed = sorted(latest.items(), key=lambda kv: (kv[0], -float(kv[1].get("ts", 0.0))))
    return [v for _, v in keyed]


def _fmt_age(ts: float) -> str:
    try:
        dt = _now() - float(ts)
        if dt < 60:
            return f"{int(dt)}s ago"
        if dt < 3600:
            return f"{int(dt // 60)}m ago"
        return f"{int(dt // 3600)}h ago"
    except Exception:
        return "-"


def _apply_filters(rows: list[MirrorRow], f: _Filters) -> list[MirrorRow]:
    out = rows
    if f.kind in ("interval", "cron"):
        out = [r for r in out if r.get("kind") == f.kind]
    q = (f.q or "").strip().lower()
    if q:
        def hit(r: MirrorRow) -> bool:
            hay = " ".join(
                str(x)
                for x in (
                    r.get("job_id", ""),
                    r.get("text", ""),
                    r.get("expr", ""),
                    r.get("note", ""),
                )
                if x is not None
            ).lower()
            return q in hay
        out = [r for r in out if hit(r)]
    return out


# ---------------------------------- render ------------------------------------

def render_schedules(
    ui: UiState,
    *,
    enable_controls: bool = False,
    approx_tail: int = DEFAULT_LOOKBACK,
    key_prefix: str = "sched",
) -> None:
    """Render the schedules visualization from ``schedules.jsonl``.

    Args:
        ui:
            The :class:`~yt_streams.streamui.state.UiState` holding paths and
            session configuration.
        enable_controls:
            If ``True``, render Pause/Resume/Remove buttons that append
            ``schedule_ctl`` commands to the control channel. Your broker must
            implement that verb; otherwise clicks are a no-op for the system.
        approx_tail:
            Rough number of mirror lines to read from the file tail.
        key_prefix:
            Streamlit widget key namespace.

    Returns:
        ``None``. Renders a table-like layout into the current Streamlit page.

    Raises:
        RuntimeError: If Streamlit is not importable.

    Examples:
        ::
            >>> # read-only visualization
            >>> # render_schedules(ui)  # doctest: +SKIP
    """
    try:
        import streamlit as st  # ensure runtime dep present (already imported above)
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Streamlit is required to render schedules") from exc

    st.subheader("Schedules")

    mirror = _mirror_path(ui.data_dir)
    st.caption(f"Mirror file: `{mirror}`")

    # Controls row
    c1, c2, c3 = st.columns([1, 1, 2])
    kind = c1.selectbox(
        "Kind",
        options=["all", "interval", "cron"],
        index=0,
        key=f"{key_prefix}-kind",
    )
    q = c2.text_input("Filter (job/text/expr/note)", value="", key=f"{key_prefix}-q")
    auto = c3.toggle("Auto-refresh", value=True, key=f"{key_prefix}-auto")
    if auto:
        import time
        time.sleep(10)  # 10 second refresh interval
        st.rerun()

    rows = _load_mirror_rows(mirror, approx_tail=approx_tail)
    folded = _fold_latest_by_job(rows)
    filt = _Filters(kind=None if kind == "all" else kind, q=q)
    view = _apply_filters(folded, filt)

    if not view:
        st.info("No schedule registrations found.")
        return

    # If pandas available, render a nicer grid; otherwise cards
    if pd is not None:
        df = pd.DataFrame(view)
        # shape + pretty columns
        if not df.empty:
            df = df.assign(
                when=df["ts"].map(_fmt_age),
                details=df.apply(
                    lambda r: (r["text"] if r.get("text") else r.get("expr") or ""),
                    axis=1,
                ),
            )
            cols = ["when", "kind", "job_id", "details", "play_seconds", "note"]
            # pad missing columns to keep dataframe consistent
            for c in cols:
                if c not in df.columns:
                    df[c] = ""
            df = df[cols].sort_values(["kind", "job_id"])
        st.dataframe(df, hide_index=True, use_container_width=True)
    else:
        # simple card list
        for r in view:
            st.markdown(
                f"- **{r.get('kind','?')}** — `{r.get('job_id','')}` • "
                f"{_fmt_age(float(r.get('ts', 0.0)))} • "
                f"{r.get('text') or r.get('expr') or ''} • "
                f"play={r.get('play_seconds','-')} • "
                f"{('note='+r['note']) if r.get('note') else ''}"
            )

    # Optional control buttons (best-effort append)
    if enable_controls:
        st.markdown("#### Control")
        st.caption("Pause/Resume/Remove send `schedule_ctl` commands; requires broker support.")
        for r in view:
            jid = str(r.get("job_id") or "")
            if not jid:
                continue
            c1, c2, c3, c4 = st.columns([1, 1, 1, 5])
            c1.write(f"`{jid}`")
            if c2.button("Pause", key=f"{key_prefix}-pause-{jid}"):
                append_command(ui.data_dir, ControlCommand(verb="schedule_ctl", args={"op": "pause", "job_id": jid}, note="ui:schedule_ctl"))
                st.toast(f"pause → {jid}", icon="⏸️")
            if c3.button("Resume", key=f"{key_prefix}-resume-{jid}"):
                append_command(ui.data_dir, ControlCommand(verb="schedule_ctl", args={"op": "resume", "job_id": jid}, note="ui:schedule_ctl"))
                st.toast(f"resume → {jid}", icon="▶️")
            if c4.button("Remove", key=f"{key_prefix}-remove-{jid}"):
                append_command(ui.data_dir, ControlCommand(verb="schedule_ctl", args={"op": "remove", "job_id": jid}, note="ui:schedule_ctl"))
                st.toast(f"remove → {jid}", icon="🗑️")


__all__: Final[list[str]] = ["render_schedules", "MIRROR_FILENAME", "DEFAULT_LOOKBACK"]
