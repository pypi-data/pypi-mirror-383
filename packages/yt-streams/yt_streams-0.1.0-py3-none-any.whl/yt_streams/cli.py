# ruff: noqa: D205,D400,D401
"""Typer CLI for :mod:`yt_streams`.

Purpose:
    Provide a consolidated, ergonomic command-line interface for operating
    :mod:`yt_streams`. The CLI focuses on a *control-plane* API: starting the
    controller and broker, launching optional UIs (Streamlit or Textual),
    appending one-off pulses, and registering interval/cron schedules via a
    simple **file-based control channel** (JSONL).

Design:
    - Pure control-plane: the CLI never touches browsers directly. It starts
      the :class:`~yt_streams.controller.PoolController` and the
      :class:`~yt_streams.control.ControlBroker` and writes commands to the
      ``commands.jsonl`` file. Observability comes from append-only artifacts
      (``runs.csv``, ``schedules.jsonl``) and UI dashboards.
    - Streamlit and Textual are optional; when not installed, the CLI degrades
      gracefully with actionable messages.
    - URL is **optional**: a default is resolved from *flag → env →
      catalog*. When none is found, the controller still starts; pulses must
      then include a per-pulse URL (supported by the Streamlit “Controls” tab
      and the `pulse` command).

Artifacts:
    - Control channel (append-only JSONL): ``commands.jsonl``
    - Ledger of run events (append-only CSV): ``runs.csv``
    - Schedule mirror for UIs (append-only JSONL): ``schedules.jsonl``
    - Optional catalog for defaults: ``catalog.csv`` or ``catalog.jsonl``

Environment:
    - ``YT_STREAMS_DEFAULT_URL`` — fallback default URL if `--url` is omitted.
    - ``YT_STREAMS_CATALOG``     — path to a catalog (.csv | .jsonl).
    - ``YT_STREAMS_DATA_DIR``    — data directory used by UIs (auto-set by CLI).

Public Commands:
    serve
        Start controller + broker in the foreground.
    serve-streamlit
        Start controller + broker and launch the Streamlit dashboard.
    tui
        Launch the Textual TUI pointing at a data directory.
    pulse
        Append a one-off pulse (fixed or randomized play window).
    schedule interval
        Append an interval schedule command (e.g., every 8 minutes).
    schedule cron
        Append a cron schedule command (e.g., ``*/13 9-21 * * 1-5``).
    schedule list / schedule ctl
        List mirrored schedules and send pause/resume/remove controls.
    export parquet
        Export ``runs.csv`` to Parquet if pandas/pyarrow are available.
    catalog [list|add|toggle|weight|remove]
        Manage a simple URL catalog (CSV/JSONL).
    status
        Quick, human-readable snapshot (exists, sizes, last ledger rows).
    tail
        Tail the ledger in the console (last N rows).
    doctor
        Environment checks (Python, Playwright install, Streamlit import).
    env
        Print effective environment (URL resolution, paths).

Examples:
    Minimal start with Streamlit::

        $ pdm run yt-streams serve-streamlit \
            --workers 3 --play_seconds 60 --data_dir ./data/yt_streams

    Use environment or catalog instead of ``--url``::

        $ export YT_STREAMS_DEFAULT_URL="https://youtu.be/9SYh2Iyhf4k"
        $ # or create ./data/yt_streams/catalog.csv with url,weight,active
        $ pdm run yt-streams serve-streamlit --workers 3 --data_dir ./data/yt_streams

    Append an interval schedule and list schedules::

        $ pdm run yt-streams schedule interval 08:00 \
            --data_dir ./data/yt_streams --play_min 45 --play_max 90
        $ pdm run yt-streams schedule list --data_dir ./data/yt_streams

Notes:
    *Compliance*: Use for testing your own content; automated viewing intended
    to manipulate counters may violate YouTube ToS.

    *Purity & side effects*: The CLI is intentionally thin and side-effect free
    unless you invoke a command. File writes are append-only. The controller
    may lazily spin up browsers; shutdown is ordered to avoid Playwright pipe
    errors (stop broker → stop controller).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Final, Iterable

import contextlib
import importlib
import inspect
import json
import os
import signal
import subprocess
import sys
import time

import typer

from .config import AppSettings
from .control import ControlBroker, ControlCommand, append_command
from .controller import PoolController
from .storage import Storage

# Optional catalog helpers (kept pure, safe to import)
try:  # pragma: no cover - optional dependency at runtime
    from .airflow.catalog import CatalogItem, load_catalog, save_catalog  # type: ignore
except Exception:  # pragma: no cover - optional
    CatalogItem = None  # type: ignore[assignment]
    load_catalog = None  # type: ignore[assignment]
    save_catalog = None  # type: ignore[assignment]

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help="yt_streams CLI — control-plane entrypoints for controller, UIs, and schedules",
)

# --------------------------------------------------------------------------- #
# URL resolution helpers
# --------------------------------------------------------------------------- #


def _maybe_url_from_env(url: str | None) -> str | None:
    """Return a URL from explicit flag or environment, if any.

    Args:
        url: URL provided by CLI flag.

    Returns:
        Resolved URL or ``None`` if not available.

    Examples:
        ::
            >>> _maybe_url_from_env(None) in (None, str())  # doctest: +ELLIPSIS
            True
    """
    if url:
        return url
    env = os.environ.get("YT_STREAMS_DEFAULT_URL", "").strip()
    return env or None


def _fallback_url_from_catalog(data_dir: Path) -> str | None:
    """Pick a default URL from a nearby catalog (env or sibling files).

    Resolution order:
        1) ``$YT_STREAMS_CATALOG``
        2) ``<data_dir>/catalog.csv``
        3) ``<data_dir>/catalog.jsonl``

    Args:
        data_dir: Data directory to probe for catalog files.

    Returns:
        The first *active* URL with the highest weight, or ``None`` if no
        catalog is present or helpers are unavailable.
    """
    try:
        path = os.environ.get("YT_STREAMS_CATALOG", "")
        if not path:
            for name in ("catalog.csv", "catalog.jsonl"):
                p = data_dir / name
                if p.exists():
                    path = str(p)
                    break
        if not path or not (load_catalog and CatalogItem):
            return None
        items = load_catalog(Path(path))  # type: ignore[arg-type]
        active = [it for it in items if getattr(it, "active", True)]
        if not active:
            return None
        pick = max(active, key=lambda it: getattr(it, "weight", 1.0))
        return pick.url or None
    except Exception:
        return None


def _resolve_default_url(url: str | None, data_dir: Path) -> str | None:
    """Resolve a default URL if possible, else ``None`` (UI will require per-pulse)."""
    return _maybe_url_from_env(url) or _fallback_url_from_catalog(data_dir)


# --------------------------------------------------------------------------- #
# Controller context — safe start/stop of controller + broker
# --------------------------------------------------------------------------- #


@dataclass(slots=True)
class _Running:
    """Holds running handles.

    Attributes:
        ctl: Running controller.
        broker: Running file-based control broker.
    """

    ctl: PoolController
    broker: ControlBroker


class _ControllerCtx:
    """Context manager to start/stop controller + broker safely.

    The context is **signature-safe**: it inspects
    :class:`~yt_streams.controller.PoolController` to detect optional keyword
    parameters (e.g., ``headless``, ``default_play_seconds``) at runtime and
    only passes supported options. This makes the CLI forward/backward
    compatible with evolutions of the controller signature.

    Args:
        url: Default YouTube watch URL (``None`` → empty string).
        workers: Number of worker threads.
        data_dir: Data directory used by storage/broker/UI.
        timezone: Controller scheduler timezone.
        headless: Headless Chromium flag (if supported by controller).
        default_play_seconds: Default play window for UI pulses (bound at
            registration time via the broker).

    Examples:
        ::
            >>> # ctx = _ControllerCtx(url=None, workers=2, data_dir=Path("data/yt_streams"))  # doctest: +SKIP
            >>> # with ctx as running: ...  # doctest: +SKIP
    """

    def __init__(
        self,
        *,
        url: str | None,
        workers: int,
        data_dir: Path,
        timezone: str = "UTC",
        headless: bool = False,
        default_play_seconds: int | None = None,
    ) -> None:
        self.url = url or ""
        self.workers = int(workers)
        self.data_dir = data_dir
        self.timezone = timezone
        self.headless = bool(headless)
        self.default_play_seconds = default_play_seconds
        self._running: _Running | None = None

    def __enter__(self) -> _Running:
        """Start controller and broker; return running handles.

        Returns:
            _Running: Handles to ``ctl`` and ``broker``.
        """
        # Ensure data dir exists before starting services
        Storage(root=self.data_dir).ensure()

        # Build kwargs compatibly with whichever controller is installed
        ctl_kwargs: dict[str, object] = {
            "url": self.url,
            "workers": self.workers,
            "timezone": self.timezone,
        }
        sig = inspect.signature(PoolController)
        if "headless" in sig.parameters:
            ctl_kwargs["headless"] = self.headless
        if "default_play_seconds" in sig.parameters and self.default_play_seconds is not None:
            ctl_kwargs["default_play_seconds"] = self.default_play_seconds

        # Start controller
        ctl = PoolController(**ctl_kwargs)
        ctl.start()

        # Start broker
        broker = ControlBroker(root=self.data_dir, controller=ctl, poll_seconds=0.5)
        broker.start()

        self._running = _Running(ctl=ctl, broker=broker)
        return self._running

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: D401
        """Stop broker, then controller, in order."""
        if self._running is None:
            return
        try:
            self._running.broker.stop()
        finally:
            self._running.ctl.stop()


# --------------------------------------------------------------------------- #
# Serve commands
# --------------------------------------------------------------------------- #


@app.command("serve")
def serve(
    url: str | None = typer.Option(
        None, help="Default video URL (optional; env/catalog fallback)."
    ),
    workers: int = typer.Option(3, min=1, help="Number of worker threads."),
    data_dir: Path = typer.Option(Path("data/yt_streams"), help="Data directory."),
    headless: bool = typer.Option(False, help="Chromium headless."),
    play_seconds: int = typer.Option(60, min=5, help="Default play seconds when pulsed."),
    timezone: str = typer.Option("UTC", help="Controller timezone for APScheduler."),
    stealth: bool = typer.Option(True, help="Enable stealth mode to avoid bot detection."),
    proxy: str | None = typer.Option(None, help="Proxy URL (e.g., http://user:pass@host:port)."),
    proxy_chain: str | None = typer.Option(None, help="Comma-separated proxy chain URLs."),
) -> None:
    """Start the controller and file-based broker in the foreground.

    If no default URL can be resolved, the controller still starts; **pulses
    must include a URL** (the Streamlit “Controls” tab and `pulse` command
    both support per-pulse URLs).
    """
    resolved = _resolve_default_url(url, data_dir)
    s = AppSettings(url=(resolved or ""), workers=workers)
    with _ControllerCtx(
        url=s.url,
        workers=s.workers,
        data_dir=data_dir,
        timezone=timezone,
        headless=headless,
        default_play_seconds=play_seconds,
    ):
        typer.echo("yt_streams controller running. Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1.0)
        except KeyboardInterrupt:
            pass


@app.command("serve-streamlit")
def serve_streamlit(
    url: str | None = typer.Option(
        None, help="Default video URL (optional; env/catalog fallback)."
    ),
    workers: int = typer.Option(3, min=1, help="Number of worker threads."),
    data_dir: Path = typer.Option(Path("data/yt_streams"), help="Data directory."),
    play_seconds: int = typer.Option(60, min=5, help="Default play seconds."),
    headless: bool = typer.Option(False, help="Chromium headless."),
    open_browser: bool = typer.Option(True, help="Open the Streamlit page."),
    stealth: bool = typer.Option(True, help="Enable stealth mode to avoid bot detection."),
    proxy: str | None = typer.Option(None, help="Proxy URL (e.g., http://user:pass@host:port)."),
    proxy_chain: str | None = typer.Option(None, help="Comma-separated proxy chain URLs."),
) -> None:
    """Start controller + broker + Streamlit dashboard.

    If no default URL is found (flag/env/catalog), the UI launches anyway and
    you can provide a URL per pulse in **Controls**.
    """
    resolved = _resolve_default_url(url, data_dir)
    s = AppSettings(url=(resolved or ""), workers=workers)
    with _ControllerCtx(
        url=s.url,
        workers=s.workers,
        data_dir=data_dir,
        timezone="UTC",
        headless=headless,
        default_play_seconds=play_seconds,
    ):
        import importlib
        import inspect

        # Find the actual file path of the app module
        try:
            mod = importlib.import_module("yt_streams.streamui.app")
        except Exception as exc:
            typer.echo(f"Could not import Streamlit app module: {exc}")
            raise typer.Exit(code=2)

        app_path = inspect.getsourcefile(mod)
        if not app_path:
            typer.echo("Could not locate Streamlit app module file path.")
            raise typer.Exit(code=2)

        env = dict(os.environ)
        env.setdefault("YT_STREAMS_DATA_DIR", str(data_dir))

        # NOTE: No '-m' after 'run'. We pass a FILE PATH.
        cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            app_path,
            "--server.headless=true" if headless else "--server.headless=false",
        ]

        proc = subprocess.Popen(cmd, env=env)

        if open_browser:
            with contextlib.suppress(Exception):
                import webbrowser
                webbrowser.open("http://localhost:8501")

        # Relay SIGINT/SIGTERM so Streamlit shuts down cleanly
        def _relay(sig, _frame):
            with contextlib.suppress(Exception):
                proc.send_signal(sig)
        signal.signal(signal.SIGINT, _relay)
        signal.signal(signal.SIGTERM, _relay)

        proc.wait()


# --------------------------------------------------------------------------- #
# Append & schedule commands
# --------------------------------------------------------------------------- #

@app.command("pulse")
def pulse(
    data_dir: Path = typer.Option(Path("data/yt_streams"), help="Control directory."),
    play_seconds: int | None = typer.Option(None, min=5, help="Fixed play window."),
    play_min: int = typer.Option(45, min=5, help="Random min if not fixed."),
    play_max: int = typer.Option(90, min=5, help="Random max if not fixed."),
    url: str | None = typer.Option(None, help="URL override for this pulse (required if no default)."),
    note: str = typer.Option("cli:pulse", help="Annotation."),
) -> None:
    """Append a one-off pulse to the control file.

    Precedence for play window:
        1) ``--play-seconds`` if provided
        2) random in ``[--play-min, --play-max]``
    """
    args: dict[str, object] = {}
    if play_seconds is not None:
        args["play_seconds"] = int(play_seconds)
    else:
        lo, hi = sorted((int(play_min), int(play_max)))
        import random

        args["play_seconds"] = int(random.randint(lo, hi))
    if url:
        args["url"] = url
    append_command(data_dir, ControlCommand(verb="pulse", args=args, note=note))
    typer.echo(f"appended pulse → {data_dir}")


schedule_app = typer.Typer(help="Append and control schedules.")
app.add_typer(schedule_app, name="schedule")


@schedule_app.command("interval")
def schedule_interval(
    text: str = typer.Argument(..., help="HH:MM:SS | MM:SS | SS"),
    data_dir: Path = typer.Option(Path("data/yt_streams"), help="Control directory."),
    play_seconds: int | None = typer.Option(None, min=5, help="Fixed play window."),
    play_min: int = typer.Option(45, min=5, help="Random min if not fixed."),
    play_max: int = typer.Option(90, min=5, help="Random max if not fixed."),
    note: str = typer.Option("cli:interval", help="Annotation."),
) -> None:
    """Append an interval schedule command."""
    args: dict[str, object] = {"text": text}
    if play_seconds is not None:
        args["play_seconds"] = int(play_seconds)
    else:
        lo, hi = sorted((int(play_min), int(play_max)))
        import random

        args["play_seconds"] = int(random.randint(lo, hi))
    append_command(data_dir, ControlCommand(verb="interval", args=args, note=note))
    typer.echo(f"scheduled interval {text} → {data_dir}")


@schedule_app.command("cron")
def schedule_cron(
    expr: str = typer.Argument(..., help="5-field cron expression."),
    data_dir: Path = typer.Option(Path("data/yt_streams"), help="Control directory."),
    play_seconds: int | None = typer.Option(None, min=5, help="Fixed play window."),
    play_min: int = typer.Option(45, min=5, help="Random min if not fixed."),
    play_max: int = typer.Option(90, min=5, help="Random max if not fixed."),
    note: str = typer.Option("cli:cron", help="Annotation."),
) -> None:
    """Append a cron schedule command."""
    args: dict[str, object] = {"expr": expr}
    if play_seconds is not None:
        args["play_seconds"] = int(play_seconds)
    else:
        lo, hi = sorted((int(play_min), int(play_max)))
        import random

        args["play_seconds"] = int(random.randint(lo, hi))
    append_command(data_dir, ControlCommand(verb="cron", args=args, note=note))
    typer.echo(f"scheduled cron '{expr}' → {data_dir}")


@schedule_app.command("list")
def schedule_list(
    data_dir: Path = typer.Option(Path("data/yt_streams"), help="Data directory."),
) -> None:
    """List known schedules from the mirror (folded by latest job_id)."""
    mirror = data_dir / "schedules.jsonl"
    if not mirror.exists():
        typer.echo("no schedules")
        raise typer.Exit()
    latest: dict[str, dict] = {}
    with mirror.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue
            try:
                obj = json.loads(s)
            except Exception:
                continue
            jid = str(obj.get("job_id", ""))
            if jid:
                latest[jid] = obj
    if not latest:
        typer.echo("no schedules")
        return
    for jid, r in sorted(latest.items()):
        kind = r.get("kind", "?")
        nrt = r.get("next_run_ts")
        when = "-" if nrt is None else datetime.fromtimestamp(float(nrt))
        note = r.get("note", "")
        typer.echo(f"{jid:28} {kind:<8} next={when} note={note}")


@schedule_app.command("ctl")
def schedule_ctl(
    op: str = typer.Argument(..., help="pause|resume|remove"),
    job_id: str = typer.Argument(..., help="Job id to control."),
    data_dir: Path = typer.Option(Path("data/yt_streams"), help="Control directory."),
) -> None:
    """Control an existing schedule via the control channel."""
    if op not in {"pause", "resume", "remove"}:
        raise typer.BadParameter("op must be one of: pause, resume, remove")
    cmd = ControlCommand(verb="schedule_ctl", args={"op": op, "job_id": job_id}, note="cli:schedule_ctl")
    append_command(data_dir, cmd)
    typer.echo(f"{op} {job_id}")


# --------------------------------------------------------------------------- #
# Export
# --------------------------------------------------------------------------- #

export_app = typer.Typer(help="Export artifacts.")
app.add_typer(export_app, name="export")


@export_app.command("parquet")
def export_parquet(
    data_dir: Path = typer.Option(Path("data/yt_streams"), help="Data directory."),
) -> None:
    """Export ``runs.csv`` to Parquet if dependencies are present."""
    out = Storage(root=data_dir).export_parquet()
    if out:
        typer.echo(str(out))
    else:
        typer.echo("no parquet exported (missing deps or empty ledger)")


# --------------------------------------------------------------------------- #
# Catalog mgmt (optional)
# --------------------------------------------------------------------------- #

catalog_app = typer.Typer(help="Manage URL catalog (CSV/JSONL).")
app.add_typer(catalog_app, name="catalog")


@catalog_app.command("list")
def catalog_list(path: Path = typer.Argument(..., help="catalog .csv or .jsonl")) -> None:
    """List items in a catalog file."""
    if not load_catalog:
        raise typer.Exit(code=2)
    items = load_catalog(path)
    for i, it in enumerate(items, 1):
        typer.echo(f"{i:>3} active={int(it.active)} weight={it.weight:g} url={it.url} note={it.note or ''}")


@catalog_app.command("add")
def catalog_add(
    path: Path = typer.Argument(...),
    url: str = typer.Option(...),
    weight: float = typer.Option(1.0),
    active: bool = typer.Option(True),
    note: str | None = typer.Option(None),
) -> None:
    """Add a new catalog row."""
    if not (CatalogItem and load_catalog and save_catalog):
        raise typer.Exit(code=2)
    items = load_catalog(path)
    items.append(CatalogItem(url=url, weight=max(0.0, float(weight)), active=bool(active), note=note))
    save_catalog(path, items)
    typer.echo("added")


@catalog_app.command("toggle")
def catalog_toggle(
    path: Path = typer.Argument(...),
    url: str = typer.Option(..., help="Exact URL to toggle"),
    active: bool = typer.Option(..., help="New active state"),
) -> None:
    """Toggle an item's active flag."""
    if not (load_catalog and save_catalog):
        raise typer.Exit(code=2)
    items = load_catalog(path)
    changed = False
    for it in items:
        if it.url == url:
            it.active = bool(active)
            changed = True
            break
    if changed:
        save_catalog(path, items)
        typer.echo("toggled")
    else:
        typer.echo("not found")


