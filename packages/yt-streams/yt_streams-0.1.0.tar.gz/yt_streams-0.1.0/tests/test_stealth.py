#!/usr/bin/env python3
"""Test script for yt_streams stealth implementation.

Purpose:
    Test the stealth implementation with a real YouTube URL to verify
    that bot detection is bypassed.

Usage:
    python test_stealth.py [URL]
"""

import asyncio
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from yt_streams import (
    BrowserOptions,
    PoolController,
    Command,
    stealth_utils,
    config_manager,
    can_fetch_url,
    get_crawl_delay,
)

console = Console()


def print_header():
    """Print test header."""
    console.print(Panel.fit(
        "[bold blue]yt_streams Stealth Test[/bold blue]\n"
        "Testing anti-detection measures against YouTube",
        border_style="blue"
    ))


def print_config():
    """Print current configuration."""
    table = Table(title="Current Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    # Stealth config
    stealth_config = config_manager.stealth_config
    table.add_row("Stealth Mode", str(stealth_config.stealth_mode))
    table.add_row("Random User Agent", str(stealth_config.random_user_agent))
    table.add_row("Random Viewport", str(stealth_config.random_viewport))
    table.add_row("Human-like Delays", str(stealth_config.human_like_delays))
    table.add_row("Simulate Mouse Movement", str(stealth_config.simulate_mouse_movement))
    table.add_row("Simulate Scrolling", str(stealth_config.simulate_scrolling))
    
    # Robots config
    robots_config = config_manager.robots_config
    table.add_row("Respect Robots.txt", str(robots_config.respect_robots))
    table.add_row("User Agent", robots_config.user_agent)
    table.add_row("Crawl Delay", f"{robots_config.crawl_delay}s")
    
    console.print(table)


def test_robots_compliance(url: str):
    """Test robots.txt compliance."""
    console.print("\n[bold]Testing robots.txt compliance...[/bold]")
    
    can_fetch = can_fetch_url(url)
    crawl_delay = get_crawl_delay(url)
    
    if can_fetch:
        console.print(f"✅ [green]Can fetch URL: {url}[/green]")
        console.print(f"⏱️  [yellow]Crawl delay: {crawl_delay} seconds[/yellow]")
    else:
        console.print(f"❌ [red]Cannot fetch URL: {url}[/red]")
        console.print("[red]URL is blocked by robots.txt[/red]")


def test_stealth_utils():
    """Test stealth utilities."""
    console.print("\n[bold]Testing stealth utilities...[/bold]")
    
    # Test user agent generation
    user_agent = stealth_utils.get_random_user_agent()
    console.print(f"🎭 [cyan]Random User Agent:[/cyan] {user_agent[:80]}...")
    
    # Test stealth headers
    headers = stealth_utils.get_stealth_headers()
    console.print(f"📋 [cyan]Stealth Headers:[/cyan] {len(headers)} headers generated")
    
    # Show some key headers
    key_headers = ["User-Agent", "Accept", "Accept-Language", "Accept-Encoding"]
    for header in key_headers:
        if header in headers:
            value = headers[header][:50] + "..." if len(headers[header]) > 50 else headers[header]
            console.print(f"   {header}: {value}")


async def test_browser_launch(url: str):
    """Test browser launch with stealth measures."""
    console.print("\n[bold]Testing browser launch with stealth...[/bold]")
    
    # Create browser options with stealth
    browser_options = BrowserOptions(
        headless=False,  # Set to False so we can see what's happening
        stealth=True,
        random_user_agent=True,
    )
    
    console.print(f"🌐 [cyan]Browser Options:[/cyan]")
    console.print(f"   Headless: {browser_options.headless}")
    console.print(f"   Stealth: {browser_options.stealth}")
    console.print(f"   Random User Agent: {browser_options.random_user_agent}")
    console.print(f"   Viewport: {browser_options.viewport}")
    console.print(f"   User Agent: {browser_options.user_agent[:80]}...")
    
    # Create controller
    controller = PoolController(
        url=url,
        workers=1,
        browser=browser_options,
    )
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Starting controller...", total=None)
            
            # Start controller
            controller.start()
            progress.update(task, description="Controller started, testing browser...")
            
            # Wait a bit for browser to initialize
            await asyncio.sleep(3)
            
            # Send a test command
            progress.update(task, description="Sending test command...")
            command = Command(play_seconds=10)
            controller.broadcast(command)
            
            # Wait for the command to be processed
            await asyncio.sleep(5)
            
            progress.update(task, description="Test completed!")
            
        console.print("✅ [green]Browser test completed successfully![/green]")
        
        # Check if we got any status updates
        status_count = 0
        while not controller.status_sink.empty():
            status = controller.status_sink.get_nowait()
            status_count += 1
            if status_count <= 5:  # Show first 5 status updates
                console.print(f"📊 [blue]Status:[/blue] {status.phase} - Worker {status.wid}")
        
        if status_count > 0:
            console.print(f"📈 [green]Received {status_count} status updates[/green]")
        else:
            console.print("⚠️  [yellow]No status updates received[/yellow]")
            
    except Exception as e:
        console.print(f"❌ [red]Error during browser test: {e}[/red]")
        import traceback
        console.print(f"[red]{traceback.format_exc()}[/red]")
    finally:
        console.print("\n🛑 [yellow]Stopping controller...[/yellow]")
        controller.stop()


async def main():
    """Main test function."""
    print_header()
    
    # Get URL from command line or use default
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        # Use a test YouTube URL
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll for testing
    
    console.print(f"🎯 [bold]Testing URL:[/bold] {url}")
    
    # Print configuration
    print_config()
    
    # Test robots.txt compliance
    test_robots_compliance(url)
    
    # Test stealth utilities
    test_stealth_utils()
    
    # Test browser launch
    await test_browser_launch(url)
    
    console.print("\n🎉 [bold green]Test completed![/bold green]")
    console.print("\n[dim]If you saw the browser open and navigate to YouTube without showing")
    console.print("'Sign in to confirm you're not a bot', then the stealth implementation is working![/dim]")


if __name__ == "__main__":
    asyncio.run(main())
