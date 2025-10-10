"""Storage utilities for :mod:`yt_streams` artifacts.

Purpose:
    Provide a thin, well-typed persistence layer for controller/worker
    artifacts, using append-only **CSV** (run ledger) and **JSONL** (metadata
    cache and schedule mirror). A light **Parquet** export is available if
    ``pandas`` and ``pyarrow`` are installed.

Design:
    - ``Storage`` is path-centric and side-effect-free until methods are
      invoked. It never holds open file handles between calls.
    - Writes are **append-only** with ``newline=""`` to avoid doubling newlines
      across platforms. A simple in-process lock prevents concurrent appends.
      For multi-process writers, we rely on the atomicity of append writes on
      modern OSes; still, single-writer is recommended.
    - Ledger rows are derived from :class:`~yt_streams.models.RunRecord`
      (Pydantic v2). For speed, we write CSV via ``csv.DictWriter`` using a
      stable header order.
    - Metadata cache stores :class:`~yt_streams.models.VideoInfo` as JSONL for
      easy tail/grep. No dedup index is kept (caller may add one if needed).

Attributes:
    DEFAULT_DIR (Path): Default data directory ``data/yt_streams``.

Examples:
    Minimal usage::

        >>> from pathlib import Path  # doctest: +SKIP
        >>> from yt_streams.storage import Storage  # doctest: +SKIP
        >>> store = Storage(Path("data/yt_streams"))  # doctest: +SKIP
        >>> store.ensure()  # doctest: +SKIP
        >>> # store.append_run(record)  # where `record` is a RunRecord         # doctest: +SKIP

    Export to Parquet if libs available::

        >>> p = store.export_parquet()  # doctest: +SKIP
        >>> print(p)  # doctest: +SKIP
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, Iterable, Iterator, Literal, Sequence
import csv
import io
import json
import threading

try:  # soft optional deps
    import pandas as _pd  # type: ignore
except Exception:  # pragma: no cover - optional
    _pd = None  # type: ignore

from .models import RunRecord, VideoInfo


DEFAULT_DIR: Final[Path] = Path("data/yt_streams")
_LEDGER_NAME: Final[str] = "runs.csv"
_META_NAME: Final[str] = "meta.jsonl"


@dataclass(slots=True)
class Storage:
    """Persist and read controller/worker artifacts.

    Args:
        root: Data directory. Created on first write or via :meth:`ensure`.

    Attributes:
        root: Root directory for artifacts.
        _lock: Process-local append lock.

    Notes:
        *Writes*: This class assumes **single-process writing** for strict
        ordering. Concurrent processes appending to the same file may interleave
        lines on some filesystems. If you need cross-process safety, add a file
        lock (e.g., ``fcntl``/``msvcrt``) in your environment.

    Examples:
        ::
            >>> s = Storage(DEFAULT_DIR)  # doctest: +SKIP
            >>> s.ensure()  # doctest: +SKIP
    """

    root: Path = DEFAULT_DIR
    # ADD THIS:
    _lock: threading.Lock = field(init=False, repr=False, compare=False, default_factory=threading.Lock)


    def __post_init__(self) -> None:
        self._lock = threading.Lock()

    # ----------------------------- Paths & ensure -----------------------------
    @property
    def ledger_path(self) -> Path:
        """Return the path to the ledger CSV.

        Returns:
            Path: ``<root>/runs.csv``.

        Examples:
            ::
                >>> Storage().ledger_path.name
                'runs.csv'
        """
        return self.root / _LEDGER_NAME

    @property
    def meta_path(self) -> Path:
        """Return the path to the metadata JSONL.

        Returns:
            Path: ``<root>/meta.jsonl``.
        """
        return self.root / _META_NAME

    def ensure(self) -> None:
        """Create the root directory if missing.

        Returns:
            ``None``.
        """
        self.root.mkdir(parents=True, exist_ok=True)

    # ------------------------------- Ledger I/O -------------------------------
    _LEDGER_FIELDS: Final[Sequence[str]] = (
        "ts",
        "wid",
        "phase",
        "play_seconds",
        "refreshes",
        "error",
    )

    def append_run(self, rec: RunRecord) -> None:
        """Append a :class:`RunRecord` to the ledger.

        Args:
            rec: Record to append.

        Returns:
            ``None``.

        Examples:
            ::
                >>> from yt_streams.models import RunRecord  # doctest: +SKIP
                >>> # s.append_run(RunRecord(...))  # doctest: +SKIP
        """
        self.ensure()
        row = {
            "ts": f"{float(rec.ts):.6f}",
            "wid": int(rec.wid),
            "phase": str(rec.phase),
            "play_seconds": int(rec.play_seconds),
            "refreshes": int(rec.refreshes),
            "error": "" if rec.error is None else str(rec.error),
        }
        with self._lock:
            file_exists = self.ledger_path.exists()
            with self.ledger_path.open("a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(self._LEDGER_FIELDS))
                if not file_exists:
                    writer.writeheader()
                writer.writerow(row)

    def read_ledger(self) -> Iterator[dict[str, str]]:
        """Iterate over ledger rows as string dicts (streaming).

        Returns:
            Iterator over mapping of column→string.
        """
        p = self.ledger_path
        if not p.exists():
            return iter(())
        with p.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield {k: (v if v is not None else "") for k, v in row.items()}

    def tail_ledger(self, n: int) -> list[dict[str, str]]:
        """Return the last ``n`` ledger rows efficiently.

        Args:
            n: Number of rows from the end (>=1).

        Returns:
            List of row dicts (possibly fewer if file is short/non-existent).
        """
        if n <= 0:
            return []
        p = self.ledger_path
        if not p.exists():
            return []
        # Heuristic: read last ~1MB or file size, then split lines
        size = p.stat().st_size
        chunk = min(size, 1_000_000)
        with p.open("rb") as f:
            f.seek(max(0, size - chunk))
            data = f.read().decode("utf-8", errors="ignore")
        lines = data.splitlines()
        # Ensure we have header; find last header occurrence
        header_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith("ts,wid,phase,play_seconds,refreshes,error"):
                header_idx = i
        relevant = lines[max(header_idx, len(lines) - (n + 1)) :]
        reader = csv.DictReader(io.StringIO("\n".join(relevant)))
        return [dict(r) for r in reader]

    # ------------------------------ Metadata I/O ------------------------------

    def cache_video_info(self, info: VideoInfo) -> None:
        """Append a :class:`VideoInfo` entry to the JSONL cache.

        Args:
            info: Video metadata structured record.

        Returns:
            ``None``.
        """
        self.ensure()
        with self._lock:
            with self.meta_path.open("a", encoding="utf-8") as f:
                f.write(info.model_dump_json() + "\n")

    # ------------------------------ Parquet Export ----------------------------

    def export_parquet(self, *, out: Path | None = None) -> Path | None:
        """Export the ledger to Parquet if dependencies are available.

        Args:
            out: Output path. If omitted, ``<root>/runs.parquet`` is used.

        Returns:
            Path to the Parquet file on success, else ``None`` (e.g., pandas
            not installed or ledger missing/empty).

        Examples:
            ::
                >>> # p = Storage().export_parquet()  # doctest: +SKIP
        """
        if _pd is None:  # pandas not installed
            return None
        p = self.ledger_path
        if not p.exists():
            return None
        try:
            df = _pd.read_csv(p)
        except Exception:
            return None
        if df.empty:
            return None
        out_path = out or (self.root / "runs.parquet")
        try:
            df.to_parquet(out_path, index=False)
        except Exception:
            return None
        return out_path


__all__: Final[list[str]] = ["Storage", "DEFAULT_DIR"]
