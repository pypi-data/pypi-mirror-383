#!/usr/bin/env python3
"""Debug script to test worker initialization step by step."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from playwright.async_api import async_playwright
from yt_streams.stealth import stealth_utils
from yt_streams.robots_config import config_manager

async def debug_browser_launch():
    """Debug browser launch step by step."""
    print("🔍 Debugging browser launch...")
    
    try:
        async with async_playwright() as pw:
            print("✅ Playwright initialized")
            
            # Test basic browser launch first
            print("🌐 Launching basic browser...")
            browser = await pw.chromium.launch(headless=False)
            print("✅ Basic browser launched")
            
            # Test context creation
            print("📄 Creating context...")
            context = await browser.new_context()
            print("✅ Context created")
            
            # Test page creation
            print("📃 Creating page...")
            page = await context.new_page()
            print("✅ Page created")
            
            # Test navigation
            print("🌍 Navigating to YouTube...")
            await page.goto("https://www.youtube.com/watch?v=dQw4w9WgXcQ", wait_until="domcontentloaded")
            print("✅ Navigation successful")
            
            # Wait a bit to see if it stays open
            print("⏳ Waiting 5 seconds to see if browser stays open...")
            await asyncio.sleep(5)
            
            # Close everything
            await context.close()
            await browser.close()
            print("✅ Browser closed cleanly")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

async def debug_stealth_browser():
    """Debug stealth browser launch."""
    print("\n🔍 Debugging stealth browser launch...")
    
    try:
        async with async_playwright() as pw:
            print("✅ Playwright initialized")
            
            # Launch with stealth options
            print("🌐 Launching browser with stealth options...")
            launch_options = {
                "headless": False,
                "args": [
                    "--no-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--disable-extensions",
                    "--disable-gpu",
                    "--disable-web-security",
                ]
            }
            
            browser = await pw.chromium.launch(**launch_options)
            print("✅ Stealth browser launched")
            
            # Create context with stealth settings
            print("📄 Creating stealth context...")
            context_kwargs = {
                "viewport": {"width": 1280, "height": 720},
                "user_agent": stealth_utils.get_random_user_agent(),
                "extra_http_headers": stealth_utils.get_stealth_headers()
            }
            
            context = await browser.new_context(**context_kwargs)
            print("✅ Stealth context created")
            
            # Create page
            print("📃 Creating page...")
            page = await context.new_page()
            print("✅ Page created")
            
            # Apply stealth
            print("🥷 Applying stealth measures...")
            from playwright_stealth import stealth
            stealth(page)
            print("✅ Stealth applied")
            
            # Navigate
            print("🌍 Navigating to YouTube...")
            await page.goto("https://www.youtube.com/watch?v=dQw4w9WgXcQ", wait_until="domcontentloaded")
            print("✅ Navigation successful")
            
            # Wait to see if it stays open
            print("⏳ Waiting 10 seconds to see if browser stays open...")
            await asyncio.sleep(10)
            
            # Close
            await context.close()
            await browser.close()
            print("✅ Stealth browser closed cleanly")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main debug function."""
    print("🚀 Starting browser debug tests...\n")
    
    # Test basic browser first
    await debug_browser_launch()
    
    # Test stealth browser
    await debug_stealth_browser()
    
    print("\n🎉 Debug tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
