# dags/yt_streams_catalog.py
"""
Airflow DAG: choose from a catalog and append a targeted pulse.

- Uses Airflow 3 Task SDK decorators: airflow.sdk.dag / airflow.sdk.task
- Timezone-aware start_date via pendulum (best practice)

Env:
    YT_STREAMS_DATA_DIR   # used if DATA_DIRS not provided

Catalog CSV/JSONL columns: url, weight(=1.0), active(=1/0), note(optional)
"""
from __future__ import annotations

import pendulum
from datetime import timedelta
from airflow.sdk import dag, task  # <-- new public imports (Airflow 3)

# Import a PURE helper (must not import Airflow itself).
# Your module should internally use yt_streams.catalog_io + control.append_command.
from yt_streams.airflow.tasks import append_random_pulse_from_catalog

CRON = "*/13 9-21 * * 1-5"
TZ = "America/Toronto"
CATALOG = "/srv/yt_streams/catalog.csv"    # or .jsonl
DATA_DIRS = ["/srv/yt_streams/a", "/srv/yt_streams/b"]  # optional

@dag.dag(
    dag_id="yt_streams_catalog",
    schedule=CRON,
    start_date=pendulum.datetime(2025, 1, 1, tz=TZ),
    catchup=False,
    max_active_runs=1,
    default_args={"retries": 1, "retry_delay": timedelta(minutes=2)},
    tags=["yt_streams", "catalog"],
)
def _dag():
    @task.task(pool="yt_streams_pulse")
    def choose_and_fire() -> str:
        return append_random_pulse_from_catalog(
            catalog_path=CATALOG,
            data_dirs=DATA_DIRS,           # omit to fall back to $YT_STREAMS_DATA_DIR
            strategy="weighted",           # or "first"
            play_min=45,
            play_max=90,
            shard_choose="random",
            note_prefix="airflow:catalog",
        )

    choose_and_fire()

dag = _dag()
