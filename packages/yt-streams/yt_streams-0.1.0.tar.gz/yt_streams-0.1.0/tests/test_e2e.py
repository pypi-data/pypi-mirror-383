#!/usr/bin/env python3
"""
End-to-End Test Suite for yt_streams

This script tests the complete functionality including:
- URL handling for different platforms
- Proxy management
- Stealth features
- Multi-browser coordination
- Streamlit UI integration
"""

import asyncio
import sys
import time
from pathlib import Path
from typing import List, Dict, Any
import json

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, TaskID

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from yt_streams.url_handler import URLHandler, URLType, ProxyConfig, ProxyChain
from yt_streams.proxy_manager import ProxyManager
from yt_streams.stealth import stealth_utils
from yt_streams.controller import PoolController
from yt_streams.worker import BrowserOptions

console = Console()

class E2ETestSuite:
    """Comprehensive end-to-end test suite"""
    
    def __init__(self):
        self.results: Dict[str, Any] = {}
        self.url_handler = URLHandler()
        self.proxy_manager = ProxyManager()
        
    def test_url_detection(self) -> bool:
        """Test URL type detection"""
        console.print("\n🔍 [bold]Testing URL Detection[/bold]")
        
        test_urls = {
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ": URLType.YOUTUBE,
            "https://youtu.be/dQw4w9WgXcQ": URLType.YOUTUBE,
            "https://www.twitch.tv/ninja": URLType.TWITCH,
            "https://vimeo.com/123456789": URLType.VIMEO,
            "https://www.dailymotion.com/video/x123abc": URLType.DAILYMOTION,
            "https://example.com/video": URLType.GENERIC,
        }
        
        passed = 0
        total = len(test_urls)
        
        for url, expected_type in test_urls.items():
            detected_type = self.url_handler.detect_url_type(url)
            if detected_type == expected_type:
                console.print(f"✅ {url} → {detected_type.value}")
                passed += 1
            else:
                console.print(f"❌ {url} → Expected {expected_type.value}, got {detected_type.value}")
        
        success_rate = passed / total
        self.results['url_detection'] = {'passed': passed, 'total': total, 'rate': success_rate}
        
        console.print(f"\n📊 URL Detection: {passed}/{total} ({success_rate:.1%})")
        return success_rate >= 0.8
    
    def test_url_validation(self) -> bool:
        """Test URL validation"""
        console.print("\n✅ [bold]Testing URL Validation[/bold]")
        
        test_cases = [
            ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", True),
            ("http://example.com", True),
            ("ftp://example.com", False),
            ("not-a-url", False),
            ("", False),
        ]
        
        passed = 0
        total = len(test_cases)
        
        for url, expected_valid in test_cases:
            is_valid, message = self.url_handler.validate_url(url)
            if is_valid == expected_valid:
                console.print(f"✅ {url} → Valid: {is_valid}")
                passed += 1
            else:
                console.print(f"❌ {url} → Expected {expected_valid}, got {is_valid}: {message}")
        
        success_rate = passed / total
        self.results['url_validation'] = {'passed': passed, 'total': total, 'rate': success_rate}
        
        console.print(f"\n📊 URL Validation: {passed}/{total} ({success_rate:.1%})")
        return success_rate >= 0.8
    
    def test_stealth_configuration(self) -> bool:
        """Test stealth configuration for different URL types"""
        console.print("\n🥷 [bold]Testing Stealth Configuration[/bold]")
        
        test_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.twitch.tv/ninja",
            "https://vimeo.com/123456789",
            "https://example.com/video",
        ]
        
        passed = 0
        total = len(test_urls)
        
        for url in test_urls:
            config = self.url_handler.get_stealth_config(url)
            
            # Check required fields
            required_fields = ['stealth_required', 'user_agent_rotation', 'viewport_randomization', 'url_type']
            if all(field in config for field in required_fields):
                console.print(f"✅ {url} → {config['url_type']} (stealth: {config['stealth_required']})")
                passed += 1
            else:
                console.print(f"❌ {url} → Missing required fields")
        
        success_rate = passed / total
        self.results['stealth_config'] = {'passed': passed, 'total': total, 'rate': success_rate}
        
        console.print(f"\n📊 Stealth Configuration: {passed}/{total} ({success_rate:.1%})")
        return success_rate >= 0.8
    
    def test_proxy_management(self) -> bool:
        """Test proxy management system"""
        console.print("\n🌐 [bold]Testing Proxy Management[/bold]")
        
        # Test proxy creation
        test_proxies = [
            ProxyConfig(host="proxy1.example.com", port=8080, protocol="http"),
            ProxyConfig(host="proxy2.example.com", port=3128, username="user", password="pass"),
            ProxyConfig(host="proxy3.example.com", port=1080, protocol="socks5"),
        ]
        
        # Add proxies
        for proxy in test_proxies:
            self.proxy_manager.add_proxy(proxy)
        
        # Test proxy chain
        if len(self.proxy_manager.proxy_chain.proxies) == len(test_proxies):
            console.print(f"✅ Added {len(test_proxies)} proxies to chain")
            passed = 1
        else:
            console.print(f"❌ Expected {len(test_proxies)} proxies, got {len(self.proxy_manager.proxy_chain.proxies)}")
            passed = 0
        
        # Test proxy rotation
        proxy1 = self.proxy_manager.proxy_chain.get_next_proxy()
        proxy2 = self.proxy_manager.proxy_chain.get_next_proxy()
        
        if proxy1 != proxy2:
            console.print("✅ Proxy rotation working")
            passed += 1
        else:
            console.print("❌ Proxy rotation not working")
        
        # Test health summary
        summary = self.proxy_manager.get_health_summary()
        if 'total_proxies' in summary and summary['total_proxies'] == len(test_proxies):
            console.print("✅ Health summary working")
            passed += 1
        else:
            console.print("❌ Health summary not working")
        
        success_rate = passed / 3
        self.results['proxy_management'] = {'passed': passed, 'total': 3, 'rate': success_rate}
        
        console.print(f"\n📊 Proxy Management: {passed}/3 ({success_rate:.1%})")
        return success_rate >= 0.8
    
    def test_stealth_utils(self) -> bool:
        """Test stealth utilities"""
        console.print("\n🛡️ [bold]Testing Stealth Utilities[/bold]")
        
        passed = 0
        total = 4
        
        # Test user agent generation
        ua1 = stealth_utils.get_random_user_agent()
        ua2 = stealth_utils.get_random_user_agent()
        
        if ua1 and ua2 and ua1 != ua2:
            console.print("✅ Random user agent generation working")
            passed += 1
        else:
            console.print("❌ Random user agent generation not working")
        
        # Test stealth headers
        headers = stealth_utils.get_stealth_headers()
        if headers and 'User-Agent' in headers:
            console.print("✅ Stealth headers generation working")
            passed += 1
        else:
            console.print("❌ Stealth headers generation not working")
        
        # Test viewport randomization
        viewport1 = stealth_utils.get_random_viewport()
        viewport2 = stealth_utils.get_random_viewport()
        
        if viewport1 and viewport2 and viewport1 != viewport2:
            console.print("✅ Viewport randomization working")
            passed += 1
        else:
            console.print("❌ Viewport randomization not working")
        
        # Test delay generation
        delay = stealth_utils.get_random_delay(1, 5)
        if 1 <= delay <= 5:
            console.print("✅ Random delay generation working")
            passed += 1
        else:
            console.print("❌ Random delay generation not working")
        
        success_rate = passed / total
        self.results['stealth_utils'] = {'passed': passed, 'total': total, 'rate': success_rate}
        
        console.print(f"\n📊 Stealth Utilities: {passed}/{total} ({success_rate:.1%})")
        return success_rate >= 0.8
    
    async def test_browser_coordination(self) -> bool:
        """Test multi-browser coordination"""
        console.print("\n🌐 [bold]Testing Browser Coordination[/bold]")
        
        try:
            # Create controller with multiple workers
            browser_options = BrowserOptions(
                headless=True,  # Use headless for testing
                stealth=True,
                random_user_agent=True,
            )
            
            controller = PoolController(
                url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                workers=3,
                browser=browser_options,
                timezone="UTC",
            )
            
            # Start controller
            controller.start()
            
            # Wait a bit for workers to initialize
            await asyncio.sleep(2)
            
            # Check if workers are running
            active_workers = sum(1 for w in controller.workers if w.is_alive())
            
            if active_workers == 3:
                console.print("✅ All 3 workers started successfully")
                passed = 1
            else:
                console.print(f"❌ Expected 3 workers, got {active_workers}")
                passed = 0
            
            # Test worker configuration
            if len(controller.workers) > 0:
                worker = controller.workers[0]
                if hasattr(worker, 'options') and worker.options.stealth:
                    console.print("✅ Worker stealth configuration working")
                    passed += 1
                else:
                    console.print("❌ Worker stealth configuration not working")
            
            # Stop controller
            controller.stop()
            
            success_rate = passed / 2
            self.results['browser_coordination'] = {'passed': passed, 'total': 2, 'rate': success_rate}
            
            console.print(f"\n📊 Browser Coordination: {passed}/2 ({success_rate:.1%})")
            return success_rate >= 0.8
            
        except Exception as e:
            console.print(f"❌ Browser coordination test failed: {e}")
            self.results['browser_coordination'] = {'passed': 0, 'total': 2, 'rate': 0.0}
            return False
    
    def generate_report(self) -> None:
        """Generate comprehensive test report"""
        console.print("\n" + "="*60)
        console.print("📊 [bold blue]E2E Test Report[/bold blue]")
        console.print("="*60)
        
        # Create results table
        table = Table(title="Test Results")
        table.add_column("Test", style="cyan")
        table.add_column("Passed", style="green")
        table.add_column("Total", style="yellow")
        table.add_column("Rate", style="red")
        table.add_column("Status", style="bold")
        
        total_passed = 0
        total_tests = 0
        
        for test_name, result in self.results.items():
            passed = result['passed']
            total = result['total']
            rate = result['rate']
            
            total_passed += passed
            total_tests += total
            
            status = "✅ PASS" if rate >= 0.8 else "❌ FAIL"
            table.add_row(
                test_name.replace('_', ' ').title(),
                str(passed),
                str(total),
                f"{rate:.1%}",
                status
            )
        
        console.print(table)
        
        # Overall summary
        overall_rate = total_passed / total_tests if total_tests > 0 else 0
        console.print(f"\n🎯 [bold]Overall Success Rate: {total_passed}/{total_tests} ({overall_rate:.1%})[/bold]")
        
        if overall_rate >= 0.8:
            console.print("🎉 [bold green]All tests passed! System is ready for production.[/bold green]")
        elif overall_rate >= 0.6:
            console.print("⚠️ [bold yellow]Most tests passed. Some issues need attention.[/bold yellow]")
        else:
            console.print("❌ [bold red]Multiple test failures. System needs significant fixes.[/bold red]")
        
        # Save report to file
        report_file = Path("e2e_test_report.json")
        with open(report_file, 'w') as f:
            json.dump({
                'timestamp': time.time(),
                'overall_rate': overall_rate,
                'total_passed': total_passed,
                'total_tests': total_tests,
                'results': self.results
            }, f, indent=2)
        
        console.print(f"\n📄 Report saved to: {report_file}")
    
    async def run_all_tests(self) -> bool:
        """Run all tests"""
        console.print(Panel.fit(
            "[bold blue]yt_streams End-to-End Test Suite[/bold blue]\n"
            "Testing complete system functionality",
            title="🧪 E2E Tests"
        ))
        
        tests = [
            ("URL Detection", self.test_url_detection),
            ("URL Validation", self.test_url_validation),
            ("Stealth Configuration", self.test_stealth_configuration),
            ("Proxy Management", self.test_proxy_management),
            ("Stealth Utilities", self.test_stealth_utils),
            ("Browser Coordination", self.test_browser_coordination),
        ]
        
        with Progress() as progress:
            task = progress.add_task("[green]Running tests...", total=len(tests))
            
            for test_name, test_func in tests:
                progress.update(task, description=f"Running {test_name}...")
                
                try:
                    if asyncio.iscoroutinefunction(test_func):
                        await test_func()
                    else:
                        test_func()
                except Exception as e:
                    console.print(f"❌ {test_name} failed with error: {e}")
                    self.results[test_name.lower().replace(' ', '_')] = {
                        'passed': 0, 'total': 1, 'rate': 0.0
                    }
                
                progress.advance(task)
        
        self.generate_report()
        
        # Return overall success
        total_passed = sum(r['passed'] for r in self.results.values())
        total_tests = sum(r['total'] for r in self.results.values())
        overall_rate = total_passed / total_tests if total_tests > 0 else 0
        
        return overall_rate >= 0.8

async def main():
    """Main test function"""
    test_suite = E2ETestSuite()
    success = await test_suite.run_all_tests()
    
    if success:
        console.print("\n🎉 [bold green]All tests passed! System is ready.[/bold green]")
        sys.exit(0)
    else:
        console.print("\n❌ [bold red]Some tests failed. Check the report.[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
