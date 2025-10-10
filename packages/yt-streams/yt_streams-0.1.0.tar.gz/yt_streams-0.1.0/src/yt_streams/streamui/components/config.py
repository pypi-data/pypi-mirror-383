"""Config component for the Streamlit UI of :mod:`yt_streams`.

Purpose:
    Display effective configuration (selected env vars, data dir, catalog path)
    to make the runtime context explicit.

Public API:
    - :func:`render_config`
"""
from __future__ import annotations

from pathlib import Path
from typing import Final
import os

from yt_streams.streamui.state import UiState


def render_config(ui: UiState) -> None:
    """Render a compact configuration panel.

    Args:
        ui: The :class:`~yt_streams.streamui.state.UiState` for this session.

    Returns:
        ``None``. Renders Streamlit widgets.

    Raises:
        RuntimeError: If Streamlit is not available at runtime.
    """
    try:
        import streamlit as st  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Streamlit is required to render config") from exc

    st.subheader("Config")
    st.write({
        "data_dir": str(ui.data_dir),
        "default_url": ui.default_url,
        "workers": ui.workers,
        "randomize": ui.randomize,
        "play_seconds": ui.play_seconds,
        "rand_min": ui.rand_min,
        "rand_max": ui.rand_max,
        "YT_STREAMS_CATALOG": os.environ.get("YT_STREAMS_CATALOG", ""),
    })


__all__: Final[list[str]] = ["render_config"]
