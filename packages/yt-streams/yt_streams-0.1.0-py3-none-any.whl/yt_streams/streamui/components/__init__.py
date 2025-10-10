"""
Component namespace for :mod:`yt_streams.streamui`.

Purpose:
    Provide stable import paths and a curated public API for Streamlit view
    components used by the dashboard. Each symbol is lazily imported and
    gracefully degrades with a clear error if the underlying module is absent.

Public API:
    - :func:`render_controls`
    - :func:`render_schedules`
    - :func:`render_schedules_viz`
    - :func:`render_catalog`
    - :func:`render_workers`
    - :func:`render_errors`
    - :func:`render_config`
    - :func:`render_ledger`

Examples:
    Import a component in a custom app::

        >>> # doctest: +SKIP
        >>> from yt_streams.streamui.components import render_controls
        >>> render_controls(ui)  # doctest: +SKIP
"""
from __future__ import annotations

from typing import Any, Callable, Final


def _lazy_load(mod_path: str, attr: str) -> Callable[..., Any]:
    """
    Import `attr` from `mod_path` and return it. If the import fails,
    return a stub that raises a helpful RuntimeError on first call.
    """
    try:
        module = __import__(mod_path, fromlist=[attr])
        obj = getattr(module, attr)  # may raise AttributeError
        return obj  # type: ignore[no-any-return]
    except Exception as exc:
        def _missing(*_args: Any, **_kwargs: Any) -> None:
            raise RuntimeError(
                f"Component '{attr}' unavailable: failed to import "
                f"{mod_path}.{attr} ({exc!r}). Ensure the file exists and imports succeed."
            ) from exc
        return _missing


# Lazily bind all public renderers. If a submodule is missing, callers get a clear error.
render_controls        = _lazy_load("yt_streams.streamui.components.controls",       "render_controls")
render_schedules       = _lazy_load("yt_streams.streamui.components.schedules",      "render_schedules")
render_schedules_viz   = _lazy_load("yt_streams.streamui.components.schedules_viz",  "render_schedules")
render_catalog         = _lazy_load("yt_streams.streamui.components.catalog",        "render_catalog")
render_workers         = _lazy_load("yt_streams.streamui.components.workers",        "render_workers")
render_errors          = _lazy_load("yt_streams.streamui.components.errors",         "render_errors")
render_config          = _lazy_load("yt_streams.streamui.components.config",         "render_config")
render_ledger          = _lazy_load("yt_streams.streamui.components.ledger",         "render_ledger")


__all__: Final[list[str]] = [
    "render_controls",
    "render_schedules",
    "render_schedules_viz",
    "render_catalog",
    "render_workers",
    "render_errors",
    "render_config",
    "render_ledger",
]
