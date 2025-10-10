"""
Universal URL Handler for yt_streams

This module provides generalized URL handling for any website,
not just YouTube, with support for proxy chains and various protocols.
"""

import re
import urllib.parse
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class URLType(Enum):
    """Supported URL types"""
    YOUTUBE = "youtube"
    TWITCH = "twitch"
    VIMEO = "vimeo"
    DAILYMOTION = "dailymotion"
    GENERIC = "generic"
    UNKNOWN = "unknown"

@dataclass
class ProxyConfig:
    """Proxy configuration for requests"""
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    protocol: str = "http"  # http, https, socks4, socks5
    
    def to_url(self) -> str:
        """Convert proxy config to URL format"""
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.protocol}://{self.host}:{self.port}"

@dataclass
class ProxyChain:
    """Chain of proxies for rotation"""
    proxies: List[ProxyConfig]
    current_index: int = 0
    
    def get_next_proxy(self) -> ProxyConfig:
        """Get next proxy in rotation"""
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy
    
    def add_proxy(self, proxy: ProxyConfig) -> None:
        """Add a proxy to the chain"""
        self.proxies.append(proxy)
    
    def remove_proxy(self, index: int) -> None:
        """Remove a proxy from the chain"""
        if 0 <= index < len(self.proxies):
            del self.proxies[index]
            if self.current_index >= len(self.proxies):
                self.current_index = 0