@catalog_app.command("weight")
def catalog_weight(
    path: Path = typer.Argument(...),
    url: str = typer.Option(...),
    weight: float = typer.Option(...),
) -> None:
    """Update an item's weight."""
    if not (load_catalog and save_catalog):
        raise typer.Exit(code=2)
    items = load_catalog(path)
    changed = False
    for it in items:
        if it.url == url:
            it.weight = max(0.0, float(weight))
            changed = True
            break
    if changed:
        save_catalog(path, items)
        typer.echo("weighted")
    else:
        typer.echo("not found")


@catalog_app.command("remove")
def catalog_remove(
    path: Path = typer.Argument(...),
    url: str = typer.Option(...),
) -> None:
    """Remove an entry from the catalog."""
    if not (load_catalog and save_catalog):
        raise typer.Exit(code=2)
    items = load_catalog(path)
    before = len(items)
    items = [it for it in items if it.url != url]
    save_catalog(path, items)
    typer.echo(f"removed {before - len(items)}")


# --------------------------------------------------------------------------- #
# Utility commands — status, tail, doctor, env
# --------------------------------------------------------------------------- #

@app.command("status")
def status(
    data_dir: Path = typer.Option(Path("data/yt_streams"), help="Data directory."),
    tail: int = typer.Option(5, min=0, help="Show last N ledger rows (0 to skip)."),
) -> None:
    """Print a quick status summary for the data directory."""
    store = Storage(root=data_dir)
    ledger = store.ledger_path
    meta = store.meta_path
    schedules = data_dir / "schedules.jsonl"

    def _size(p: Path) -> str:
        return f"{p.stat().st_size} B" if p.exists() else "-"

    typer.echo(f"data_dir:    {data_dir}")
    typer.echo(f"runs.csv:    {ledger.exists()} ({_size(ledger)})")
    typer.echo(f"meta.jsonl:  {meta.exists()} ({_size(meta)})")
    typer.echo(f"schedules:   {schedules.exists()} ({_size(schedules)})")

    if tail > 0 and ledger.exists():
        rows = store.tail_ledger(tail)
        if rows:
            typer.echo("\nlast rows:")
            for r in rows[-tail:]:
                typer.echo(
                    f"  ts={r.get('ts','?')} wid={r.get('wid','?')} phase={r.get('phase','?')}"
                    f" play={r.get('play_seconds','?')} refresh={r.get('refreshes','?')}"
                    f" err={r.get('error','')}"
                )


