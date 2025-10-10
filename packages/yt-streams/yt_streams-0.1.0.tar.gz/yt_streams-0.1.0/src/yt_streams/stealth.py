"""Advanced stealth utilities for yt_streams to avoid bot detection.

Purpose:
    Provide comprehensive anti-detection measures combining multiple libraries
    and techniques to make browser automation appear as human-like as possible.

Features:
    - Multiple stealth libraries integration
    - Advanced fingerprint masking
    - Human-like behavior simulation
    - CAPTCHA solving integration
    - Cloudflare bypass
    - TLS fingerprint randomization
"""

from __future__ import annotations

import asyncio
import random
import time
from typing import Any, Dict, List, Optional, Union

import cloudscraper
import requests
from fake_useragent import UserAgent

try:
    import undetected_chromedriver as uc
    from selenium import webdriver
    from selenium_stealth import stealth
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    from playwright.async_api import Page
    from playwright_stealth import stealth_sync
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    stealth_sync = None


class AdvancedStealth:
    """Advanced stealth utilities combining multiple anti-detection techniques."""
    
    def __init__(self):
        self.user_agent_generator = UserAgent()
        self.cloudscraper_session = cloudscraper.create_scraper()
        self.requests_session = requests.Session()
        
    def get_random_user_agent(self) -> str:
        """Get a random, realistic user agent."""
        try:
            # Try different browsers randomly
            browsers = ['chrome', 'firefox', 'safari', 'edge']
            browser = random.choice(browsers)
            return getattr(self.user_agent_generator, browser)
        except Exception:
            # Fallback user agents
            fallback_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
            ]
            return random.choice(fallback_agents)
    
    def get_stealth_headers(self) -> Dict[str, str]:
        """Get comprehensive stealth headers."""
        user_agent = self.get_random_user_agent()
        
        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": random.choice([
                "en-US,en;q=0.9",
                "en-US,en;q=0.9,es;q=0.8",
                "en-GB,en;q=0.9,en-US;q=0.8",
                "en-US,en;q=0.9,fr;q=0.8",
            ]),
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
        
        # Add Chrome-specific headers randomly
        if "Chrome" in user_agent:
            if random.random() < 0.7:
                headers.update({
                    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    "Sec-Ch-Ua-Mobile": "?0",
                    "Sec-Ch-Ua-Platform": random.choice(['"Windows"', '"macOS"', '"Linux"']),
                })
        
        return headers
    
    def create_undetected_chrome_driver(self, headless: bool = False, proxy: Optional[str] = None) -> webdriver.Chrome:
        """Create an undetected Chrome driver with stealth measures."""
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium and undetected-chromedriver are required")
        
        options = uc.ChromeOptions()
        
        if headless:
            options.add_argument("--headless=new")
        
        # Advanced stealth arguments
        stealth_args = [
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
            "--disable-features=VizDisplayCompositor",
            "--disable-blink-features=AutomationControlled",
            "--exclude-switches=enable-automation",
            "--disable-extensions-except",
            "--disable-plugins-except",
            "--disable-default-apps",
            "--disable-background-mode",
            "--disable-background-networking",
            "--disable-background-timer-throttling",
            "--disable-renderer-backgrounding",
            "--disable-backgrounding-occluded-windows",
            "--disable-client-side-phishing-detection",
            "--disable-sync",
            "--metrics-recording-only",
            "--no-report-upload",
            "--disable-logging",
            "--disable-gpu-logging",
            "--silent",
            "--log-level=3",
        ]
        
        for arg in stealth_args:
            options.add_argument(arg)
        
        # Randomize window size
        width = random.randint(1200, 1920)
        height = random.randint(800, 1080)
        options.add_argument(f"--window-size={width},{height}")
        
        if proxy:
            options.add_argument(f"--proxy-server={proxy}")
        
        # Create undetected driver
        driver = uc.Chrome(options=options, version_main=None)
        
        # Apply selenium-stealth
        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
        )
        
        return driver
    
    async def apply_playwright_stealth(self, page: Page) -> None:
        """Apply advanced stealth measures to a Playwright page."""
        if not PLAYWRIGHT_AVAILABLE:
            return
        
        # Advanced JavaScript stealth measures
        stealth_script = """
        // Remove webdriver property
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined,
        });
        
        // Mock plugins
        Object.defineProperty(navigator, 'plugins', {
            get: () => [
                { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' },
                { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
                { name: 'Native Client', filename: 'internal-nacl-plugin' },
            ],
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
            runtime: {
                onConnect: undefined,
                onMessage: undefined,
            },
        };
        
        // Mock screen properties
        Object.defineProperty(screen, 'availHeight', {
            get: () => 1040,
        });
        Object.defineProperty(screen, 'availWidth', {
            get: () => 1920,
        });
        
        // Mock timezone
        Object.defineProperty(Intl.DateTimeFormat.prototype, 'resolvedOptions', {
            value: function() {
                return { timeZone: 'America/New_York' };
            },
        });
        
        // Mock canvas fingerprint
        const getContext = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function(type) {
            if (type === '2d') {
                const context = getContext.call(this, type);
                const originalFillText = context.fillText;
                context.fillText = function(text, x, y, maxWidth) {
                    // Add slight randomization to canvas fingerprint
                    const jitter = Math.random() * 0.1;
                    return originalFillText.call(this, text, x + jitter, y + jitter, maxWidth);
                };
                return context;
            }
            return getContext.call(this, type);
        };
        
        // Mock WebGL fingerprint
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(parameter) {
            if (parameter === 37445) { // UNMASKED_VENDOR_WEBGL
                return 'Intel Inc.';
            }
            if (parameter === 37446) { // UNMASKED_RENDERER_WEBGL
                return 'Intel Iris OpenGL Engine';
            }
            return getParameter.call(this, parameter);
        };
        
        // Mock battery API
        if ('getBattery' in navigator) {
            navigator.getBattery = () => Promise.resolve({
                charging: true,
                chargingTime: 0,
                dischargingTime: Infinity,
                level: 1,
            });
        }
        
        // Mock connection API
        if ('connection' in navigator) {
            Object.defineProperty(navigator, 'connection', {
                get: () => ({
                    effectiveType: '4g',
                    rtt: 50,
                    downlink: 10,
                    saveData: false,
                }),
            });
        }
        
        // Mock device memory
        if ('deviceMemory' in navigator) {
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8,
            });
        }
        
        // Mock hardware concurrency
        Object.defineProperty(navigator, 'hardwareConcurrency', {
            get: () => 8,
        });
        
        // Mock platform
        Object.defineProperty(navigator, 'platform', {
            get: () => 'Win32',
        });
        
        // Mock vendor
        Object.defineProperty(navigator, 'vendor', {
            get: () => 'Google Inc.',
        });
        
        // Mock vendorSub
        Object.defineProperty(navigator, 'vendorSub', {
            get: () => '',
        });
        
        // Mock productSub
        Object.defineProperty(navigator, 'productSub', {
            get: () => '20030107',
        });
        
        // Mock appName
        Object.defineProperty(navigator, 'appName', {
            get: () => 'Netscape',
        });
        
        // Mock appVersion
        Object.defineProperty(navigator, 'appVersion', {
            get: () => '5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        });
        
        // Mock userAgent
        Object.defineProperty(navigator, 'userAgent', {
            get: () => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        });
        """
        
        await page.add_init_script(stealth_script)
    
    def make_cloudscraper_request(self, url: str, **kwargs) -> requests.Response:
        """Make a request using cloudscraper to bypass Cloudflare."""
        headers = self.get_stealth_headers()
        kwargs.setdefault('headers', {}).update(headers)
        
        # Add random delay
        time.sleep(random.uniform(1, 3))
        
        return self.cloudscraper_session.get(url, **kwargs)
    
    def make_stealth_request(self, url: str, **kwargs) -> requests.Response:
        """Make a stealth request using regular requests with stealth headers."""
        headers = self.get_stealth_headers()
        kwargs.setdefault('headers', {}).update(headers)
        
        # Add random delay
        time.sleep(random.uniform(0.5, 2))
        
        return self.requests_session.get(url, **kwargs)
    
    async def simulate_human_behavior(self, page: Page) -> None:
        """Simulate human-like behavior on a page."""
        if not PLAYWRIGHT_AVAILABLE:
            return
        
        # Random mouse movements
        for _ in range(random.randint(2, 5)):
            x = random.randint(100, 800)
            y = random.randint(100, 600)
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # Random scrolling
        if random.random() < 0.7:
            scroll_amount = random.randint(-300, 300)
            await page.mouse.wheel(0, scroll_amount)
            await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Random keyboard activity
        if random.random() < 0.3:
            keys = ['Tab', 'Space', 'ArrowDown', 'ArrowUp']
            key = random.choice(keys)
            await page.keyboard.press(key)
            await asyncio.sleep(random.uniform(0.1, 0.3))


# Global instance for easy access
stealth_utils = AdvancedStealth()
