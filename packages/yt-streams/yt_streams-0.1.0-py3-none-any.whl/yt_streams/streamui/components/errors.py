"""Errors component for the Streamlit UI of :mod:`yt_streams`.

Purpose:
    Surface recent errors from the ledger (``runs.csv``) to aid debugging.
    Shows a table of rows where ``error`` is present, with quick grouping by
    error message.

Public API:
    - :func:`render_errors`
"""
from __future__ import annotations

from typing import Final

import pandas as pd  # type: ignore

from yt_streams.streamui.state import UiState, tail_ledger_df


def render_errors(ui: UiState) -> None:
    """Render recent error rows and aggregates.

    Args:
        ui: The :class:`~yt_streams.streamui.state.UiState` for this session.

    Returns:
        ``None``. Renders Streamlit widgets and tables.

    Raises:
        RuntimeError: If Streamlit is not available at runtime.
    """
    try:
        import streamlit as st  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Streamlit is required to render errors") from exc

    st.subheader("Errors")
    df = tail_ledger_df(ui.data_dir, n=1000)
    if df is None or df.empty or "error" not in df:
        st.info("No errors recorded.")
        return

    errs = df[df["error"].notna() & (df["error"] != "")]
    if errs.empty:
        st.info("No errors recorded.")
        return

    st.dataframe(errs.tail(200), use_container_width=True, hide_index=True)

    try:
        g = errs.groupby("error", dropna=False).size().sort_values(ascending=False).head(20)
        st.bar_chart(g)
    except Exception:
        pass


__all__: Final[list[str]] = ["render_errors"]
