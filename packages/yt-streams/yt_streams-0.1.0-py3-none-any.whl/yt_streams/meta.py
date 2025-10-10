"""YouTube metadata service for :mod:`yt_streams` built on :mod:`yt_dlp`.

Purpose:
    Provide a small, dependency-isolated wrapper that resolves a YouTube URL
    (watch/shorts/share) to a normalized :class:`~yt_streams.models.VideoInfo`.
    The service never downloads media; it only extracts metadata.

Design:
    - Uses ``yt_dlp.YoutubeDL`` with ``download=False`` and quiet flags.
    - Accepts playlist/shorts URLs and normalizes to the first entry if needed.
    - Returns a compact :class:`~yt_streams.models.VideoInfo` for caching and UI.
    - No I/O beyond yt-dlp's network fetch; no global state or side effects.

Attributes:
    DEFAULT_OPTS (dict[str, object]): Baseline options passed to yt-dlp.

Examples:
    Basic usage::

        >>> from yt_streams.meta import YtInfoService
        >>> svc = YtInfoService()
        >>> isinstance(svc, YtInfoService)
        True

    Resolving a URL (networked; doctest skipped)::

        >>> info = svc.extract("https://www.youtube.com/watch?v=dQw4w9WgXcQ")  # doctest: +SKIP
        >>> (info.id, bool(info.title))  # doctest: +SKIP
        ('dQw4w9WgXcQ', True)
"""
from __future__ import annotations

from typing import Any, Final

import yt_dlp

from .models import VideoInfo

DEFAULT_OPTS: Final[dict[str, object]] = {
    "quiet": True,
    "no_warnings": True,
    "skip_download": True,
}


class YtInfoService:
    """Thin wrapper around :mod:`yt_dlp` for metadata extraction only.

    Args:
        opts: Optional dict merged into :data:`DEFAULT_OPTS` for ``YoutubeDL``.

    Raises:
        RuntimeError: If the URL can't be resolved to a video id.

    Examples:
        ::
            >>> YtInfoService()._opts["quiet"]  # internal, for illustration
            True
    """

    def __init__(self, *, opts: dict[str, object] | None = None) -> None:
        merged = dict(DEFAULT_OPTS)
        if opts:
            merged.update(opts)
        # store for inspection/testing; YoutubeDL object is built lazily per call
        self._opts: dict[str, object] = merged

    def extract(self, url: str) -> VideoInfo:
        """Extract and normalize metadata for ``url``.

        Args:
            url: A YouTube watch/shorts/playlist entry URL.

        Returns:
            :class:`~yt_streams.models.VideoInfo` with id/title/duration/url.

        Raises:
            RuntimeError: If extraction fails or no video id is present.

        Examples:
            ::
                >>> svc = YtInfoService()
                >>> isinstance(svc.extract, object)
                True
        """
        ydl = yt_dlp.YoutubeDL(self._opts)  # type: ignore[no-untyped-call]
        data: dict[str, Any] = ydl.extract_info(url, download=False)  # type: ignore[no-untyped-call]
        # If a playlist-like structure is returned, take the first entry
        if data.get("_type") == "playlist" and data.get("entries"):
            first = data["entries"][0]
            if isinstance(first, dict):
                data = first  # type: ignore[assignment]
        vid = str(data.get("id") or "")
        if not vid:
            raise RuntimeError("No video id found for URL")
        return VideoInfo(
            id=vid,
            title=str(data.get("title") or ""),
            duration=int(data["duration"]) if data.get("duration") else None,
            url=f"https://www.youtube.com/watch?v={vid}",
        )
