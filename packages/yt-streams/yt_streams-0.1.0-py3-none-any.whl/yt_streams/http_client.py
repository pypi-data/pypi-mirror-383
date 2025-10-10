"""HTTP client utilities with anti-detection measures for yt_streams.

Purpose:
    Provide stealth HTTP clients that can make requests without being detected
    as automated traffic. Includes support for httpx, curl-cffi, and other
    anti-detection techniques.

Features:
    - User agent rotation
    - Proxy support
    - TLS fingerprint randomization
    - Request header randomization
    - Cookie management
    - Rate limiting
"""

from __future__ import annotations

import asyncio
import random
import time
from typing import Any, Dict, Optional

import httpx
from fake_useragent import UserAgent

try:
    from curl_cffi import requests as curl_requests
    from curl_cffi.requests import Session as CurlSession
    CURL_AVAILABLE = True
except ImportError:
    CURL_AVAILABLE = False
    CurlSession = None


class StealthHTTPClient:
    """HTTP client with anti-detection measures."""
    
    def __init__(
        self,
        user_agent: Optional[str] = None,
        proxy: Optional[str] = None,
        use_curl: bool = True,
        randomize_headers: bool = True,
    ):
        self.user_agent = user_agent or self._get_random_user_agent()
        self.proxy = proxy
        self.use_curl = use_curl and CURL_AVAILABLE
        self.randomize_headers = randomize_headers
        
        # Initialize clients
        self._httpx_client: Optional[httpx.AsyncClient] = None
        self._curl_session: Optional[CurlSession] = None
        
    def _get_random_user_agent(self) -> str:
        """Get a random user agent."""
        try:
            ua = UserAgent()
            return ua.chrome
        except Exception:
            # Fallback user agents
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            ]
            return random.choice(user_agents)
    
    def _get_random_headers(self) -> Dict[str, str]:
        """Get randomized headers to avoid detection."""
        base_headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
        }
        
        if self.randomize_headers:
            # Randomly add/remove some headers
            if random.random() < 0.5:
                base_headers["Sec-Ch-Ua"] = '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"'
                base_headers["Sec-Ch-Ua-Mobile"] = "?0"
                base_headers["Sec-Ch-Ua-Platform"] = '"Windows"'
            
            # Randomly vary Accept-Language
            languages = [
                "en-US,en;q=0.9",
                "en-US,en;q=0.9,es;q=0.8",
                "en-US,en;q=0.9,fr;q=0.8",
                "en-GB,en;q=0.9,en-US;q=0.8",
            ]
            base_headers["Accept-Language"] = random.choice(languages)
        
        return base_headers
    
    async def _get_httpx_client(self) -> httpx.AsyncClient:
        """Get or create httpx client."""
        if self._httpx_client is None:
            limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
            timeout = httpx.Timeout(30.0)
            
            client_kwargs = {
                "limits": limits,
                "timeout": timeout,
                "headers": self._get_random_headers(),
            }
            
            if self.proxy:
                client_kwargs["proxies"] = self.proxy
            
            self._httpx_client = httpx.AsyncClient(**client_kwargs)
        
        return self._httpx_client
    
    def _get_curl_session(self) -> CurlSession:
        """Get or create curl-cffi session."""
        if self._curl_session is None and CURL_AVAILABLE:
            self._curl_session = CurlSession(
                impersonate="chrome120",  # Impersonate Chrome 120
                headers=self._get_random_headers(),
                proxies=self.proxy,
                timeout=30,
            )
        return self._curl_session
    
    async def get(self, url: str, **kwargs) -> httpx.Response:
        """Make a GET request with stealth measures."""
        # Random delay to avoid rate limiting
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        if self.use_curl and CURL_AVAILABLE:
            # Use curl-cffi for better fingerprint evasion
            session = self._get_curl_session()
            if session:
                response = session.get(url, **kwargs)
                # Convert to httpx-like response
                return httpx.Response(
                    status_code=response.status_code,
                    headers=response.headers,
                    content=response.content,
                    request=httpx.Request("GET", url),
                )
        
        # Fallback to httpx
        client = await self._get_httpx_client()
        return await client.get(url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> httpx.Response:
        """Make a POST request with stealth measures."""
        # Random delay to avoid rate limiting
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        if self.use_curl and CURL_AVAILABLE:
            # Use curl-cffi for better fingerprint evasion
            session = self._get_curl_session()
            if session:
                response = session.post(url, **kwargs)
                # Convert to httpx-like response
                return httpx.Response(
                    status_code=response.status_code,
                    headers=response.headers,
                    content=response.content,
                    request=httpx.Request("POST", url),
                )
        
        # Fallback to httpx
        client = await self._get_httpx_client()
        return await client.post(url, **kwargs)
    
    async def close(self):
        """Close all clients."""
        if self._httpx_client:
            await self._httpx_client.aclose()
            self._httpx_client = None
        
        if self._curl_session:
            self._curl_session.close()
            self._curl_session = None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# Convenience function for quick requests
async def stealth_request(
    method: str,
    url: str,
    user_agent: Optional[str] = None,
    proxy: Optional[str] = None,
    **kwargs
) -> httpx.Response:
    """Make a stealth HTTP request."""
    async with StealthHTTPClient(user_agent=user_agent, proxy=proxy) as client:
        if method.upper() == "GET":
            return await client.get(url, **kwargs)
        elif method.upper() == "POST":
            return await client.post(url, **kwargs)
        else:
            raise ValueError(f"Unsupported method: {method}")


# Rate limiter for requests
class RateLimiter:
    """Simple rate limiter for HTTP requests."""
    
    def __init__(self, requests_per_second: float = 1.0):
        self.requests_per_second = requests_per_second
        self.last_request_time = 0.0
    
    async def wait(self):
        """Wait if necessary to respect rate limit."""
        now = time.time()
        time_since_last = now - self.last_request_time
        min_interval = 1.0 / self.requests_per_second
        
        if time_since_last < min_interval:
            await asyncio.sleep(min_interval - time_since_last)
        
        self.last_request_time = time.time()
