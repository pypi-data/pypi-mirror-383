"""Streamlit dashboard for :mod:`yt_streams`.

Purpose:
    Provide an interactive control & observability UI on top of the
    file-based artifacts used by ``yt_streams``:
    - Append **pulses** and **schedules** to the control channel.
    - Inspect **workers**, **schedules**, and **ledger**.
    - Manage a lightweight **catalog** of URLs.
    - Persist a default URL in ``ui_prefs.json`` (under the chosen data dir).

Design:
    The app composes small, testable pieces:
      - :mod:`yt_streams.streamui.state` supplies a typed state object,
        cached readers, and action helpers.
      - Components under :mod:`yt_streams.streamui.components` render each tab:
        * controls      – enqueue pulses/schedules
        * workers       – live worker metrics from the ledger tail
        * schedules_viz – schedules mirror (JSONL)
        * ledger        – ledger browsing & export affordances
        * catalog       – simple URL catalog view/manage

    Importantly, the UI **never** talks to the controller directly; it writes
    to the **append-only** control file (``commands.jsonl``) and reads from
    **append-only** mirrors (``runs.csv``, ``schedules.jsonl``). This keeps the
    system robust and easy to operate locally or under schedulers (Airflow/cron).

Environment:
    - ``YT_STREAMS_DATA_DIR`` (optional): default data dir for artifacts.
    - ``YT_STREAMS_DEFAULT_URL`` (optional): default URL precedence over prefs.
    - ``YT_STREAMS_CATALOG`` (optional): explicit path to catalog CSV/JSONL.

Examples:
    Run via the consolidated CLI (recommended)::

        $ pdm run yt-streams serve-streamlit \
            --workers 4 --data_dir ./data/yt_streams

    Or run Streamlit directly (ensure controller+broker running separately)::

        $ export YT_STREAMS_DATA_DIR=./data/yt_streams
        $ streamlit run src/yt_streams/streamui/app.py

Notes:
    *Compliance*: Use only for testing your own content; automated viewing
    intended to manipulate counters may violate YouTube ToS.
"""
from __future__ import annotations

__all__ = ["main"]

from pathlib import Path
from typing import Final

# Streamlit import here so the module is importable even if not installed elsewhere
import streamlit as st  # type: ignore

from yt_streams.streamui.state import (
    UiState,
    append_pulse,
    get_state,
    infer_worker_count_from_ledger,
    read_catalog,
    read_schedules_jsonl,
    set_default_url,
    tail_ledger_df,
)

# Components (each must expose a render_* function)
from yt_streams.streamui.components.controls import render_controls
from yt_streams.streamui.components.workers import render_workers
from yt_streams.streamui.components.schedules_viz import render_schedules
from yt_streams.streamui.components.ledger import render_ledger
from yt_streams.streamui.components.catalog import render_catalog


_APP_TITLE: Final[str] = "yt_streams — Dashboard"
_HELP_LINKS: Final[dict[str, str]] = {
    "README": "https://github.com/your-org/yt_streams#readme",
}


# ------------------------------- Sidebar helpers -------------------------------

def _sidebar_prefs(ui: UiState) -> None:
    """Render global controls & sticky preferences in the sidebar.

    Args:
        ui: App state (data_dir, default_url, prefs).

    Returns:
        ``None`` (Streamlit rendering).
    """
    st.sidebar.header("Preferences & Quick Actions")
    st.sidebar.caption(f"Data dir: `{ui.data_dir}`")

    # Default URL editor
    with st.sidebar.expander("Default URL", expanded=True):
        current = ui.default_url or ""
        new_url = st.text_input(
            "Default YouTube URL",
            value=current,
            placeholder="https://www.youtube.com/watch?v=...",
            help="Used if a pulse/schedule does not specify a URL explicitly.",
            key="default_url_input",
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Save default URL", use_container_width=True):
                set_default_url(ui, new_url.strip() or None)
                st.success("Default URL saved.")
                st.rerun()
        with col2:
            if st.button("Clear default URL", use_container_width=True):
                set_default_url(ui, None)
                st.info("Default URL cleared (env/catalog may still provide a default).")
                st.rerun()

    # Quick Pulse
    with st.sidebar.expander("Quick Pulse", expanded=True):
        fixed = st.toggle("Use fixed play window", value=True, help="Off = random range below.")
        if fixed:
            play_seconds = st.slider("Play seconds", min_value=5, max_value=600, value=60, step=5)
            play_min = play_max = None
        else:
            play_seconds = None
            play_min, play_max = st.slider(
                "Random play range (seconds)",
                min_value=5,
                max_value=600,
                value=(45, 90),
                step=5,
            )
        url_override = st.text_input("Pulse URL (optional)", value="", help="Overrides default URL for this pulse only.")
        if st.button("Send Pulse", type="primary", use_container_width=True):
            append_pulse(
                ui,
                play_seconds=play_seconds,
                play_min=play_min,
                play_max=play_max,
                url=(url_override.strip() or None),
                note="ui:quick_pulse",
            )
            st.success("Pulse appended. Controller will pick it up shortly.")

    with st.sidebar.expander("Insight", expanded=False):
        w = infer_worker_count_from_ledger(ui)
        st.caption(f"Inferred workers (recent): **{w if w is not None else 'n/a'}**")

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "The UI writes to **commands.jsonl** and reads **runs.csv** / **schedules.jsonl**. "
        "Make sure the controller is running."
    )


# --------------------------------- Main layout ---------------------------------

def _header(ui: UiState) -> None:
    st.title(_APP_TITLE)
    default_url_msg = ui.default_url or "—"
    st.caption(f"Default URL: `{default_url_msg}`")
    st.markdown(
        """
        This dashboard controls a running **yt_streams** controller via a file-based
        control channel. Use the **Controls** tab to enqueue actions; inspect live
        status under **Workers** and **Ledger**.
        """
    )


def _tabs(ui: UiState) -> None:
    tab_labels = ["Controls", "Workers", "Schedules", "Ledger", "Catalog", "About"]
    t_controls, t_workers, t_schedules, t_ledger, t_catalog, t_about = st.tabs(tab_labels)

    with t_controls:
        render_controls(data_dir=ui.data_dir, default_url=ui.default_url)

    with t_workers:
        render_workers(ui)

    with t_schedules:
        render_schedules(ui)

    with t_ledger:
        render_ledger(ui)

    with t_catalog:
        render_catalog(ui)

    with t_about:
        st.subheader("About")
        st.write(
            """
            **yt_streams** launches multiple isolated Chromium sessions (Playwright)
            that perform play → wait → refresh cycles, optionally under interval/cron
            schedules. This UI is intentionally simple and robust: no sockets, no RPCs,
            just append-only files.
            """
        )
        st.write("Helpful links:")
        for label, url in _HELP_LINKS.items():
            st.markdown(f"- [{label}]({url})")


# ------------------------------------ Main ------------------------------------

def main() -> None:
    """Entrypoint for the Streamlit app.

    Returns:
        ``None`` (Streamlit renders to the page).
    """
    # Discover state from env/prefs/catalog; persist the resolved default once.
    ui = get_state(persist_defaults=True)

    # Page config (safe to call once per run)
    st.set_page_config(
        page_title="yt_streams",
        page_icon="▶️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    _sidebar_prefs(ui)
    _header(ui)
    _tabs(ui)


if __name__ == "__main__":
    main()
