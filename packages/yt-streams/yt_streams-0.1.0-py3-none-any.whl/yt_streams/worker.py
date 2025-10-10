"""Browser worker thread for :mod:`yt_streams` using Playwright (Chromium).

Purpose:
    Each worker owns **one OS thread** and runs a **private asyncio loop** inside
    that thread to control a single Playwright Chromium instance (1 browser →
    1 context → 1 page). Workers receive :class:`~yt_streams.models.Command`
    messages from the controller and emit :class:`~yt_streams.models.WorkerState`
    updates into a thread‑safe queue for UIs and logging.

Design:
    - Thread boundary: the worker is a subclass of :class:`threading.Thread`.
    - Async boundary: the Playwright async API is driven by a per‑thread loop
      via :func:`asyncio.run` inside :meth:`Worker.run`.
    - Isolation: each worker has its own browser context (cookies/storage/UA).
    - Status: periodic heartbeats + edge updates (errors, refreshes).

Preconditions:
    - Playwright is installed and Chromium has been set up (e.g.,
      ``playwright install chromium``).

Postconditions:
    - When :meth:`stop` is called, the worker cleans up its page/context/browser
      and transitions to the ``stopped`` phase.

Examples:
    Minimal lifecycle (doctest uses ``+SKIP`` to avoid launching a browser)::

        >>> import queue  # doctest: +SKIP
        >>> from yt_streams.models import Command  # doctest: +SKIP
        >>> status: "queue.Queue" = queue.Queue()  # doctest: +SKIP
        >>> cmds: "queue.Queue" = queue.Queue()    # doctest: +SKIP
        >>> w = Worker(0, "https://www.youtube.com/watch?v=dQw4w9WgXcQ", status, cmds)  # doctest: +SKIP
        >>> w.start(); cmds.put(Command(play_seconds=5))  # doctest: +SKIP
        >>> w.stop(); w.join(timeout=5)  # doctest: +SKIP
"""
from __future__ import annotations

import asyncio
import random
import threading
import time
from dataclasses import dataclass
from typing import Any, Mapping, MutableMapping

from playwright.async_api import (  # type: ignore
    async_playwright,
    Browser,
    BrowserContext,
    Page,
)
from playwright_stealth import stealth
from fake_useragent import UserAgent

from .stealth import stealth_utils
from .robots_config import config_manager
from .url_handler import url_handler, get_stealth_config

from .models import Command, WorkerPhase, WorkerState


@dataclass(slots=True)
class BrowserOptions:
    """Options used to configure Chromium contexts per worker.

    Args:
        headless: Launch Chromium headless if ``True``.
        viewport: ``{"width": int, "height": int}`` mapping for context size.
        user_agent: Optional User‑Agent string override.
        proxy: Optional proxy URL (e.g., ``http://user:pass@host:port``).
        stealth: Enable stealth mode to avoid bot detection.
        random_user_agent: Use random user agent from fake-useragent.
    """

    headless: bool = False
    viewport: Mapping[str, int] = None  # type: ignore[assignment]
    user_agent: str | None = None
    proxy: str | None = None
    stealth: bool = True
    random_user_agent: bool = True

    def __post_init__(self) -> None:  # pragma: no cover - trivial defaulting
        if self.viewport is None:
            # Use stealth config for viewport randomization
            if config_manager.stealth_config.random_viewport:
                width = random.randint(1200, 1920)
                height = random.randint(800, 1080)
                self.viewport = {"width": width, "height": height}
            else:
                self.viewport = {"width": 1280, "height": 720}
        
        if self.random_user_agent and not self.user_agent:
            # Use stealth utils for user agent generation
            self.user_agent = stealth_utils.get_random_user_agent()
    
    def configure_for_url(self, url: str) -> None:
        """Configure browser options based on URL type"""
        stealth_config = get_stealth_config(url)
        
        # Override stealth settings based on URL type
        if not stealth_config['stealth_required']:
            self.stealth = False
        
        if not stealth_config['user_agent_rotation']:
            self.random_user_agent = False
        
        if not stealth_config['viewport_randomization']:
            self.viewport = {"width": 1280, "height": 720}