@app.command("tail")
def tail(
    data_dir: Path = typer.Option(Path("data/yt_streams"), help="Data directory."),
    n: int = typer.Option(20, min=1, help="Number of ledger rows."),
) -> None:
    """Tail the ledger (CSV) and print last N rows."""
    store = Storage(root=data_dir)
    rows = store.tail_ledger(n)
    if not rows:
        typer.echo("no rows")
        return

    def _fmt(r: dict[str, str]) -> str:
        return (
            f"{r.get('ts','?'):>13} wid={r.get('wid','?'):>3} "
            f"{r.get('phase','?'):<10} play={r.get('play_seconds','?'):>3} "
            f"ref={r.get('refreshes','?'):>2} err={r.get('error','')}"
        )

    for r in rows[-n:]:
        typer.echo(_fmt(r))


@app.command("doctor")
def doctor() -> None:
    """Run environment checks and print a short report."""
    ok = True

    def _check(desc: str, fn) -> None:
        nonlocal ok
        try:
            fn()
            typer.echo(f"[ OK ] {desc}")
        except Exception as e:  # pragma: no cover - env specific
            ok = False
            typer.echo(f"[FAIL] {desc}: {e}")

    _check("python -m playwright import", lambda: importlib.import_module("playwright"))
    _check("streamlit import", lambda: importlib.import_module("streamlit"))
    _check("pandas import (optional)", lambda: importlib.import_module("pandas"))

    # Browser availability is environment-specific; best-effort call
    def _playwright_browsers():
        from playwright.sync_api import sync_playwright  # type: ignore

        with sync_playwright() as p:
            # don’t actually launch; just list channels
            _ = [b for b in (p.chromium, p.firefox, p.webkit)]
    _check("playwright browsers (probe)", _playwright_browsers)

    if not ok:
        typer.echo("\nSome checks failed. Try:")
        typer.echo("  pdm run playwright install chromium")
        typer.echo("  pdm run streamlit --version")


