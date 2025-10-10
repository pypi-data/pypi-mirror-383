"""Pool controller and scheduler for :mod:`yt_streams`.

Purpose:
    Coordinate a set of browser workers, provide broadcast controls, and expose
    an internal scheduler (APScheduler) for interval/cron play cycles. The
    controller is the **single writer** to storage (ledger) and the owner of
    the worker set lifecycle.

Design:
    - Composition over inheritance: this class mixes in
      :class:`~yt_streams.ratelimit.RateLimitMixin` for optional rate limits.
    - Startup creates **N** worker threads (isolation: one Chromium per worker).
    - A thread-safe ``status_sink`` (``queue.Queue``) is used for push-based
      telemetry from workers. UIs (Textual/Streamlit) drain this queue.
    - APScheduler (BackgroundScheduler) lives in the same process and triggers
      broadcasts, not direct worker calls, keeping a single control path.

Preconditions:
    - Playwright Chromium is installed (``playwright install chromium``).

Postconditions:
    - ``start()`` returns immediately after workers are launched and the
      scheduler is started.
    - ``stop()`` signals workers to shut down and stops the scheduler.

Examples:
    Programmatic lifecycle::

        >>> from yt_streams.controller import PoolController  # doctest: +SKIP
        >>> from yt_streams.models import Command, IntervalSpec  # doctest: +SKIP
        >>> ctl = PoolController(url="https://www.youtube.com/watch?v=abc", workers=2)  # doctest: +SKIP
        >>> ctl.start()  # doctest: +SKIP
        >>> ctl.broadcast(Command(play_seconds=10))  # doctest: +SKIP
        >>> _ = ctl.schedule_interval(IntervalSpec(hours=0, minutes=1, seconds=0), play_seconds=10)  # doctest: +SKIP
        >>> ctl.stop()  # doctest: +SKIP
"""
from __future__ import annotations

import atexit
import queue
from typing import Iterable

from apscheduler.schedulers.background import BackgroundScheduler  # type: ignore
from apscheduler.triggers.cron import CronTrigger  # type: ignore
from apscheduler.triggers.interval import IntervalTrigger  # type: ignore

from .models import Command, CronSpec, IntervalSpec, WorkerState
from .ratelimit import RateLimitMixin
from .worker import BrowserOptions, Worker


class PoolController(RateLimitMixin):
    """Manage a pool of workers and an internal scheduler.

    Args:
        url: Canonical YouTube watch URL to open in each worker.
        workers: Number of worker threads to start.
        browser: Browser options to apply to each worker's Chromium context.
        qsize: Max size for the status queue (drop-on-full semantics).
        timezone: Scheduler timezone (IANA).

    Attributes:
        status_sink: ``queue.Queue[WorkerState]`` receiving worker telemetry.
        command_queues: Per-worker command queues (internal control channel).
        scheduler: APScheduler BackgroundScheduler instance.

    Raises:
        ValueError: If ``workers`` < 1.

    Examples:
        ::
            >>> isinstance(PoolController(url="https://x", workers=1), PoolController)
            True
    """

    def __init__(
        self,
        *,
        url: str,
        workers: int,
        browser: BrowserOptions | None = None,
        qsize: int = 4096,
        timezone: str = "UTC",
    ) -> None:
        super().__init__()
        if workers < 1:
            raise ValueError("workers must be >= 1")
        self.url = url
        self.requested_workers = workers
        self.browser = browser or BrowserOptions()
        self.status_sink: "queue.Queue[WorkerState]" = queue.Queue(maxsize=qsize)
        self.command_queues: list["queue.Queue[Command]"] = []
        self.workers: list[Worker] = []
        self.scheduler = BackgroundScheduler(timezone=timezone)

        # Rate-limit: gate broadcast of play cycles (e.g., 1 token per 2 seconds).
        # Capacity allows short bursts up to workers/2.
        self.init_bucket(
            "play_cycle",
            capacity=max(1, workers // 2),
            refill_rate_per_sec=0.5,  # 1 token every 2s
        )

        # Ensure cleanup on interpreter exit (best-effort).
        atexit.register(self.stop)

    # ---------------- Lifecycle ----------------
    def start(self) -> None:
        """Launch workers and start the background scheduler."""
        # spawn workers
        for wid in range(self.requested_workers):
            cq: "queue.Queue[Command]" = queue.Queue()
            w = Worker(wid, self.url, self.status_sink, cq, options=self.browser)
            self.command_queues.append(cq)
            self.workers.append(w)
            w.start()
        # start scheduler
        self.scheduler.start()

    def stop(self) -> None:
        """Signal workers to stop and shut down the scheduler."""
        try:
            for w in self.workers:
                w.stop()
        finally:
            try:
                self.scheduler.shutdown(wait=False)
            except Exception:
                pass

    # ---------------- Dispatch ----------------
    def broadcast(self, cmd: Command) -> None:
        """Send a command to all workers, honoring rate limits.

        Args:
            cmd: The command to broadcast (e.g., ``Command(play_seconds=60)``).
        """
        if not self.try_acquire("play_cycle"):
            return
        for cq in self.command_queues:
            cq.put(cmd)

    # ---------------- Scheduling ----------------
    def schedule_interval(self, spec: IntervalSpec, *, play_seconds: int) -> str:
        """Register an interval job that broadcasts a play cycle.

        Args:
            spec: Interval components.
            play_seconds: Play window length for each broadcast.

        Returns:
            The APScheduler job id.
        """
        trig: IntervalTrigger = spec.to_trigger()
        job = self.scheduler.add_job(
            lambda: self.broadcast(Command(play_seconds=play_seconds)),
            trigger=trig,
            coalesce=True,
            max_instances=1,
            replace_existing=False,
        )
        return job.id

    def schedule_cron(self, spec: CronSpec, *, play_seconds: int) -> str:
        """Register a cron job that broadcasts a play cycle.

        Args:
            spec: Cron expression wrapper.
            play_seconds: Play window length for each broadcast.

        Returns:
            The APScheduler job id.
        """
        trig: CronTrigger = spec.to_trigger()
        job = self.scheduler.add_job(
            lambda: self.broadcast(Command(play_seconds=play_seconds)),
            trigger=trig,
            coalesce=True,
            max_instances=1,
            replace_existing=False,
        )
        return job.id

    # ---------------- Utilities ----------------
    def drain_status(self, max_items: int | None = None) -> list[WorkerState]:
        """Non-blocking drain of the status queue.

        Args:
            max_items: Optional cap on the number of items to drain.

        Returns:
            A list of :class:`WorkerState` objects in FIFO order drained from
            the queue at the time of the call.
        """
        out: list[WorkerState] = []
        while True:
            if max_items is not None and len(out) >= max_items:
                break
            try:
                item = self.status_sink.get_nowait()
            except queue.Empty:
                break
            else:
                out.append(item)
        return out
