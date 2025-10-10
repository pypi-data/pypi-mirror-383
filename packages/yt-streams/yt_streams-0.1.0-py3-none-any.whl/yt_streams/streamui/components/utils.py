"""UI utilities: default URL & recent URLs persistence for Streamlit components.

Purpose:
    Provide a tiny, file-backed layer to persist a single "default URL" and a
    rolling history of "recent URLs" under the current `data_dir`. Components
    use this to pre-populate inputs and offer convenient quick-picks.

Design:
    Files live under `<data_dir>/config/` and are append-only (for JSONL):
      - `default_url.txt` (single line; last write wins).
      - `recent_urls.jsonl` (append-only; records with ts,url,note).

    All helpers are synchronous and side-effect-free except on write.

Functions:
    ensure_config_dir
        Create `<data_dir>/config` if missing.
    load_default_url / save_default_url
        Get or set the default URL.
    record_recent_urls / load_recent_urls
        Append or read recent URLs (dedup + newest-first).
    pick_effective_default_url
        Resolve default from flag > env > file > None.

Notes:
    - The JSONL is deliberately simple for tail/grep friendliness.
    - We do not enforce a strict length; callers can pass `max_items`.

Examples:
    ::
        >>> from pathlib import Path  # doctest: +SKIP
        >>> root = Path("data/yt_streams")  # doctest: +SKIP
        >>> save_default_url(root, "https://youtu.be/xyz")  # doctest: +SKIP
        >>> load_default_url(root)  # doctest: +SKIP
        'https://youtu.be/xyz'
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Tuple
import json
import os
import time

CONFIG_DIR = "config"
DEFAULT_URL_FILE = "default_url.txt"
RECENT_URLS_FILE = "recent_urls.jsonl"


def ensure_config_dir(root: Path) -> Path:
    """Ensure `<root>/config` exists.

    Args:
        root: Data directory root.

    Returns:
        Path to the created/existing config directory.
    """
    p = root / CONFIG_DIR
    p.mkdir(parents=True, exist_ok=True)
    return p


def load_default_url(root: Path) -> str | None:
    """Load default URL from `<root>/config/default_url.txt` if present."""
    p = root / CONFIG_DIR / DEFAULT_URL_FILE
    if not p.exists():
        return None
    s = p.read_text(encoding="utf-8").strip()
    return s or None


def save_default_url(root: Path, url: str) -> None:
    """Persist the default URL to `<root>/config/default_url.txt`."""
    if not url:
        return
    ensure_config_dir(root).joinpath(DEFAULT_URL_FILE).write_text(url.strip() + "\n", encoding="utf-8")


def record_recent_urls(root: Path, urls: Iterable[str], note: str = "ui") -> None:
    """Append URLs to `<root>/config/recent_urls.jsonl` with a timestamp.

    Args:
        root: Data directory.
        urls: One or more URLs to record.
        note: Optional note for traceability (e.g., 'controls:pulse').
    """
    p = ensure_config_dir(root).joinpath(RECENT_URLS_FILE)
    ts = time.time()
    with p.open("a", encoding="utf-8") as f:
        for u in urls:
            u2 = (u or "").strip()
            if not u2:
                continue
            rec = {"ts": ts, "url": u2, "note": note}
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def load_recent_urls(root: Path, max_items: int = 20) -> list[str]:
    """Return newest-first unique recent URLs (best-effort).

    Args:
        root: Data directory root.
        max_items: Max URLs to return after de-duplication.

    Returns:
        List of URLs.
    """
    p = root / CONFIG_DIR / RECENT_URLS_FILE
    if not p.exists():
        return []
    out: list[str] = []
    seen: set[str] = set()
    try:
        lines = p.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []
    for s in reversed(lines):  # newest last → reverse → newest-first
        try:
            obj = json.loads(s)
        except Exception:
            continue
        u = str(obj.get("url") or "").strip()
        if not u or u in seen:
            continue
        out.append(u)
        seen.add(u)
        if len(out) >= max_items:
            break
    return out


def pick_effective_default_url(
    *,
    flag_url: str | None,
    data_dir: Path,
    env_var: str = "YT_STREAMS_DEFAULT_URL",
) -> str | None:
    """Resolve an effective default URL from flag > env > persisted file.

    Args:
        flag_url: URL from CLI flag or in-memory setting.
        data_dir: Data directory; used to read the persisted file.
        env_var: Name of env var to consider.

    Returns:
        URL string or ``None`` if nothing resolves.
    """
    if flag_url and flag_url.strip():
        return flag_url.strip()
    env = os.environ.get(env_var, "").strip()
    if env:
        return env
    return load_default_url(data_dir)
