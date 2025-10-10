"""Schedules view component for the Streamlit UI of :mod:`yt_streams`.

Purpose:
    Render a **read-only** table of accepted schedules mirrored by the
    controller into ``schedules.jsonl``. Intended to complement the Controls
    tab, which appends new schedules to the control channel.

Design:
    - Streamlit is imported inside the renderer for testability without UI.
    - Data access goes through :func:`yt_streams.streamui.state.read_schedules_df`.
    - Small, focused surface: one function, one responsibility.

Public API:
    - :func:`render_schedules`

Examples:
    Minimal integration::

        >>> # inside your Streamlit app (doctest skipped)             # doctest: +SKIP
        >>> from yt_streams.streamui.state import get_state           # doctest: +SKIP
        >>> from yt_streams.streamui.components.schedules import render_schedules  # doctest: +SKIP
        >>> ui = get_state()                                          # doctest: +SKIP
        >>> render_schedules(ui)                                      # doctest: +SKIP
"""
from __future__ import annotations

from typing import Final

from yt_streams.streamui.state import UiState, read_schedules_df


def render_schedules(ui: UiState) -> None:
    """Render the Schedules tab (read-only mirror).

    Args:
        ui: The :class:`~yt_streams.streamui.state.UiState` for this session.

    Returns:
        ``None``. Renders Streamlit widgets and a table if data exists.

    Raises:
        RuntimeError: If Streamlit is not available at runtime.
    """
    try:
        import streamlit as st  # type: ignore
    except Exception as exc:  # pragma: no cover - only raised in non-UI tests
        raise RuntimeError("Streamlit is required to render schedules") from exc

    st.subheader("Accepted schedules (mirror)")
    df = read_schedules_df(ui.data_dir)
    if df is None or df.empty:
        st.info("No schedules yet.")
        return

    # Reorder/rename a few user-friendly columns when present
    pretty = df.copy()
    if "when" in pretty:
        cols = ["when"] + [c for c in pretty.columns if c != "when"]
        pretty = pretty[cols]
    st.dataframe(pretty, use_container_width=True, hide_index=True)


__all__: Final[list[str]] = ["render_schedules"]
