"""Robots.txt compliance and configuration management for yt_streams.

Purpose:
    Provide robots.txt compliance checking and comprehensive configuration
    management for stealth web scraping operations.

Features:
    - Robots.txt parsing and compliance checking
    - Crawl delay enforcement
    - User agent management
    - Configuration file support
    - Environment variable integration
"""

from __future__ import annotations

import asyncio
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import aiofiles
from pydantic import BaseModel, Field


class RobotsConfig(BaseModel):
    """Configuration for robots.txt compliance."""
    
    respect_robots: bool = Field(True, description="Whether to respect robots.txt")
    user_agent: str = Field("yt-streams-bot", description="User agent for robots.txt checking")
    crawl_delay: float = Field(1.0, description="Default crawl delay in seconds")
    max_crawl_delay: float = Field(10.0, description="Maximum crawl delay to enforce")
    cache_robots: bool = Field(True, description="Cache robots.txt files")
    cache_ttl: int = Field(3600, description="Cache TTL in seconds")


class StealthConfig(BaseModel):
    """Comprehensive stealth configuration."""
    
    # Browser settings
    headless: bool = Field(False, description="Run browser in headless mode")
    stealth_mode: bool = Field(True, description="Enable stealth mode")
    random_user_agent: bool = Field(True, description="Use random user agents")
    random_viewport: bool = Field(True, description="Randomize viewport size")
    
    # Timing settings
    min_delay: float = Field(1.0, description="Minimum delay between requests")
    max_delay: float = Field(3.0, description="Maximum delay between requests")
    human_like_delays: bool = Field(True, description="Use human-like delays")
    
    # Proxy settings
    proxy: Optional[str] = Field(None, description="Proxy URL")
    proxy_rotation: bool = Field(False, description="Rotate proxies")
    proxy_list: List[str] = Field(default_factory=list, description="List of proxy URLs")
    
    # Advanced settings
    disable_images: bool = Field(False, description="Disable image loading")
    disable_css: bool = Field(False, description="Disable CSS loading")
    disable_js: bool = Field(False, description="Disable JavaScript")
    block_ads: bool = Field(True, description="Block advertisements")
    
    # Fingerprint evasion
    randomize_fingerprint: bool = Field(True, description="Randomize browser fingerprint")
    mock_webgl: bool = Field(True, description="Mock WebGL fingerprint")
    mock_canvas: bool = Field(True, description="Mock canvas fingerprint")
    mock_audio: bool = Field(True, description="Mock audio fingerprint")
    
    # Behavior simulation
    simulate_mouse_movement: bool = Field(True, description="Simulate mouse movements")
    simulate_scrolling: bool = Field(True, description="Simulate scrolling")
    simulate_typing: bool = Field(False, description="Simulate typing")
    random_interactions: bool = Field(True, description="Random user interactions")


