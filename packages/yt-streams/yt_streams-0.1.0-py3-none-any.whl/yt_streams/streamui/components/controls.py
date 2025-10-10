"""Streamlit Controls panel for :mod:`yt_streams`.

Purpose:
    Provide a rich, ergonomic surface to enqueue **pulses** and **schedules**
    into the file-based control channel that a running
    :class:`~yt_streams.controller.PoolController` consumes. This component
    does not talk to browsers directly; it only appends JSONL commands and
    writes small UI config files (default URL, recent URLs).

Design:
    - High-level operations:
        • "Pulse": one-off play cycle, either fixed duration or randomized
          by (min, max, optional jitter). Supports batch over many URLs.
        • "Schedule": create interval or cron registrations. Validates inputs
          and renders a dry-run preview before appending.
    - URL management:
        • Resolve a default URL from flag → env (`YT_STREAMS_DEFAULT_URL`)
          → `<data_dir>/config/default_url.txt`.
        • Maintain a recent URLs JSONL and render them as quick-pick chips.
        • Accept URLs via single input, multi-line text, CSV upload (.csv or
          .jsonl with `url` column/field), and (optionally) a lightweight peek
          at the Airflow/catalog file if present.
    - Persisted artifacts (all under `<data_dir>`):
        • Control input   : `commands.jsonl` (append-only) — written here.
        • Schedules mirror: `schedules.jsonl` (read by other panels).
        • UI config       : `config/default_url.txt`, `config/recent_urls.jsonl`.

Public API:
    render_controls(data_dir: Path, default_url: str | None, key_prefix: str = "ctrl") -> None
        Render the full Controls panel.

Args & UI:
    - `data_dir` (Path): Root directory for artifacts. Must be the same folder
      that the running controller/broker uses.
    - `default_url` (str | None): Optional default URL passed by the app runner
      (e.g., from CLI). If not provided, we fallback to env/file via helper.
    - `key_prefix` (str): Session-state namespace for Streamlit keys.

Examples:
    ::
        >>> # In your Streamlit app:
        >>> from pathlib import Path  # doctest: +SKIP
        >>> from yt_streams.streamui.components.controls import render_controls  # doctest: +SKIP
        >>> render_controls(data_dir=Path("data/yt_streams"), default_url=None)  # doctest: +SKIP

Notes:
    *Compliance*: Use to test your own content; automated viewing to manipulate
    counters may violate YouTube ToS.
    *Purity*: This module performs only file I/O (append JSONL, small config).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import csv
import io
import json
import random
import re
import streamlit as st

from ...control import ControlCommand, append_command
from .utils import (
    load_recent_urls,
    pick_effective_default_url,
    record_recent_urls,
    save_default_url,
)

# ------------------------------ helpers & models ------------------------------


@dataclass(slots=True)
class _PulsePlan:
    """Resolved plan for a pulse batch.

    Args:
        urls: Final list of URLs that will be targeted by pulses.
        count: Number of pulses to emit per URL (>=1).
        play_seconds: If not None, fixed per-pulse duration (>=5).
        play_min: If play_seconds is None, lower bound for random range (>=5).
        play_max: If play_seconds is None, upper bound for random range (>=5).
        jitter: Extra random ± seconds applied per pulse (>=0).
        note: Annotation propagated to the command (e.g., 'ui:pulse').

    Invariants:
        - Exactly one of (play_seconds) or (play_min and play_max) is active.
    """
    urls: list[str]
    count: int
    play_seconds: int | None
    play_min: int | None
    play_max: int | None
    jitter: int
    note: str

    def pretty(self) -> str:
        if self.play_seconds is not None:
            base = f"{self.play_seconds}s"
        else:
            base = f"{self.play_min}-{self.play_max}s"
        if self.jitter:
            base += f" ±{self.jitter}s"
        return f"{self.count}× per URL @ {base}"


@dataclass(slots=True)
class _SchedulePlan:
    """Resolved plan for a schedule registration.

    Args:
        kind: 'interval' or 'cron'
        spec: textual spec ('HH:MM:SS' etc. for interval, cron expr for cron)
        play_seconds: Fixed play seconds (>=5) or None to indicate randomized.
        play_min/play_max: Optional range if not fixed.
        note: Annotation for traceability.
    """
    kind: str
    spec: str
    play_seconds: int | None
    play_min: int | None
    play_max: int | None
    note: str

    def label(self) -> str:
        if self.kind == "interval":
            what = self.spec
        else:
            what = f"cron: {self.spec}"
        if self.play_seconds is not None:
            dur = f"{self.play_seconds}s"
        else:
            dur = f"{self.play_min}-{self.play_max}s"
        return f"{what} → {dur}"


_URL_RE = re.compile(r"https?://\S+", re.IGNORECASE)


def _dedup(seq: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for s in seq:
        s2 = s.strip()
        if not s2 or s2 in seen:
            continue
        seen.add(s2)
        out.append(s2)
    return out


def _parse_freeform(text: str) -> list[str]:
    """Extract URLs from free-text (newline or whitespace separated)."""
    if not text.strip():
        return []
    # pick obvious URLs OR split by lines
    hits = _URL_RE.findall(text)
    if hits:
        return _dedup(hits)
    return _dedup([ln.strip() for ln in text.splitlines() if ln.strip()])


def _parse_csv(file_bytes: bytes) -> list[str]:
    """Parse URLs from uploaded CSV/JSONL with 'url' field/column."""
    if not file_bytes:
        return []
    data = file_bytes.decode("utf-8", errors="ignore")
    # try JSONL first
    lines = data.splitlines()
    jsonl_like = sum(1 for ln in lines[:20] if ln.strip().startswith("{")) >= 3
    if jsonl_like:
        urls: list[str] = []
        for ln in lines:
            ln = ln.strip()
            if not ln:
                continue
            try:
                obj = json.loads(ln)
            except Exception:
                continue
            u = (obj.get("url") or "").strip()
            if u:
                urls.append(u)
        return _dedup(urls)
    # fallback CSV
    reader = csv.DictReader(io.StringIO(data))
    urls = [(row.get("url") or "").strip() for row in reader]
    return _dedup([u for u in urls if u])


def _pick_seconds(plan: _PulsePlan) -> int:
    """Pick a per-pulse duration respecting jitter and bounds."""
    if plan.play_seconds is not None:
        base = plan.play_seconds
    else:
        lo = max(5, int(plan.play_min or 5))
        hi = max(lo, int(plan.play_max or lo))
        base = random.randint(lo, hi)
    j = int(plan.jitter or 0)
    if j:
        base = max(5, base + random.randint(-j, j))
    return int(base)


def _dryrun_pulse_rows(plan: _PulsePlan, max_rows: int = 30) -> list[dict[str, str]]:
    """Produce a preview table of what will be appended as pulse commands."""
    rows: list[dict[str, str]] = []
    for u in plan.urls:
        for i in range(plan.count):
            ps = _pick_seconds(plan)
            rows.append({"url": u, "pulse": str(i + 1), "play_seconds": str(ps), "note": plan.note})
            if len(rows) >= max_rows:
                return rows
    return rows


def _emit_pulses(data_dir: Path, plan: _PulsePlan) -> int:
    """Append pulse commands to `commands.jsonl` and record recents.

    Returns:
        Number of control lines appended.
    """
    total = 0
    for u in plan.urls:
        for _ in range(plan.count):
            if plan.play_seconds is not None:
                args = {"play_seconds": int(plan.play_seconds), "url": u}
            else:
                args = {
                    "play_min": int(plan.play_min or 5),
                    "play_max": int(plan.play_max or 5),
                    "url": u,
                }
            append_command(data_dir, ControlCommand(verb="pulse", args=args, note=plan.note))
            total += 1
    record_recent_urls(data_dir, plan.urls, note="controls:pulse")
    return total


def _emit_schedule(data_dir: Path, plan: _SchedulePlan) -> int:
    """Append a schedule command to `commands.jsonl`."""
    if plan.kind not in {"interval", "cron"}:
        return 0
    args: dict[str, object] = {}
    if plan.kind == "interval":
        args["text"] = plan.spec
        verb = "interval"
    else:
        args["expr"] = plan.spec
        verb = "cron"
    if plan.play_seconds is not None:
        args["play_seconds"] = int(plan.play_seconds)
    else:
        args["play_min"] = int(plan.play_min or 5)
        args["play_max"] = int(plan.play_max or 5)
    append_command(data_dir, ControlCommand(verb=verb, args=args, note=plan.note))
    return 1


# -------------------------------- render panel --------------------------------


def render_controls(
    *,
    data_dir: Path,
    default_url: str | None = None,
    key_prefix: str = "ctrl",
) -> None:
    """Render the **Controls** panel.

    Args:
        data_dir: Root data directory (shared with controller/broker).
        default_url: Optional default URL from the app; we fallback internally
            to env/file via :func:`pick_effective_default_url` if None/blank.
        key_prefix: Streamlit session key namespace.

    Returns:
        ``None``. The function renders Streamlit widgets and may append to
        the control channel (`commands.jsonl`) and UI config files.

    Examples:
        ::
            >>> # render_controls(data_dir=Path("data/yt_streams"))  # doctest: +SKIP
    """
    st.markdown("## Controls")

    # ------------------------------- URLs row --------------------------------
    eff_default = pick_effective_default_url(flag_url=default_url, data_dir=data_dir)
    st.caption("Default URL is used when a field is left empty in batches.")
    recents = load_recent_urls(data_dir, max_items=20)

    url_box, chips_box, default_box = st.columns([2, 2, 1])

    # recent chips
    with chips_box:
        if recents:
            st.caption("Recent")
            chip_cols = st.columns(min(len(recents), 4))
            chosen: str | None = None
            for i, u in enumerate(recents[: len(chip_cols)]):
                if chip_cols[i].button(u, key=f"{key_prefix}-chip-{i}"):
                    chosen = u
            if chosen:
                st.session_state[f"{key_prefix}-single-url"] = chosen

    with url_box:
        single_url = st.text_input(
            "Single URL",
            value=st.session_state.get(f"{key_prefix}-single-url", eff_default or ""),
            placeholder="https://youtu.be/VIDEO_ID",
            key=f"{key_prefix}-single-url",
        )

    with default_box:
        st.caption("Default")
        if st.button("Set from Single URL", disabled=not (single_url or "").strip(), key=f"{key_prefix}-set-default"):
            save_default_url(data_dir, single_url.strip())
            st.success("Saved as default URL.")

    st.divider()

    # ----------------------------- Bulk URL intake ---------------------------
    st.markdown("### Targets")
    c1, c2 = st.columns([2, 1])

    with c1:
        bulk_text = st.text_area(
            "Paste URLs (one per line or any text with URLs)",
            placeholder="https://youtu.be/...\nhttps://www.youtube.com/watch?v=...\n...",
            key=f"{key_prefix}-bulk",
            height=120,
        )
    with c2:
        up = st.file_uploader(
            "Upload CSV/JSONL with a 'url' column/field",
            type=["csv", "jsonl"],
            key=f"{key_prefix}-upload",
        )

    # collect URLs: single + parsed bulk + uploaded
    urls: list[str] = []
    if single_url.strip():
        urls.append(single_url.strip())
    urls.extend(_parse_freeform(bulk_text or ""))
    if up is not None:
        urls.extend(_parse_csv(up.getvalue()))
    urls = _dedup([u for u in urls if _URL_RE.match(u)])

    with st.expander("Preview URLs", expanded=bool(urls)):
        if urls:
            st.write(f"**{len(urls)}** target(s):")
            st.code("\n".join(urls[:100]), language="text")
            if len(urls) > 100:
                st.caption(f"... and {len(urls) - 100} more.")
        else:
            st.info("No valid URLs yet. Add one above or rely on the default per pulse.")

    st.divider()

    # -------------------------------- Pulses ---------------------------------
    st.markdown("### Pulse (one-off)")

    pcol1, pcol2, pcol3, pcol4, pcol5 = st.columns([1, 1, 1, 1, 1])

    fixed = pcol1.toggle("Fixed", value=True, key=f"{key_prefix}-fixed")
    play_seconds = int(pcol2.number_input("Seconds", min_value=5, value=60, step=5, key=f"{key_prefix}-ps"))
    play_min = int(pcol3.number_input("Min", min_value=5, value=45, step=5, disabled=fixed, key=f"{key_prefix}-min"))
    play_max = int(pcol4.number_input("Max", min_value=5, value=90, step=5, disabled=fixed, key=f"{key_prefix}-max"))
    jitter = int(pcol5.number_input("Jitter ±s", min_value=0, value=0, step=5, key=f"{key_prefix}-jit"))

    rcol1, rcol2 = st.columns([1, 3])
    repeats = int(rcol1.number_input("Repeat per URL", min_value=1, value=1, step=1, key=f"{key_prefix}-rep"))
    note = rcol2.text_input("Note", value="ui:pulse", key=f"{key_prefix}-note")

    # build plan
    pulse_plan = _PulsePlan(
        urls=urls or ([eff_default] if eff_default else []),
        count=repeats,
        play_seconds=play_seconds if fixed else None,
        play_min=None if fixed else play_min,
        play_max=None if fixed else play_max,
        jitter=jitter,
        note=note,
    )

    with st.expander("Dry-run preview", expanded=True):
        if not pulse_plan.urls:
            st.warning("No URLs resolved (none given and no default set).")
        else:
            preview = _dryrun_pulse_rows(pulse_plan, max_rows=40)
            st.dataframe(preview, use_container_width=True, hide_index=True)

    pbtn1, pbtn2 = st.columns([1, 1])
    do_pulse = pbtn1.button("Append pulses", disabled=not pulse_plan.urls, key=f"{key_prefix}-pulse")
    if do_pulse:
        appended = _emit_pulses(data_dir, pulse_plan)
        st.success(f"Appended {appended} pulse command(s).")

    st.divider()

    # ----------------------------- Schedule builder ---------------------------
    st.markdown("### Schedule")

    sch_tab1, sch_tab2 = st.tabs(["Interval", "Cron"])

    with sch_tab1:
        scol = st.columns([1, 1, 1, 3])
        i_h = scol[0].number_input("Hours", min_value=0, value=0, step=1, key=f"{key_prefix}-ih")
        i_m = scol[1].number_input("Minutes", min_value=0, value=8, step=1, key=f"{key_prefix}-im")
        i_s = scol[2].number_input("Seconds", min_value=0, value=0, step=5, key=f"{key_prefix}-is")
        st.caption("Format: HH:MM:SS (zero-padded automatically).")

        icol = st.columns([1, 1, 1, 1, 2])
        i_fixed = icol[0].toggle("Fixed", value=True, key=f"{key_prefix}-ifixed")
        i_ps = int(icol[1].number_input("Seconds", min_value=5, value=60, step=5, key=f"{key_prefix}-ips"))
        i_min = int(icol[2].number_input("Min", min_value=5, value=45, step=5, disabled=i_fixed, key=f"{key_prefix}-imin"))
        i_max = int(icol[3].number_input("Max", min_value=5, value=90, step=5, disabled=i_fixed, key=f"{key_prefix}-imax"))
        i_note = icol[4].text_input("Note", value="ui:interval", key=f"{key_prefix}-inote")

        interval_text = f"{int(i_h):02d}:{int(i_m):02d}:{int(i_s):02d}"
        iplan = _SchedulePlan(
            kind="interval",
            spec=interval_text,
            play_seconds=i_ps if i_fixed else None,
            play_min=None if i_fixed else i_min,
            play_max=None if i_fixed else i_max,
            note=i_note,
        )
        st.write(f"Preview: **every {interval_text} → {('' if i_fixed else 'random ')}"
                 f"{(iplan.play_seconds or (str(iplan.play_min)+'-'+str(iplan.play_max)))}s**")
        if st.button("Append interval schedule", key=f"{key_prefix}-iappend"):
            _emit_schedule(data_dir, iplan)
            st.success("Interval schedule appended.")

    with sch_tab2:
        ccol = st.columns([2, 1, 1, 1, 2])
        expr = ccol[0].text_input("Cron (5 fields)", value="*/13 9-21 * * 1-5", key=f"{key_prefix}-expr")
        c_fixed = ccol[1].toggle("Fixed", value=True, key=f"{key_prefix}-cfixed")
        c_ps = int(ccol[2].number_input("Seconds", min_value=5, value=60, step=5, key=f"{key_prefix}-cps"))
        c_min = int(ccol[3].number_input("Min", min_value=5, value=45, step=5, disabled=c_fixed, key=f"{key_prefix}-cmin"))
        c_max = int(ccol[4].number_input("Max", min_value=5, value=90, step=5, disabled=c_fixed, key=f"{key_prefix}-cmax"))
        c_note = st.text_input("Note", value="ui:cron", key=f"{key_prefix}-cnote")

        # Minimal sanity check for 5 fields
        ok_fields = len([f for f in expr.strip().split() if f]) == 5
        if not ok_fields:
            st.warning("Cron expression must have exactly 5 fields.")

        cplan = _SchedulePlan(
            kind="cron",
            spec=expr.strip(),
            play_seconds=c_ps if c_fixed else None,
            play_min=None if c_fixed else c_min,
            play_max=None if c_fixed else c_max,
            note=c_note,
        )
        st.write(f"Preview: **{expr} → {('' if c_fixed else 'random ')}"
                 f"{(cplan.play_seconds or (str(cplan.play_min)+'-'+str(cplan.play_max)))}s**")

        if st.button("Append cron schedule", disabled=not ok_fields, key=f"{key_prefix}-cappend"):
            _emit_schedule(data_dir, cplan)
            st.success("Cron schedule appended.")

    st.divider()

    st.caption(
        "Control file: `commands.jsonl`. Schedules mirror: `schedules.jsonl`. "
        "Default & recents under `config/`."
    )
