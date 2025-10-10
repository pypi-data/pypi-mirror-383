"""Workers status component for the Streamlit UI of :mod:`yt_streams`.

Purpose:
    Infer and display per-worker status (phase, last heartbeat, recent
    refreshes, last error) from the append-only ledger (``runs.csv``). The
    controller should record the worker id (``wid``) and relevant fields.

Design:
    - No direct controller RPC; everything is derived from ledger rows.
    - We take the latest row per worker to show current phase/error, and a
      small recent window to count refreshes.

Public API:
    - :func:`render_workers`

Examples:
    Minimal integration::

        >>> # inside Streamlit app (doctest skipped)                 # doctest: +SKIP
        >>> from yt_streams.streamui.state import get_state          # doctest: +SKIP
        >>> from yt_streams.streamui.components.workers import render_workers  # doctest: +SKIP
        >>> ui = get_state()                                         # doctest: +SKIP
        >>> render_workers(ui)                                       # doctest: +SKIP
"""
from __future__ import annotations

from typing import Final

import pandas as pd  # type: ignore

from yt_streams.streamui.state import UiState, tail_ledger_df


def _latest_by_worker(df: pd.DataFrame) -> pd.DataFrame:
    if "wid" not in df.columns:
        return pd.DataFrame()
    if "when" not in df.columns and "ts" in df.columns:
        df = df.assign(when=pd.to_datetime(df["ts"].astype(float), unit="s"))
    return df.sort_values("when").drop_duplicates("wid", keep="last")


def render_workers(ui: UiState) -> None:
    """Render per-worker status cards derived from the ledger.

    Args:
        ui: The :class:`~yt_streams.streamui.state.UiState` for this session.

    Returns:
        ``None``. Renders Streamlit cards if data exists.

    Raises:
        RuntimeError: If Streamlit is not available at runtime.
    """
    try:
        import streamlit as st  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Streamlit is required to render workers") from exc

    st.subheader("Workers")
    df = tail_ledger_df(ui.data_dir, n=1000)
    if df is None or df.empty or "wid" not in df:
        st.info("No worker data yet.")
        return

    latest = _latest_by_worker(df)
    cols = st.columns(max(1, min(4, latest.shape[0])))
    for idx, row in enumerate(latest.itertuples(index=False)):
        with cols[idx % len(cols)]:
            st.metric("Worker", getattr(row, "wid", "?"))
            st.caption(f"Phase: {getattr(row, 'phase', '-')}")
            st.caption(f"Last: {getattr(row, 'when', '-')}")
            if "refreshes" in df.columns:
                last_window = df[df["wid"] == getattr(row, "wid")].tail(50)
                total_refreshes = last_window.get("refreshes").sum() if "refreshes" in last_window else None
                st.caption(f"Recent refreshes: {int(total_refreshes) if total_refreshes is not None else '-'}")
            err = getattr(row, "error", None)
            if isinstance(err, str) and err:
                st.error(err)


__all__: Final[list[str]] = ["render_workers"]