class RobotsChecker:
    """Robots.txt compliance checker with caching."""
    
    def __init__(self, config: RobotsConfig):
        self.config = config
        self._cache: Dict[str, tuple[RobotFileParser, float]] = {}
    
    def _get_robots_url(self, url: str) -> str:
        """Get the robots.txt URL for a given URL."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    
    def _is_cache_valid(self, robots_url: str) -> bool:
        """Check if cached robots.txt is still valid."""
        if not self.config.cache_robots:
            return False
        
        if robots_url not in self._cache:
            return False
        
        _, timestamp = self._cache[robots_url]
        return time.time() - timestamp < self.config.cache_ttl
    
    def _get_robot_parser(self, url: str) -> Optional[RobotFileParser]:
        """Get or fetch robots.txt parser for a URL."""
        robots_url = self._get_robots_url(url)
        
        # Check cache first
        if self._is_cache_valid(robots_url):
            return self._cache[robots_url][0]
        
        # Fetch robots.txt
        try:
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            
            # Cache the result
            if self.config.cache_robots:
                self._cache[robots_url] = (rp, time.time())
            
            return rp
        except Exception:
            # If robots.txt can't be fetched, assume it's allowed
            return None
    
    def can_fetch(self, url: str, user_agent: Optional[str] = None) -> bool:
        """Check if a URL can be fetched according to robots.txt."""
        if not self.config.respect_robots:
            return True
        
        user_agent = user_agent or self.config.user_agent
        rp = self._get_robot_parser(url)
        
        if rp is None:
            return True  # Assume allowed if robots.txt can't be fetched
        
        return rp.can_fetch(user_agent, url)
    
    def get_crawl_delay(self, url: str, user_agent: Optional[str] = None) -> float:
        """Get the crawl delay for a URL according to robots.txt."""
        if not self.config.respect_robots:
            return self.config.crawl_delay
        
        user_agent = user_agent or self.config.user_agent
        rp = self._get_robot_parser(url)
        
        if rp is None:
            return self.config.crawl_delay
        
        # Get crawl delay from robots.txt
        delay = rp.crawl_delay(user_agent)
        if delay is None:
            delay = self.config.crawl_delay
        
        # Enforce maximum delay
        return min(delay, self.config.max_crawl_delay)
    
    def get_sitemap_urls(self, url: str) -> List[str]:
        """Get sitemap URLs from robots.txt."""
        rp = self._get_robot_parser(url)
        if rp is None:
            return []
        
        return rp.site_maps()


class ConfigManager:
    """Configuration manager for yt_streams."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path("data/yt_streams/config")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.robots_config_file = self.config_dir / "robots.json"
        self.stealth_config_file = self.config_dir / "stealth.json"
        
        self.robots_config = self._load_robots_config()
        self.stealth_config = self._load_stealth_config()
        
        self.robots_checker = RobotsChecker(self.robots_config)
    
    def _load_robots_config(self) -> RobotsConfig:
        """Load robots configuration from file or create default."""
        if self.robots_config_file.exists():
            try:
                import json
                with open(self.robots_config_file) as f:
                    data = json.load(f)
                return RobotsConfig(**data)
            except Exception:
                pass
        
        # Create default config
        config = RobotsConfig()
        self._save_robots_config(config)
        return config
    
    def _save_robots_config(self, config: RobotsConfig) -> None:
        """Save robots configuration to file."""
        import json
        with open(self.config_dir / "robots.json", "w") as f:
            json.dump(config.model_dump(), f, indent=2)
    
    def _load_stealth_config(self) -> StealthConfig:
        """Load stealth configuration from file or create default."""
        if self.stealth_config_file.exists():
            try:
                import json
                with open(self.stealth_config_file) as f:
                    data = json.load(f)
                return StealthConfig(**data)
            except Exception:
                pass
        
        # Create default config
        config = StealthConfig()
        self._save_stealth_config(config)
        return config
    
    def _save_stealth_config(self, config: StealthConfig) -> None:
        """Save stealth configuration to file."""
        import json
        with open(self.config_dir / "stealth.json", "w") as f:
            json.dump(config.model_dump(), f, indent=2)
    
    def update_robots_config(self, **kwargs) -> None:
        """Update robots configuration."""
        for key, value in kwargs.items():
            if hasattr(self.robots_config, key):
                setattr(self.robots_config, key, value)
        self._save_robots_config(self.robots_config)
        self.robots_checker = RobotsChecker(self.robots_config)
    
    def update_stealth_config(self, **kwargs) -> None:
        """Update stealth configuration."""
        for key, value in kwargs.items():
            if hasattr(self.stealth_config, key):
                setattr(self.stealth_config, key, value)
        self._save_stealth_config(self.stealth_config)
    
    def can_fetch_url(self, url: str, user_agent: Optional[str] = None) -> bool:
        """Check if a URL can be fetched according to robots.txt."""
        return self.robots_checker.can_fetch(url, user_agent)
    
    def get_crawl_delay(self, url: str, user_agent: Optional[str] = None) -> float:
        """Get crawl delay for a URL."""
        return self.robots_checker.get_crawl_delay(url, user_agent)
    
    async def wait_for_crawl_delay(self, url: str, user_agent: Optional[str] = None) -> None:
        """Wait for the appropriate crawl delay."""
        delay = self.get_crawl_delay(url, user_agent)
        
        # Add some randomization to avoid predictable patterns
        if self.stealth_config.human_like_delays:
            delay *= (0.8 + 0.4 * (time.time() % 1))  # ±20% variation
        
        await asyncio.sleep(delay)


# Global configuration manager instance
config_manager = ConfigManager()


# Convenience functions
def can_fetch_url(url: str, user_agent: Optional[str] = None) -> bool:
    """Check if a URL can be fetched according to robots.txt."""
    return config_manager.can_fetch_url(url, user_agent)


def get_crawl_delay(url: str, user_agent: Optional[str] = None) -> float:
    """Get crawl delay for a URL."""
    return config_manager.get_crawl_delay(url, user_agent)


async def wait_for_crawl_delay(url: str, user_agent: Optional[str] = None) -> None:
    """Wait for the appropriate crawl delay."""
    await config_manager.wait_for_crawl_delay(url, user_agent)


def update_stealth_config(**kwargs) -> None:
    """Update stealth configuration."""
    config_manager.update_stealth_config(**kwargs)


def update_robots_config(**kwargs) -> None:
    """Update robots configuration."""
    config_manager.update_robots_config(**kwargs)
