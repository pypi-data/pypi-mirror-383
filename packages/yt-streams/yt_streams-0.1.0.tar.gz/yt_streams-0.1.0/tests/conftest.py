"""
Pytest configuration and fixtures for yt_streams tests
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
from typing import Generator

@pytest.fixture
def temp_data_dir() -> Generator[Path, None, None]:
    """Create a temporary data directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def sample_youtube_url() -> str:
    """Sample YouTube URL for testing"""
    return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

@pytest.fixture
def sample_twitch_url() -> str:
    """Sample Twitch URL for testing"""
    return "https://www.twitch.tv/ninja"

@pytest.fixture
def sample_vimeo_url() -> str:
    """Sample Vimeo URL for testing"""
    return "https://vimeo.com/123456789"