class Worker(threading.Thread):
    """A single Playwright‑driven browser worker.

    Args:
        wid: Worker id (0..N‑1).
        url: Canonical YouTube watch URL to open.
        status_sink: A ``queue.Queue[WorkerState]`` receiving telemetry updates.
        command_queue: A ``queue.Queue[Command]`` providing work to execute.
        options: Optional :class:`BrowserOptions` for Chromium/context setup.

    Raises:
        RuntimeError: On irrecoverable initialization failures inside the
            asynchronous main loop.

    Examples:
        Thread creation (no browser launched in doctest)::

            >>> import queue  # doctest: +SKIP
            >>> status, cmds = queue.Queue(), queue.Queue()  # doctest: +SKIP
            >>> Worker(1, "https://x", status, cmds)  # doctest: +SKIP
            <...Worker...>
    """

    def __init__(
        self,
        wid: int,
        url: str,
        status_sink: "queue.Queue[WorkerState]",
        command_queue: "queue.Queue[Command]",
        options: BrowserOptions | None = None,
    ) -> None:
        super().__init__(name=f"worker-{wid}", daemon=True)
        self.wid = wid
        self.url = url
        self.status_sink = status_sink
        self.command_queue = command_queue
        self.options = options or BrowserOptions()
        # Configure options based on URL type
        self.options.configure_for_url(url)
        self._stop = threading.Event()
        self._browser: Browser | None = None
        self._ctx: BrowserContext | None = None
        self._page: Page | None = None

    # ---------------- Public API ----------------
    def stop(self) -> None:
        """Signal the worker to stop at the next safe point."""
        self._stop.set()

    # --------------- Thread entrypoint ---------------
    def run(self) -> None:  # noqa: D401 - standard thread entrypoint docstring omitted
        asyncio.run(self._amain())

    # --------------- Async internals ---------------
    async def _amain(self) -> None:
        self._emit(phase=WorkerPhase.initialized)
        try:
            async with async_playwright() as pw:
                # Launch browser with stealth options from config
                launch_options = {
                    "headless": self.options.headless,
                    "args": [
                        "--no-sandbox",
                        "--disable-blink-features=AutomationControlled",
                        "--disable-dev-shm-usage",
                        "--disable-extensions",
                        "--disable-gpu",
                        "--disable-web-security",
                        "--disable-features=VizDisplayCompositor",
                        "--disable-ipc-flooding-protection",
                        "--disable-renderer-backgrounding",
                        "--disable-backgrounding-occluded-windows",
                        "--disable-client-side-phishing-detection",
                        "--disable-sync",
                        "--disable-default-apps",
                        "--disable-hang-monitor",
                        "--disable-prompt-on-repost",
                        "--disable-domain-reliability",
                        "--disable-component-extensions-with-background-pages",
                        "--disable-background-timer-throttling",
                        "--disable-background-networking",
                        "--disable-breakpad",
                        "--disable-component-update",
                        "--disable-features=TranslateUI",
                        "--no-first-run",
                        "--no-default-browser-check",
                        "--no-pings",
                        "--password-store=basic",
                        "--use-mock-keychain",
                    ]
                }
                
                # Add stealth-specific arguments based on config
                if config_manager.stealth_config.disable_images:
                    launch_options["args"].extend(["--disable-images"])
                if config_manager.stealth_config.disable_css:
                    launch_options["args"].extend(["--disable-css"])
                if config_manager.stealth_config.disable_js:
                    launch_options["args"].extend(["--disable-javascript"])
                if config_manager.stealth_config.block_ads:
                    launch_options["args"].extend(["--disable-extensions-except", "--disable-plugins-except"])
                
                self._browser = await pw.chromium.launch(**launch_options)
                
                # Create context with stealth settings from config
                context_kwargs: MutableMapping[str, Any] = {
                    "viewport": dict(self.options.viewport),
                    "user_agent": self.options.user_agent,
                    "locale": "en-US",
                    "timezone_id": "America/New_York",
                    "permissions": ["geolocation"],
                    "geolocation": {"latitude": 40.7128, "longitude": -74.0060},  # NYC
                    "extra_http_headers": stealth_utils.get_stealth_headers()
                }
                
                if self.options.proxy:
                    context_kwargs["proxy"] = {"server": self.options.proxy}
                
                self._ctx = await self._browser.new_context(**context_kwargs)
                self._page = await self._ctx.new_page()
                
                # Apply stealth measures
                if self.options.stealth:
                    # Note: playwright-stealth apply_stealth_sync is synchronous but may have async components
                    # We'll apply it after the page is ready
                    pass
                
                # Add additional stealth JavaScript
                await self._page.add_init_script("""
                    // Remove webdriver property
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                    
                    // Mock plugins
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5],
                    });
                    
                    // Mock languages
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en'],
                    });
                    
                    // Mock permissions
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );
                    
                    // Mock chrome runtime
                    window.chrome = {
                        runtime: {},
                    };
                    
                    // Override the `plugins` property to use a custom getter
                    Object.defineProperty(navigator, 'plugins', {
                        get: function() {
                            return [1, 2, 3, 4, 5];
                        },
                    });
                """)
                
                # Random delay before navigation
                await asyncio.sleep(random.uniform(1, 3))
                
                await self._page.goto(self.url, wait_until="domcontentloaded", timeout=30000)
                
                # Apply stealth measures after page is loaded
                if self.options.stealth:
                    try:
                        stealth.Stealth().apply_stealth_sync(self._page)
                    except Exception as e:
                        print(f"Warning: Failed to apply stealth measures: {e}")
                
                # Random delay after page load
                await asyncio.sleep(random.uniform(2, 5))
                
                await self._ensure_play(self._page)
                # Main command loop
                while not self._stop.is_set():
                    self._emit()  # heartbeat
                    try:
                        cmd = self.command_queue.get(timeout=0.2)
                    except Exception:
                        continue
                    if cmd.name == "play_cycle":
                        await self._play_cycle(self._page, cmd.play_seconds)
        except Exception as e:  # noqa: BLE001 - surface in state, keep thread alive to exit cleanly
            self._emit(phase=WorkerPhase.error, last_error=str(e))
        finally:
            try:
                if self._ctx:
                    await self._ctx.close()
                if self._browser:
                    await self._browser.close()
            except Exception:
                pass
            self._emit(phase=WorkerPhase.stopped)

    async def _ensure_play(self, page: Page) -> None:
        """Attempt to unmute and start playback via the YouTube player API.

        This function is a best‑effort helper; errors are swallowed because
        real playback often proceeds without JS control depending on autoplay
        policies.
        """
        js = """
        (async () => {
          const p = document.getElementById('movie_player');
          if (p && p.playVideo) { p.unMute?.(); p.playVideo?.(); return true; }
          return false;
        })();
        """
        try:
            await page.evaluate(js)
        except Exception:
            pass

    async def _play_cycle(self, page: Page, seconds: int) -> None:
        self._emit(phase=WorkerPhase.working)
        
        # Simulate human-like behavior during playback
        for t in range(seconds):
            if self._stop.is_set():
                break
            
            # Random mouse movements and scrolls to simulate human activity
            if t % 30 == 0:  # Every 30 seconds
                try:
                    # Random mouse movement
                    await page.mouse.move(
                        random.randint(100, 800), 
                        random.randint(100, 600)
                    )
                    
                    # Random scroll
                    if random.random() < 0.3:  # 30% chance
                        await page.mouse.wheel(0, random.randint(-100, 100))
                    
                    # Random pause/play to simulate user interaction
                    if random.random() < 0.1:  # 10% chance
                        await page.keyboard.press("Space")
                        await asyncio.sleep(random.uniform(0.5, 2))
                        await page.keyboard.press("Space")
                        
                except Exception:
                    pass  # Ignore mouse/keyboard errors
            
            await asyncio.sleep(1)
            self._emit(phase=WorkerPhase.working, play_seconds=t + 1)
        
        # Random delay before refresh
        await asyncio.sleep(random.uniform(2, 5))
        
        # Refresh after the window
        try:
            await page.reload(wait_until="domcontentloaded", timeout=30000)
            # Random delay after refresh
            await asyncio.sleep(random.uniform(1, 3))
        except Exception as e:  # surface error but keep thread alive
            self._emit(phase=WorkerPhase.error, last_error=str(e))
            return
        self._emit(phase=WorkerPhase.initialized, play_seconds=0, bump_refresh=True)

    # --------------- Telemetry helper ---------------
    def _emit(
        self,
        *,
        phase: WorkerPhase | None = None,
        play_seconds: int | None = None,
        bump_refresh: bool = False,
        last_error: str | None = None,
    ) -> None:
        """Push a :class:`WorkerState` update to the status sink.

        Args:
            phase: Optional new phase.
            play_seconds: Optional updated counter for the current cycle.
            bump_refresh: If ``True``, increments refresh counter by 1 relative to
                the previous state known by the UI (stateless emit increments).
            last_error: Optional error message.
        """
        import queue as _q

        try:
            st = WorkerState(wid=self.wid, heartbeat_ts=time.monotonic())
            if phase is not None:
                st.phase = phase
            if play_seconds is not None:
                st.play_seconds = play_seconds
            if bump_refresh:
                st.refreshes = 1  # UI/controller will accumulate deltas per wid
            if last_error:
                st.last_error = last_error
            self.status_sink.put(st, block=False)
        except _q.Full:
            # best-effort; drop update to avoid blocking worker
            pass
