"""File-based control channel for :mod:`yt_streams`.

Purpose:
    Enable an external UI (e.g., Streamlit) to send commands to a running
    :class:`~yt_streams.controller.PoolController` **without sockets/HTTP** by
    appending JSONL messages to a well-known file that a broker tails.

Design:
    - Writers call :func:`append_command` with a :class:`ControlCommand`.
    - The :class:`ControlBroker` runs in the controller process, polling a
      JSONL file and applying side effects (broadcast pulse, register interval/
      cron schedules).
    - Commands are idempotent-ish; each carries a timestamp and optional seq.

Schema:
    Supported verbs:
      - ``"pulse"``      → broadcast one play cycle.
      - ``"interval"``   → register an interval schedule.
      - ``"cron"``       → register a cron schedule.

Randomization:
    Each command can either specify a fixed ``play_seconds`` or a range via
    ``play_min``/``play_max``. The broker will pick a random value within that
    range *at application time*. For interval/cron, the value is bound at
    registration (simple & predictable).

Artifacts:
    - Control input  : ``commands.jsonl`` (append-only)
    - Schedule mirror: ``schedules.jsonl`` (append-only, for UIs)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, Literal

import json
import random
import threading
import time

from pydantic import BaseModel, Field, model_validator

from .models import CronSpec, IntervalSpec


# ------------------------------- Constants ------------------------------------

CONTROL_FILE: Final[str] = "commands.jsonl"
"""File name of the incoming control channel (append-only JSONL)."""

SCHEDULES_FILE: Final[str] = "schedules.jsonl"
"""File name where accepted schedule registrations are mirrored (append-only)."""


# --------------------------------- Models -------------------------------------

class ControlCommand(BaseModel):
    """Serialized control message understood by the broker.

    Args:
        verb: One of ``"pulse"``, ``"interval"``, ``"cron"``.
        args: Verb-specific arguments.
        ts: POSIX timestamp when the command was created.
        seq: Optional monotonic sequence for UI-side ordering/dedup.
        note: Optional string note for human traceability (UI/debug).

    Common ``args`` keys:
        - For all verbs:
            * ``play_seconds`` (int) — explicit fixed play window
            * ``play_min``/``play_max`` (int) — random window bounds (inclusive)
        - For ``interval``:
            * ``text`` (str) — "HH:MM:SS" | "MM:SS" | "SS"
        - For ``cron``:
            * ``expr`` (str) — standard 5-field cron expression

    Raises:
        ValueError: If both ``play_seconds`` and a play range are present.

    Examples:
        ::
            >>> ControlCommand(verb="pulse", args={}, note="one-off").verb
            'pulse'
    """

    verb: Literal["pulse", "interval", "cron"]
    args: dict = Field(default_factory=dict)
    ts: float = Field(default_factory=lambda: time.time())
    seq: int | None = None
    note: str | None = None

    @model_validator(mode="after")
    def _validate_play_choice(self) -> "ControlCommand":
        ps = self.args.get("play_seconds")
        lo = self.args.get("play_min")
        hi = self.args.get("play_max")
        if ps is not None and (lo is not None or hi is not None):
            raise ValueError("Specify either play_seconds OR (play_min/play_max), not both.")
        return self

    # -------------------------- Convenience constructors ----------------------

    @staticmethod
    def pulse(
        *,
        play_seconds: int | None = None,
        play_min: int | None = None,
        play_max: int | None = None,
        note: str | None = None,
    ) -> "ControlCommand":
        args: dict = {}
        if play_seconds is not None:
            args["play_seconds"] = int(play_seconds)
        if play_min is not None:
            args["play_min"] = int(play_min)
        if play_max is not None:
            args["play_max"] = int(play_max)
        return ControlCommand(verb="pulse", args=args, note=note)

    @staticmethod
    def interval(
        text: str,
        *,
        play_seconds: int | None = None,
        play_min: int | None = None,
        play_max: int | None = None,
        note: str | None = None,
    ) -> "ControlCommand":
        args: dict = {"text": str(text)}
        if play_seconds is not None:
            args["play_seconds"] = int(play_seconds)
        if play_min is not None:
            args["play_min"] = int(play_min)
        if play_max is not None:
            args["play_max"] = int(play_max)
        return ControlCommand(verb="interval", args=args, note=note)

    @staticmethod
    def cron(
        expr: str,
        *,
        play_seconds: int | None = None,
        play_min: int | None = None,
        play_max: int | None = None,
        note: str | None = None,
    ) -> "ControlCommand":
        args: dict = {"expr": str(expr)}
        if play_seconds is not None:
            args["play_seconds"] = int(play_seconds)
        if play_min is not None:
            args["play_min"] = int(play_min)
        if play_max is not None:
            args["play_max"] = int(play_max)
        return ControlCommand(verb="cron", args=args, note=note)


# ------------------------------- Write helpers --------------------------------

def append_command(root: Path, cmd: ControlCommand) -> None:
    """Append a single command to ``commands.jsonl``.

    Args:
        root: Data directory containing :data:`CONTROL_FILE`.
        cmd: Command to append.
    """
    root.mkdir(parents=True, exist_ok=True)
    p = root / CONTROL_FILE
    with p.open("a", encoding="utf-8") as f:
        f.write(cmd.model_dump_json() + "\n")


def append_commands(root: Path, cmds: list[ControlCommand]) -> None:
    """Append multiple commands efficiently.

    Args:
        root: Data directory.
        cmds: Commands to append in order.
    """
    if not cmds:
        return
    root.mkdir(parents=True, exist_ok=True)
    p = root / CONTROL_FILE
    with p.open("a", encoding="utf-8") as f:
        for c in cmds:
            f.write(c.model_dump_json() + "\n")


# ------------------------------- Control broker -------------------------------

@dataclass(slots=True)
class ControlBroker:
    """Tail and apply commands from a JSONL file to a running controller.

    Args:
        root: Data directory containing :data:`CONTROL_FILE`.
        controller: A running :class:`~yt_streams.controller.PoolController`.
        poll_seconds: Poll cadence to check the control file.

    Notes:
        - Single-reader; meant to live in the same process as the controller.
        - The broker starts a background thread and stops via :meth:`stop`.
    """

    root: Path
    controller: "PoolController"
    poll_seconds: float = 0.5

    # Internal state (must be declared when using slots=True)
    _stop: threading.Event = field(init=False, repr=False, compare=False)
    _thread: threading.Thread | None = field(init=False, default=None, repr=False, compare=False)
    _offset: int = field(init=False, default=0, repr=False, compare=False)

    def __post_init__(self) -> None:  # noqa: D401 - dataclass init detail
        # With slots, these assignments are valid because fields are declared.
        self._stop = threading.Event()
        (self.root / CONTROL_FILE).parent.mkdir(parents=True, exist_ok=True)
        (self.root / CONTROL_FILE).touch(exist_ok=True)

    # ------------------------------- Lifecycle --------------------------------

    def start(self) -> None:
        """Start the background tailer thread."""
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._run, name="control-broker", daemon=True
        )
        self._thread.start()

    def stop(self) -> None:
        """Signal the broker thread to stop and join."""
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=5.0)

    # -------------------------------- Internals -------------------------------

    def _run(self) -> None:
        p = self.root / CONTROL_FILE
        while not self._stop.is_set():
            try:
                self._drain_file(p)
            except Exception:
                # best-effort: swallow & continue
                pass
            # Lightweight wait so we respond quickly but avoid busy-spin
            self._stop.wait(self.poll_seconds)

    def _drain_file(self, p: Path) -> None:
        try:
            size = p.stat().st_size
        except FileNotFoundError:
            return
        if size <= self._offset:
            return
        with p.open("r", encoding="utf-8") as f:
            f.seek(self._offset)
            for line in f:
                s = line.strip()
                if not s:
                    continue
                try:
                    cmd = ControlCommand.model_validate_json(s)
                except Exception:
                    # ignore malformed lines
                    continue
                self._apply(cmd)
            self._offset = f.tell()

    # ----------------------------- Command application ------------------------

    def _apply(self, cmd: ControlCommand) -> None:
        """Apply a single command to the controller."""
        if cmd.verb == "pulse":
            self._apply_pulse(cmd)
        elif cmd.verb == "interval":
            self._apply_interval(cmd)
        elif cmd.verb == "cron":
            self._apply_cron(cmd)

    # ---- verb helpers ----

    def _pick_play_seconds(self, args: dict, *, default: int = 60) -> int:
        """Choose a play window using explicit or randomized args.

        Precedence:
            1. args['play_seconds'] if present
            2. randint(args['play_min'], args['play_max']) if a valid range
            3. default (>= 5)
        """
        ps = args.get("play_seconds")
        if ps is not None:
            return max(int(ps), 5)
        lo = args.get("play_min")
        hi = args.get("play_max")
        if lo is not None and hi is not None:
            lo_i, hi_i = int(lo), int(hi)
            if hi_i < lo_i:
                lo_i, hi_i = hi_i, lo_i
            return max(random.randint(lo_i, hi_i), 5)
        return max(default, 5)

    def _apply_pulse(self, cmd: ControlCommand) -> None:
        from .models import Command  # local import to keep module side-effects small

        ps = self._pick_play_seconds(cmd.args, default=60)
        self.controller.broadcast(Command(play_seconds=ps, url=cmd.args.get("url")))

    def _apply_interval(self, cmd: ControlCommand) -> None:
        text = str(cmd.args.get("text") or "")
        if not text:
            return
        ps = self._pick_play_seconds(cmd.args, default=60)
        spec = IntervalSpec.from_text(text)
        job_id = self.controller.schedule_interval(spec, play_seconds=ps, url=cmd.args.get("url"))
        self._mirror_schedule(
            kind="interval",
            payload={"text": text, "play_seconds": ps, "job_id": job_id, "note": cmd.note},
        )

    def _apply_cron(self, cmd: ControlCommand) -> None:
        expr = str(cmd.args.get("expr") or "")
        if not expr:
            return
        ps = self._pick_play_seconds(cmd.args, default=60)
        spec = CronSpec(expr=expr)
        job_id = self.controller.schedule_cron(spec, play_seconds=ps, url=cmd.args.get("url"))
        self._mirror_schedule(
            kind="cron",
            payload={"expr": expr, "play_seconds": ps, "job_id": job_id, "note": cmd.note},
        )

    # ------------------------------ Schedule mirror ---------------------------

    def _mirror_schedule(self, *, kind: Literal["interval", "cron"], payload: dict) -> None:
        """Append an accepted schedule registration to ``schedules.jsonl``.

        Args:
            kind: ``"interval"`` or ``"cron"``.
            payload: Dict with at least the fields used by UIs (e.g., text/expr,
                play_seconds, job_id, optional note).
        """
        p = self.root / SCHEDULES_FILE
        record = {"ts": time.time(), "kind": kind, **payload}
        try:
            with p.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception:
            # non-fatal; scheduling still succeeded
            pass


__all__ = [
    "ControlCommand",
    "append_command",
    "append_commands",
    "ControlBroker",
    "CONTROL_FILE",
    "SCHEDULES_FILE",
]