@app.command("env")
def env(
    url: str | None = typer.Option(None, help="Candidate URL."),
    data_dir: Path = typer.Option(Path("data/yt_streams"), help="Data directory."),
) -> None:
    """Show effective environment (URL resolution, paths)."""
    typer.echo(f"YT_STREAMS_DEFAULT_URL={os.environ.get('YT_STREAMS_DEFAULT_URL','')!r}")
    typer.echo(f"YT_STREAMS_CATALOG={os.environ.get('YT_STREAMS_CATALOG','')!r}")
    typer.echo(f"YT_STREAMS_DATA_DIR={os.environ.get('YT_STREAMS_DATA_DIR','')!r}")
    resolved = _resolve_default_url(url, data_dir)
    typer.echo(f"resolved_url={resolved!r}")
    store = Storage(root=data_dir)
    typer.echo(f"ledger_path={store.ledger_path}")
    typer.echo(f"meta_path={store.meta_path}")
    typer.echo(f"schedules_path={data_dir / 'schedules.jsonl'}")


# --------------------------------------------------------------------------- #
# TUI entry (optional)
# --------------------------------------------------------------------------- #

@app.command("tui")
def tui(
    data_dir: Path = typer.Option(Path("data/yt_streams"), help="Data directory."),
) -> None:
    """Launch the Textual TUI (if installed)."""
    try:
        from .tui import run as run_tui  # type: ignore
    except Exception as exc:  # pragma: no cover
        typer.echo(f"Textual TUI not available: {exc}")
        raise typer.Exit(code=2)
    run_tui(data_dir)


# --------------------------------------------------------------------------- #
# Typer entrypoint (installed via [project.scripts])
# --------------------------------------------------------------------------- #

if __name__ == "__main__":  # pragma: no cover
    app()
