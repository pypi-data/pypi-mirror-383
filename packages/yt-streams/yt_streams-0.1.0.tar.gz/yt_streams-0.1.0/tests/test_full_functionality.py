#!/usr/bin/env python3
"""Test full functionality of yt_streams with stealth measures.

Purpose:
    Test the complete workflow: browser launch, stealth measures, 
    YouTube navigation, and video playback.

Usage:
    python test_full_functionality.py [URL]
"""

import asyncio
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from yt_streams import (
    PoolController,
    BrowserOptions,
    Command,
    stealth_utils,
    config_manager,
)

console = Console()


def print_header():
    """Print test header."""
    console.print(Panel.fit(
        "[bold blue]yt_streams Full Functionality Test[/bold blue]\n"
        "Testing complete workflow with stealth measures",
        border_style="blue"
    ))


async def test_full_workflow(url: str):
    """Test the complete workflow."""
    console.print(f"\n🎯 [bold]Testing URL:[/bold] {url}")
    
    # Create stealth browser options
    browser_options = BrowserOptions(
        headless=False,  # Set to False so we can see what's happening
        stealth=True,
        random_user_agent=True,
    )
    
    console.print(f"🌐 [cyan]Browser Options:[/cyan]")
    console.print(f"   Headless: {browser_options.headless}")
    console.print(f"   Stealth: {browser_options.stealth}")
    console.print(f"   User Agent: {browser_options.user_agent[:80]}...")
    console.print(f"   Viewport: {browser_options.viewport}")
    
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
            progress.update(task, description="Controller started, waiting for browser...")
            
            # Wait for browser to initialize
            await asyncio.sleep(5)
            
            # Check status
            status_count = 0
            while not controller.status_sink.empty():
                status = controller.status_sink.get_nowait()
                status_count += 1
                console.print(f"📊 [blue]Status:[/blue] {status.phase} - Worker {status.wid}")
                if hasattr(status, 'last_error') and status.last_error:
                    console.print(f"❌ [red]Error:[/red] {status.last_error}")
            
            if status_count == 0:
                console.print("⚠️  [yellow]No status updates received[/yellow]")
                return
            
            # Send a play command
            progress.update(task, description="Sending play command...")
            command = Command(play_seconds=30)  # Play for 30 seconds
            controller.broadcast(command)
            
            # Wait and monitor
            for i in range(35):  # Wait 35 seconds total
                await asyncio.sleep(1)
                
                # Check for new status updates
                while not controller.status_sink.empty():
                    status = controller.status_sink.get_nowait()
                    if status.phase.value == "working":
                        play_seconds = getattr(status, 'play_seconds', 0)
                        console.print(f"▶️  [green]Playing:[/green] {play_seconds}s")
                    elif status.phase.value == "error":
                        console.print(f"❌ [red]Error:[/red] {getattr(status, 'last_error', 'Unknown error')}")
                        return
                
                if i % 5 == 0:  # Update progress every 5 seconds
                    progress.update(task, description=f"Playing video... {i}s")
            
            progress.update(task, description="Test completed!")
            
        console.print("✅ [green]Full workflow test completed![/green]")
        console.print("\n[dim]If you saw the browser open, navigate to YouTube, and start playing")
        console.print("a video without showing 'Sign in to confirm you're not a bot',")
        console.print("then the stealth implementation is working perfectly![/dim]")
            
    except Exception as e:
        console.print("❌ [red]Error during test:[/red]")
        console.print(f"[red]{str(e)}[/red]")
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
    
    # Test full workflow
    await test_full_workflow(url)
    
    console.print("\n🎉 [bold green]Test completed![/bold green]")


if __name__ == "__main__":
    asyncio.run(main())
