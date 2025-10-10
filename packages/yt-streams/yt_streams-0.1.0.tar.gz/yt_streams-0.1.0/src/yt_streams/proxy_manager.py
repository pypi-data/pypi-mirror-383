"""
Proxy Management System for yt_streams

This module provides comprehensive proxy management including:
- Proxy chain rotation
- Proxy health checking
- Automatic failover
- Proxy performance monitoring
"""

import asyncio
import json
import time
import random
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import httpx
from urllib.parse import urlparse

from .url_handler import ProxyConfig, ProxyChain

logger = logging.getLogger(__name__)

@dataclass
class ProxyHealth:
    """Proxy health status"""
    proxy: ProxyConfig
    is_healthy: bool
    response_time: float
    last_check: float
    failure_count: int = 0
    success_count: int = 0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0

@dataclass
class ProxyStats:
    """Proxy usage statistics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    last_used: float = 0.0

class ProxyManager:
    """Advanced proxy management system"""
    
    def __init__(self, config_file: Optional[Path] = None):
        self.config_file = config_file or Path("proxy_config.json")
        self.proxy_chain = ProxyChain([])
        self.health_status: Dict[str, ProxyHealth] = {}
        self.stats: Dict[str, ProxyStats] = {}
        self.test_urls = [
            "https://httpbin.org/ip",
            "https://api.ipify.org?format=json",
            "https://ipinfo.io/json"
        ]
        self.health_check_interval = 300  # 5 minutes
        self.max_failures = 3
        self.timeout = 10.0
        
        self.load_config()
    
    def load_config(self) -> None:
        """Load proxy configuration from file"""
        if not self.config_file.exists():
            self.create_default_config()
            return
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            # Load proxy chain
            if 'proxy_chain' in config:
                for proxy_data in config['proxy_chain']:
                    proxy = ProxyConfig(**proxy_data)
                    self.proxy_chain.add_proxy(proxy)
            
            # Load settings
            self.health_check_interval = config.get('health_check_interval', 300)
            self.max_failures = config.get('max_failures', 3)
            self.timeout = config.get('timeout', 10.0)
            
            logger.info(f"Loaded {len(self.proxy_chain.proxies)} proxies from config")
            
        except Exception as e:
            logger.error(f"Failed to load proxy config: {e}")
            self.create_default_config()
    
    def save_config(self) -> None:
        """Save proxy configuration to file"""
        config = {
            'enabled': len(self.proxy_chain.proxies) > 0,
            'proxy_chain': [asdict(proxy) for proxy in self.proxy_chain.proxies],
            'health_check_interval': self.health_check_interval,
            'max_failures': self.max_failures,
            'timeout': self.timeout,
            'test_urls': self.test_urls
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info("Proxy configuration saved")
        except Exception as e:
            logger.error(f"Failed to save proxy config: {e}")
    
    def create_default_config(self) -> None:
        """Create default proxy configuration"""
        config = {
            'enabled': False,
            'proxy_chain': [],
            'health_check_interval': 300,
            'max_failures': 3,
            'timeout': 10.0,
            'test_urls': self.test_urls
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info("Created default proxy configuration")
    
    def add_proxy(self, proxy: ProxyConfig) -> None:
        """Add a proxy to the chain"""
        self.proxy_chain.add_proxy(proxy)
        proxy_key = f"{proxy.host}:{proxy.port}"
        self.health_status[proxy_key] = ProxyHealth(
            proxy=proxy,
            is_healthy=True,
            response_time=0.0,
            last_check=0.0
        )
        self.stats[proxy_key] = ProxyStats()
        self.save_config()
        logger.info(f"Added proxy: {proxy_key}")
    
    def remove_proxy(self, index: int) -> None:
        """Remove a proxy from the chain"""
        if 0 <= index < len(self.proxy_chain.proxies):
            proxy = self.proxy_chain.proxies[index]
            proxy_key = f"{proxy.host}:{proxy.port}"
            
            self.proxy_chain.remove_proxy(index)
            self.health_status.pop(proxy_key, None)
            self.stats.pop(proxy_key, None)
            self.save_config()
            logger.info(f"Removed proxy: {proxy_key}")
    
    async def check_proxy_health(self, proxy: ProxyConfig) -> ProxyHealth:
        """Check health of a single proxy"""
        proxy_key = f"{proxy.host}:{proxy.port}"
        start_time = time.time()
        
        try:
            # Test with a simple HTTP request
            test_url = random.choice(self.test_urls)
            proxy_url = proxy.to_url()
            
            async with httpx.AsyncClient(
                proxies=proxy_url,
                timeout=self.timeout,
                follow_redirects=True
            ) as client:
                response = await client.get(test_url)
                response.raise_for_status()
                
                response_time = time.time() - start_time
                
                # Update health status
                if proxy_key in self.health_status:
                    health = self.health_status[proxy_key]
                    health.is_healthy = True
                    health.response_time = response_time
                    health.last_check = time.time()
                    health.success_count += 1
                else:
                    health = ProxyHealth(
                        proxy=proxy,
                        is_healthy=True,
                        response_time=response_time,
                        last_check=time.time(),
                        success_count=1
                    )
                    self.health_status[proxy_key] = health
                
                logger.debug(f"Proxy {proxy_key} is healthy (response time: {response_time:.2f}s)")
                return health
                
        except Exception as e:
            response_time = time.time() - start_time
            
            # Update health status
            if proxy_key in self.health_status:
                health = self.health_status[proxy_key]
                health.is_healthy = False
                health.response_time = response_time
                health.last_check = time.time()
                health.failure_count += 1
            else:
                health = ProxyHealth(
                    proxy=proxy,
                    is_healthy=False,
                    response_time=response_time,
                    last_check=time.time(),
                    failure_count=1
                )
                self.health_status[proxy_key] = health
            
            logger.warning(f"Proxy {proxy_key} is unhealthy: {e}")
            return health
    
    async def check_all_proxies(self) -> Dict[str, ProxyHealth]:
        """Check health of all proxies"""
        if not self.proxy_chain.proxies:
            return {}
        
        tasks = [self.check_proxy_health(proxy) for proxy in self.proxy_chain.proxies]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        healthy_proxies = {}
        for result in results:
            if isinstance(result, ProxyHealth):
                proxy_key = f"{result.proxy.host}:{result.proxy.port}"
                healthy_proxies[proxy_key] = result
        
        return healthy_proxies
    
    def get_healthy_proxy(self) -> Optional[ProxyConfig]:
        """Get a healthy proxy from the chain"""
        if not self.proxy_chain.proxies:
            return None
        
        # Filter healthy proxies
        healthy_proxies = [
            proxy for proxy in self.proxy_chain.proxies
            if self.is_proxy_healthy(proxy)
        ]
        
        if not healthy_proxies:
            logger.warning("No healthy proxies available")
            return None
        
        # Return proxy with best performance
        best_proxy = min(healthy_proxies, key=lambda p: self.get_proxy_response_time(p))
        return best_proxy
    
    def is_proxy_healthy(self, proxy: ProxyConfig) -> bool:
        """Check if a proxy is considered healthy"""
        proxy_key = f"{proxy.host}:{proxy.port}"
        
        if proxy_key not in self.health_status:
            return True  # Assume healthy if not checked yet
        
        health = self.health_status[proxy_key]
        
        # Check if proxy has too many failures
        if health.failure_count >= self.max_failures:
            return False
        
        # Check if health check is too old
        if time.time() - health.last_check > self.health_check_interval:
            return True  # Assume healthy if not checked recently
        
        return health.is_healthy
    
    def get_proxy_response_time(self, proxy: ProxyConfig) -> float:
        """Get average response time for a proxy"""
        proxy_key = f"{proxy.host}:{proxy.port}"
        
        if proxy_key in self.health_status:
            return self.health_status[proxy_key].response_time
        
        return float('inf')
    
    def update_proxy_stats(self, proxy: ProxyConfig, success: bool, response_time: float) -> None:
        """Update proxy usage statistics"""
        proxy_key = f"{proxy.host}:{proxy.port}"
        
        if proxy_key not in self.stats:
            self.stats[proxy_key] = ProxyStats()
        
        stats = self.stats[proxy_key]
        stats.total_requests += 1
        stats.last_used = time.time()
        
        if success:
            stats.successful_requests += 1
        else:
            stats.failed_requests += 1
        
        # Update average response time
        if stats.total_requests == 1:
            stats.average_response_time = response_time
        else:
            stats.average_response_time = (
                (stats.average_response_time * (stats.total_requests - 1) + response_time) 
                / stats.total_requests
            )
    
    def get_proxy_stats(self) -> Dict[str, ProxyStats]:
        """Get statistics for all proxies"""
        return self.stats.copy()
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary for all proxies"""
        summary = {
            'total_proxies': len(self.proxy_chain.proxies),
            'healthy_proxies': 0,
            'unhealthy_proxies': 0,
            'average_response_time': 0.0,
            'proxy_details': {}
        }
        
        total_response_time = 0.0
        healthy_count = 0
        
        for proxy in self.proxy_chain.proxies:
            proxy_key = f"{proxy.host}:{proxy.port}"
            is_healthy = self.is_proxy_healthy(proxy)
            
            if is_healthy:
                summary['healthy_proxies'] += 1
                healthy_count += 1
                response_time = self.get_proxy_response_time(proxy)
                total_response_time += response_time
            else:
                summary['unhealthy_proxies'] += 1
            
            summary['proxy_details'][proxy_key] = {
                'healthy': is_healthy,
                'response_time': self.get_proxy_response_time(proxy),
                'stats': self.stats.get(proxy_key, ProxyStats())
            }
        
        if healthy_count > 0:
            summary['average_response_time'] = total_response_time / healthy_count
        
        return summary
    
    async def start_health_monitoring(self) -> None:
        """Start background health monitoring"""
        logger.info("Starting proxy health monitoring")
        
        while True:
            try:
                await self.check_all_proxies()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying

# Global proxy manager instance
proxy_manager = ProxyManager()

def get_proxy_manager() -> ProxyManager:
    """Get global proxy manager instance"""
    return proxy_manager

def add_proxy(host: str, port: int, username: Optional[str] = None, 
              password: Optional[str] = None, protocol: str = "http") -> None:
    """Add a proxy to the global manager"""
    proxy = ProxyConfig(host=host, port=port, username=username, 
                       password=password, protocol=protocol)
    proxy_manager.add_proxy(proxy)

def get_healthy_proxy() -> Optional[ProxyConfig]:
    """Get a healthy proxy from the global manager"""
    return proxy_manager.get_healthy_proxy()

def get_proxy_stats() -> Dict[str, ProxyStats]:
    """Get proxy statistics from the global manager"""
    return proxy_manager.get_proxy_stats()
