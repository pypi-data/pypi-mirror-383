"""Textual dashboard for :mod:`yt_streams`.

Purpose:
    Provide a terminal UI (TUI) to observe and control a running pool of
    Playwright workers. The dashboard renders a live table of workers and a
    compact status header showing **requested**, **initialized**, **working**,
    and **errors** counts. Hotkeys trigger ad‑hoc play cycles and housekeeping.

Design:
    - Owns a :class:`~yt_streams.controller.PoolController` instance.
    - Periodically drains the controller's status queue and writes a durable
      append‑only ledger via :class:`~yt_streams.storage.Storage`.
    - Keeps only the latest state per worker in memory for rendering.

Key bindings:
    * ``p`` — broadcast a one‑off play cycle of ``settings.schedule.play_seconds``.
    * ``c`` — clear in‑memory error messages (cosmetic).
    * ``q`` — quit the dashboard (workers are asked to stop by the controller
      in the application's shutdown path).

Examples:
    Minimal run (heads‑up: launches browsers)::

        >>> from yt_streams.config import AppSettings  # doctest: +SKIP
        >>> from yt_streams.storage import Storage     # doctest: +SKIP
        >>> from yt_streams.tui import run_tui         # doctest: +SKIP
        >>> s = AppSettings(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ", workers=2)  # doctest: +SKIP
        >>> run_tui(s, Storage(root=s.storage.data_dir))  # doctest: +SKIP
"""
from __future__ import annotations

import time
from typing import Dict

from textual.app import App, ComposeResult
from textual.widgets import DataTable, Footer, Header, Static

from .config import AppSettings
from .controller import PoolController
from .models import Command, RunRecord, WorkerPhase, WorkerState
from .storage import Storage


class Dashboard(App):
    """Textual application that displays workers and basic controls.

    Args:
        settings: Resolved application settings controlling URL, workers, etc.
        store: Storage facade used to persist the run ledger.

    Raises:
        RuntimeError: If initialization fails before the UI loop starts.

    Examples:
        ::
            >>> from yt_streams.config import AppSettings  # doctest: +SKIP
            >>> from yt_streams.storage import Storage     # doctest: +SKIP
            >>> Dashboard(AppSettings(url="https://x", workers=1), Storage(root=Path("/tmp")))  # doctest: +SKIP
            <...Dashboard...>
    """

    CSS = "Screen {align: center middle;} #stats {padding: 1 2;}"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("p", "pulse", "Play Once"),
        ("c", "clear_errors", "Clear Errors"),
    ]

    def __init__(self, settings: AppSettings, store: Storage) -> None:
        super().__init__()
        self.settings = settings
        self.store = store
        self.pool = PoolController(
            url=settings.url,
            workers=settings.workers,
            browser=None,  # use PoolController defaults; could map from settings.browser
            timezone=self.settings.schedule.timezone,
        )
        self.table = DataTable(zebra_stripes=True)
        self.stats = Static(id="stats")
        self._state: Dict[int, WorkerState] = {}

    # --------------- Textual lifecycle ---------------
    def compose(self) -> ComposeResult:  # noqa: D401 - Textual compose contract
        yield Header(show_clock=True)
        yield self.stats
        yield self.table
        yield Footer()

    async def on_mount(self) -> None:
        """Start controller, set up table, and kick an initial play cycle."""
        self.table.add_columns("wid", "phase", "play_s", "refreshes", "last_error", "heartbeat")
        self.pool.start()
        # drain/render every 300ms
        self.set_interval(0.3, self._drain_status)
        self.set_interval(0.3, self._redraw)
        # initial action so users see activity without pressing keys
        self.pool.broadcast(Command(play_seconds=self.settings.schedule.play_seconds))

    async def on_unmount(self) -> None:  # pragma: no cover - UI tear‑down path
        """Best‑effort shutdown of the controller when the TUI closes."""
        try:
            self.pool.stop()
        except Exception:
            pass

    # --------------- Actions ---------------
    def action_pulse(self) -> None:
        """Broadcast a one‑off play cycle to all workers."""
        self.pool.broadcast(Command(play_seconds=self.settings.schedule.play_seconds))

    def action_clear_errors(self) -> None:
        """Clear in‑memory error messages (cosmetic only)."""
        for st in self._state.values():
            st.last_error = None

    # --------------- Internal helpers ---------------
    def _drain_status(self) -> None:
        """Drain worker telemetry, fold into UI state, and append ledger rows."""
        rows: list[RunRecord] = []
        drained = self.pool.drain_status()
        for st in drained:
            prev = self._state.get(st.wid)
            if prev and st.refreshes:
                st.refreshes = prev.refreshes + st.refreshes
            self._state[st.wid] = st
            rows.append(
                RunRecord(
                    ts=time.time(),
                    wid=st.wid,
                    phase=st.phase.value if isinstance(st.phase, WorkerPhase) else str(st.phase),
                    play_seconds=st.play_seconds,
                    refreshes=st.refreshes,
                    error=st.last_error,
                )
            )
        if rows:
            self.store.ensure()
            self.store.append_runs(rows)

    def _redraw(self) -> None:
        """Recompute header counters and refresh the table contents."""
        phases = [s.phase for s in self._state.values()]
        initialized = sum(1 for p in phases if p in {WorkerPhase.initialized, WorkerPhase.working})
        working = sum(1 for p in phases if p == WorkerPhase.working)
        errors = sum(1 for p in phases if p == WorkerPhase.error)
        self.stats.update(
            f"requested: {self.settings.workers} | initialized: {initialized} | "
            f"working: {working} | errors: {errors}"
        )
        self.table.clear()
        for wid in range(self.settings.workers):
            s = self._state.get(wid, WorkerState(wid=wid))
            self.table.add_row(
                str(wid),
                s.phase.value if isinstance(s.phase, WorkerPhase) else str(s.phase),
                str(s.play_seconds),
                str(s.refreshes),
                s.last_error or "",
                f"{s.heartbeat_ts:.1f}",
            )


def run_tui(settings: AppSettings, store: Storage) -> None:
    """Run the Textual dashboard application.

    Args:
        settings: Application settings.
        store: Storage facade for persisting the run ledger.

    Returns:
        ``None``. This function blocks until the UI is closed.

    Examples:
        ::
            >>> from yt_streams.config import AppSettings  # doctest: +SKIP
            >>> from yt_streams.storage import Storage     # doctest: +SKIP
            >>> run_tui(AppSettings(url="https://x", workers=1), Storage(root=Path("/tmp")))  # doctest: +SKIP
    """
    Dashboard(settings, store).run()
