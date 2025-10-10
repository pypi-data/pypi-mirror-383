"""Streamlit UI package for :mod:`yt_streams`.

Purpose:
    Compose a modular dashboard (Controls, Schedules, Schedules Viz, Catalog,
    Workers, Errors, Ledger/Stats, Config) that interacts with the controller
    purely via the **file control channel** and visualizes append-only
    artifacts (``runs.csv``, ``schedules.jsonl``, ``meta.jsonl``).

Design:
    - :mod:`yt_streams.streamui.state` defines session state & readers.
    - :mod:`yt_streams.streamui.components.*` are small, testable views.
    - :mod:`yt_streams.streamui.app` wires components into a Streamlit app.

Public API:
    - :func:`main` — entrypoint to render the Streamlit app.
    - State helpers: :func:`get_state`, :func:`set_state`,
      :func:`read_schedules_df`, :func:`tail_ledger_df`.
    - Component renderers: ``render_controls``, ``render_schedules``,
      ``render_schedules_viz``, ``render_catalog``, ``render_workers``,
      ``render_errors``, ``render_config``, ``render_ledger``.

Examples:
    Run via CLI (recommended)::

        $ yt-streams serve-streamlit --url "https://youtu.be/VIDEOID" --workers 3

    Or directly with Streamlit::

        $ python -m streamlit run -m yt_streams.streamui.app
"""
from __future__ import annotations

from typing import Final

from .app import main
from .state import UiState, get_state, set_default_url, read_schedules_jsonl, tail_ledger_df
from .components import (
    render_controls,
    render_schedules,
    render_schedules_viz,
    render_catalog,
    render_workers,
    render_errors,
    render_config,
    render_ledger,
)

__all__: Final[list[str]] = [
    # entry
    "main",
    # state
    "UiState",
    "get_state",
    "set_default_url",
    "read_schedules_jsonl",
    "tail_ledger_df",
    # components
    "render_controls",
    "render_schedules",
    "render_schedules_viz",
    "render_catalog",
    "render_workers",
    "render_errors",
    "render_config",
    "render_ledger",
]