class URLHandler:
    """Universal URL handler for any website"""
    
    # URL patterns for different platforms
    URL_PATTERNS = {
        URLType.YOUTUBE: [
            r'https?://(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
            r'https?://(?:www\.)?youtu\.be/([a-zA-Z0-9_-]+)',
            r'https?://(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]+)',
        ],
        URLType.TWITCH: [
            r'https?://(?:www\.)?twitch\.tv/([a-zA-Z0-9_]+)',
            r'https?://(?:www\.)?twitch\.tv/videos/(\d+)',
        ],
        URLType.VIMEO: [
            r'https?://(?:www\.)?vimeo\.com/(\d+)',
            r'https?://(?:www\.)?vimeo\.com/channels/[^/]+/(\d+)',
        ],
        URLType.DAILYMOTION: [
            r'https?://(?:www\.)?dailymotion\.com/video/([a-zA-Z0-9]+)',
        ],
    }
    
    def __init__(self, proxy_chain: Optional[ProxyChain] = None):
        self.proxy_chain = proxy_chain or ProxyChain([])
    
    def detect_url_type(self, url: str) -> URLType:
        """Detect the type of URL"""
        for url_type, patterns in self.URL_PATTERNS.items():
            for pattern in patterns:
                if re.match(pattern, url):
                    return url_type
        return URLType.GENERIC
    
    def validate_url(self, url: str) -> Tuple[bool, str]:
        """Validate URL format and accessibility"""
        try:
            parsed = urllib.parse.urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False, "Invalid URL format"
            
            # Check if it's a supported protocol
            if parsed.scheme not in ['http', 'https']:
                return False, f"Unsupported protocol: {parsed.scheme}"
            
            return True, "Valid URL"
        except Exception as e:
            return False, f"URL validation error: {e}"
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from URL"""
        url_type = self.detect_url_type(url)
        
        for pattern in self.URL_PATTERNS.get(url_type, []):
            match = re.match(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def normalize_url(self, url: str) -> str:
        """Normalize URL to standard format"""
        parsed = urllib.parse.urlparse(url)
        
        # Ensure https scheme
        if parsed.scheme == 'http':
            parsed = parsed._replace(scheme='https')
        
        # Remove tracking parameters
        query_params = urllib.parse.parse_qs(parsed.query)
        clean_params = {}
        
        # Keep only essential parameters
        essential_params = ['v', 't', 'list', 'index']
        for param in essential_params:
            if param in query_params:
                clean_params[param] = query_params[param]
        
        # Rebuild query string
        if clean_params:
            query_string = urllib.parse.urlencode(clean_params, doseq=True)
            parsed = parsed._replace(query=query_string)
        else:
            parsed = parsed._replace(query='')
        
        return urllib.parse.urlunparse(parsed)
    
    def get_platform_config(self, url_type: URLType) -> Dict[str, any]:
        """Get platform-specific configuration"""
        configs = {
            URLType.YOUTUBE: {
                'play_button_selectors': [
                    'button[aria-label*="Play"]',
                    '.ytp-play-button',
                    '#play-button',
                    'button[title*="Play"]'
                ],
                'video_selectors': [
                    'video',
                    '.html5-video-player video',
                    '#movie_player video'
                ],
                'stealth_required': True,
                'user_agent_rotation': True,
                'viewport_randomization': True,
            },
            URLType.TWITCH: {
                'play_button_selectors': [
                    '[data-a-target="player-play-pause-button"]',
                    '.player-controls__play-button',
                    'button[aria-label*="Play"]'
                ],
                'video_selectors': [
                    'video',
                    '.player-video video'
                ],
                'stealth_required': False,
                'user_agent_rotation': True,
                'viewport_randomization': False,
            },
            URLType.VIMEO: {
                'play_button_selectors': [
                    '.vp-play',
                    '.vp-play-button',
                    'button[aria-label*="Play"]'
                ],
                'video_selectors': [
                    'video',
                    '.vp-video video'
                ],
                'stealth_required': False,
                'user_agent_rotation': False,
                'viewport_randomization': False,
            },
            URLType.GENERIC: {
                'play_button_selectors': [
                    'button[aria-label*="Play"]',
                    '.play-button',
                    '#play',
                    'button[title*="Play"]',
                    '[data-testid*="play"]'
                ],
                'video_selectors': [
                    'video',
                    'iframe[src*="youtube"]',
                    'iframe[src*="vimeo"]'
                ],
                'stealth_required': True,
                'user_agent_rotation': True,
                'viewport_randomization': True,
            }
        }
        
        return configs.get(url_type, configs[URLType.GENERIC])
    
    def get_next_proxy(self) -> Optional[ProxyConfig]:
        """Get next proxy from chain"""
        if not self.proxy_chain.proxies:
            return None
        return self.proxy_chain.get_next_proxy()
    
    def create_proxy_chain_from_list(self, proxy_list: List[str]) -> ProxyChain:
        """Create proxy chain from list of proxy URLs"""
        chain = ProxyChain([])
        
        for proxy_url in proxy_list:
            try:
                parsed = urllib.parse.urlparse(proxy_url)
                config = ProxyConfig(
                    host=parsed.hostname,
                    port=parsed.port or 8080,
                    username=parsed.username,
                    password=parsed.password,
                    protocol=parsed.scheme or 'http'
                )
                chain.add_proxy(config)
            except Exception as e:
                logger.warning(f"Failed to parse proxy URL {proxy_url}: {e}")
        
        return chain
    
    def get_stealth_config(self, url: str) -> Dict[str, any]:
        """Get stealth configuration based on URL type"""
        url_type = self.detect_url_type(url)
        platform_config = self.get_platform_config(url_type)
        
        return {
            'stealth_required': platform_config['stealth_required'],
            'user_agent_rotation': platform_config['user_agent_rotation'],
            'viewport_randomization': platform_config['viewport_randomization'],
            'play_button_selectors': platform_config['play_button_selectors'],
            'video_selectors': platform_config['video_selectors'],
            'url_type': url_type.value,
        }

# Global URL handler instance
url_handler = URLHandler()

def detect_url_type(url: str) -> URLType:
    """Detect URL type"""
    return url_handler.detect_url_type(url)

def validate_url(url: str) -> Tuple[bool, str]:
    """Validate URL"""
    return url_handler.validate_url(url)

def get_stealth_config(url: str) -> Dict[str, any]:
    """Get stealth configuration for URL"""
    return url_handler.get_stealth_config(url)

def create_proxy_chain(proxy_list: List[str]) -> ProxyChain:
    """Create proxy chain from list"""
    return url_handler.create_proxy_chain_from_list(proxy_list)
