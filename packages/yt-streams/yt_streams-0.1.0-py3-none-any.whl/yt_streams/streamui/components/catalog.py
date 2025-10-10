"""Catalog view component for the Streamlit UI of :mod:`yt_streams`.

Purpose:
    Render a **Catalog** tab backed by a CSV/JSONL file containing saved
    YouTube URLs with optional weights and active flags. The component can:

    - Display current items (url, weight, active, note).
    - Fire a **Pulse** for a selected URL into the control channel.
    - Optionally **edit** items (toggle `active`, update `weight`, add/remove)
      when catalog helpers are available (``yt_streams.airflow.catalog``).

Design:
    - Editing is **optional**: we conditionally import the catalog helpers.
    - All command writes go through :mod:`yt_streams.control` only.
    - State is passed explicitly via :class:`~yt_streams.streamui.state.UiState`.

Public API:
    - :func:`render_catalog`

Examples:
    Minimal integration::

        >>> # inside your Streamlit app                                 # doctest: +SKIP
        >>> from yt_streams.streamui.state import get_state             # doctest: +SKIP
        >>> from yt_streams.streamui.components.catalog import render_catalog  # doctest: +SKIP
        >>> ui = get_state()                                            # doctest: +SKIP
        >>> render_catalog(ui)                                          # doctest: +SKIP
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final
import os

try:  # optional helpers
    from yt_streams.airflow.catalog import (
        CatalogItem,
        load_catalog,
        save_catalog,
    )
except Exception:  # pragma: no cover - optional
    CatalogItem = None  # type: ignore[assignment]
    load_catalog = None  # type: ignore[assignment]
    save_catalog = None  # type: ignore[assignment]

import pandas as pd  # type: ignore

from yt_streams.control import ControlCommand, append_command
from yt_streams.streamui.state import UiState


def _pulse_url(ui: UiState, url: str, *, note: str) -> None:
    args: dict[str, Any] = {"play_seconds": (ui.play_seconds if not ui.randomize else max(ui.rand_min, 5))}
    # If randomize is on, we use rand_min as a quick bound (kept simple here);
    # Controls tab provides the full min/max randomization surface.
    if url:
        args["url"] = url
    append_command(ui.data_dir, ControlCommand(verb="pulse", args=args, note=note))


def render_catalog(ui: UiState) -> None:
    """Render the Catalog tab (view + optional edits + pulse).

    Args:
        ui: The :class:`~yt_streams.streamui.state.UiState` for this session.

    Returns:
        ``None``. Renders Streamlit widgets and writes control commands.

    Raises:
        RuntimeError: If Streamlit is not available at runtime.
    """
    try:
        import streamlit as st  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Streamlit is required to render catalog") from exc

    st.subheader("Catalog (CSV/JSONL)")
    default_path = os.environ.get("YT_STREAMS_CATALOG", "")
    path_text = st.text_input("Catalog path", value=default_path, key="catalog_path")
    if not path_text:
        st.info("Set a catalog path (CSV/JSONL) via the input or YT_STREAMS_CATALOG.")
        return

    if not load_catalog:
        st.warning("Catalog editing helpers not installed; display-only mode.")
        st.stop()

    items = load_catalog(path_text)
    if not items:
        st.info("Empty or missing catalog.")
        # Allow adding the first item if helpers exist
        with st.expander("Add first item"):
            new_url = st.text_input("URL", value="")
            new_weight = st.number_input("Weight", min_value=0.0, value=1.0, step=0.5, key="add_weight")
            new_active = st.checkbox("Active", value=True, key="add_active")
            new_note = st.text_input("Note", value="", key="add_note")
            if st.button("Add") and new_url:
                save_catalog(path_text, [CatalogItem(url=new_url, weight=float(new_weight), active=bool(new_active), note=(new_note or None))])
                st.success("Added.")
        return

    # Table view
    df = pd.DataFrame([
        {"url": it.url, "weight": it.weight, "active": it.active, "note": it.note or ""}
        for it in items
    ])
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()

    # Quick actions
    st.markdown("**Actions**")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        target = st.text_input("URL to pulse", value=(df[df["active"] == True]["url"].head(1).item() if (not df.empty and df["active"].any()) else ""))
        if st.button("Pulse URL") and target:
            _pulse_url(ui, target, note="ui:catalog")
            st.success(f"Appended pulse for {target}.")
    with col2:
        t_url = st.selectbox("Toggle active (pick URL)", options=list(df["url"]))
        new_state = st.selectbox("New state", options=["active", "inactive"], index=0)
        if st.button("Apply toggle"):
            # update in-memory then save
            for it in items:
                if it.url == t_url:
                    it.active = bool(new_state == "active")
                    break
            save_catalog(path_text, items)
            st.success("Saved.")
    with col3:
        w_url = st.selectbox("Set weight (pick URL)", options=list(df["url"]), key="weight_url")
        new_w = st.number_input("Weight", min_value=0.0, value=float(df.set_index("url").loc[w_url, "weight"]) if not df.empty else 1.0, step=0.5)
        if st.button("Apply weight"):
            for it in items:
                if it.url == w_url:
                    it.weight = float(new_w)
                    break
            save_catalog(path_text, items)
            st.success("Saved.")
    with col4:
        r_url = st.selectbox("Remove (pick URL)", options=list(df["url"]), key="remove_url")
        if st.button("Remove"):
            items = [it for it in items if it.url != r_url]
            save_catalog(path_text, items)
            st.success("Removed.")


__all__: Final[list[str]] = ["render_catalog"]
