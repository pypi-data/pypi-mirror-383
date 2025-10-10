#!/usr/bin/env python3
"""
Demonstration of Multiple Browser Windows with Randomization
Shows how yt_streams handles multiple workers with different stealth configurations
"""

import asyncio
import random
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, TaskID
import time

from yt_streams.controller import PoolController
from yt_streams.worker import BrowserOptions

console = Console()

async def demo_multiple_browsers():
    """Demonstrate multiple browser windows with randomization"""
    
    console.print(Panel.fit(
        "[bold blue]yt_streams Multiple Browser Demonstration[/bold blue]\n"
        "This demo shows how the system handles multiple browser instances\n"
        "with randomized stealth configurations and user agents.",
        title="🌐 Multi-Browser Demo"
    ))
    
    # Test URL
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    # Create browser options with stealth enabled
    browser_options = BrowserOptions(
        headless=False,  # Show all browsers
        stealth=True,  # Enable stealth mode
        random_user_agent=True,  # Randomize user agents
    )
    
    # Create controller with multiple workers
    controller = PoolController(
        url=url,
        workers=5,  # 5 browser windows
        browser=browser_options,
        timezone="UTC",
    )
    
    console.print(f"\n🎯 [bold]Starting 5 browser instances for URL:[/bold] {url}")
    console.print("🔧 [bold]Stealth Features Enabled:[/bold]")
    console.print("   • Random user agents")
    console.print("   • Randomized viewports")
    console.print("   • Anti-detection measures")
    console.print("   • Human-like interactions")
    console.print("   • Random delays")
    
    # Start the controller
    controller.start()
    
    # Show browser configurations
    table = Table(title="Browser Instance Configurations")
    table.add_column("Worker ID", style="cyan")
    table.add_column("User Agent", style="green", max_width=50)
    table.add_column("Viewport", style="yellow")
    table.add_column("Stealth", style="red")
    
    for i, worker in enumerate(controller.workers):
        if hasattr(worker, 'options'):
            ua = worker.options.user_agent[:47] + "..." if len(worker.options.user_agent) > 50 else worker.options.user_agent
            viewport = f"{worker.options.viewport['width']}x{worker.options.viewport['height']}"
            stealth_status = "✅" if worker.options.stealth else "❌"
            
            table.add_row(
                str(i),
                ua,
                viewport,
                stealth_status
            )
    
    console.print("\n")
    console.print(table)
    
    # Monitor the workers
    console.print("\n🔄 [bold]Monitoring browser activity...[/bold]")
    console.print("Each browser will:")
    console.print("   • Open in a separate window")
    console.print("   • Navigate to YouTube")
    console.print("   • Apply stealth measures")
    console.print("   • Start playing the video")
    console.print("   • Use randomized interactions")
    
    # Progress tracking
    with Progress() as progress:
        task = progress.add_task("[green]Running demo...", total=100)
        
        for i in range(100):
            # Update progress
            progress.update(task, advance=1, description=f"Demo running... {i}%")
            
            # Show worker status
            if i % 10 == 0:
                active_workers = sum(1 for w in controller.workers if w.is_alive())
                console.print(f"📊 Active workers: {active_workers}/5")
            
            await asyncio.sleep(0.1)
    
    console.print("\n✅ [bold green]Demo completed![/bold green]")
    console.print("\n[dim]You should have seen:")
    console.print("   • 5 browser windows open")
    console.print("   • Each with different user agents")
    console.print("   • Different viewport sizes")
    console.print("   • All navigating to YouTube")
    console.print("   • Videos playing without bot detection[/dim]")
    
    # Stop the controller
    console.print("\n🛑 [yellow]Stopping all browsers...[/yellow]")
    controller.stop()

async def demo_randomization_features():
    """Show the randomization features in detail"""
    
    console.print(Panel.fit(
        "[bold blue]Randomization Features Demo[/bold blue]\n"
        "This shows the various randomization techniques used",
        title="🎲 Randomization Demo"
    ))
    
    from yt_streams.stealth import stealth_utils
    from yt_streams.robots_config import config_manager
    
    # Show random user agents
    console.print("\n🌐 [bold]Random User Agents:[/bold]")
    for i in range(5):
        ua = stealth_utils.get_random_user_agent()
        console.print(f"   {i+1}. {ua}")
    
    # Show random viewports
    console.print("\n📱 [bold]Random Viewports:[/bold]")
    for i in range(5):
        width = random.randint(1200, 1920)
        height = random.randint(800, 1080)
        console.print(f"   {i+1}. {width}x{height}")
    
    # Show stealth headers
    console.print("\n🔒 [bold]Stealth Headers:[/bold]")
    headers = stealth_utils.get_stealth_headers()
    for key, value in headers.items():
        console.print(f"   {key}: {value}")
    
    # Show config options
    console.print("\n⚙️ [bold]Configuration Options:[/bold]")
    console.print(f"   Random viewport: {config_manager.stealth_config.random_viewport}")
    console.print(f"   Random user agent: {config_manager.stealth_config.random_user_agent}")
    console.print(f"   Disable images: {config_manager.stealth_config.disable_images}")
    console.print(f"   Human-like delays: {config_manager.stealth_config.human_like_delays}")

async def main():
    """Main demo function"""
    try:
        await demo_randomization_features()
        console.print("\n" + "="*60 + "\n")
        await demo_multiple_browsers()
    except KeyboardInterrupt:
        console.print("\n🛑 [yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print("\n❌ [red]Demo error:[/red]")
        console.print(f"[red]{str(e)}[/red]")

if __name__ == "__main__":
    asyncio.run(main())
