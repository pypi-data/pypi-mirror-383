"""Airflow integration surface for :mod:`yt_streams`.

Purpose:
    Provide a stable public API for DAG files without importing Airflow at
    package import time. Re-exports task callables (to append control commands)
    and catalog utilities (load/save/edit/choose URLs).

Public API:
    Tasks
        - append_random_pulse
        - append_pulse_for_url
        - append_random_pulse_from_catalog
    Catalog
        - CatalogItem
        - load_catalog, save_catalog
        - choose_item
        - toggle_active, set_weight
        - add_item, remove_item

Examples:
    TaskFlow DAG (weighted catalog pick)::

        >>> # dags/yt_streams_catalog.py  # doctest: +SKIP
        >>> from datetime import datetime, timedelta  # doctest: +SKIP
        >>> from airflow.decorators import dag, task  # doctest: +SKIP
        >>> from yt_streams.airflow import append_random_pulse_from_catalog  # doctest: +SKIP
        >>> @dag(start_date=datetime(2025,1,1), schedule="*/13 9-21 * * 1-5", catchup=False)  # doctest: +SKIP
        ... def yt_streams_catalog():  # doctest: +SKIP
        ...     @task(pool="yt_streams_pulse", retries=1, retry_delay=timedelta(minutes=2))  # doctest: +SKIP
        ...     def fire():  # doctest: +SKIP
        ...         return append_random_pulse_from_catalog(  # doctest: +SKIP
        ...             catalog_path="/srv/yt_streams/catalog.csv",
        ...             data_dirs=["/srv/yt_streams/a", "/srv/yt_streams/b"],
        ...             strategy="weighted",
        ...             play_min=45, play_max=90,
        ...         )
        ...     fire()  # doctest: +SKIP
        >>> dag = yt_streams_catalog()  # doctest: +SKIP
"""
from __future__ import annotations

from typing import Final

# Task helpers (framework-agnostic)
from .tasks import (
    append_random_pulse,
    append_pulse_for_url,
    append_random_pulse_from_catalog,
)

# Catalog utilities
from .catalog import (
    CatalogItem,
    load_catalog,
    save_catalog,
    choose_item,
    toggle_active,
    set_weight,
    add_item,
    remove_item,
)

__all__: Final[list[str]] = [
    # tasks
    "append_random_pulse",
    "append_pulse_for_url",
    "append_random_pulse_from_catalog",
    # catalog
    "CatalogItem",
    "load_catalog",
    "save_catalog",
    "choose_item",
    "toggle_active",
    "set_weight",
    "add_item",
    "remove_item",
]
