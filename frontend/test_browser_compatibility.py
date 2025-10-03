"""
Cross-Browser Compatibility Testing for 3D AI Simulation Frontend

Tests the 3D visualization platform across different browsers and
validates WebGL support, performance, and feature compatibility.
"""

import asyncio
import json
import time
import platform
import subprocess
import sys
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Browser compatibility testing using Selenium or Playwright
try:
    from playwright.sync_api import Playwright, Browser, BrowserContext, Page, sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Import frontend types for validation
sys.path.append(os.path.dirname(__file__))
try:
    from src.types.simulation import (
        Agent, Anomaly, SimulationState, WebSocketMessage,
        PerformanceMetrics, ViewportSettings
    )
    TYPES_AVAILABLE = True
except ImportError:
    TYPES_AVAILABLE = False

class BrowserType(Enum):
    """Supported browser types for testing."""
    CHROME = "chrome"
    FIREFOX = "firefox"
    SAFARI = "safari"
    EDGE = "edge"

@dataclass
class BrowserTestResult:
    """Results from browser compatibility testing."""
    browser_type: BrowserType
    version: str
    platform: str
    webgl_support: bool
    webgl_version: str
    performance_score: float
    errors: List[str]
    warnings: List[str]
    test_duration: float
    viewport_tests: Dict[str, bool]
    feature_tests: Dict[str, bool]

@dataclass
class CompatibilityReport:
    """Complete compatibility test report."""
    timestamp: float
    overall_score: float
    total_browsers_tested: int
    compatible_browsers: int
    results: List[BrowserTestResult]
    recommendations: List[str]

class BrowserCompatibilityTester:
    """Main browser compatibility testing class."""

    def __init__(self):
        self.playwright: Optional[Playwright] = None
        self.browsers: Dict[BrowserType, Browser] = {}
        self.test_results: List[BrowserTestResult] = []

    def initialize_browsers(self) -> bool:
        """Initialize browser instances for testing."""
        if not PLAYWRIGHT_AVAILABLE:
            print("⚠️  Playwright not available. Install with: pip install playwright")
            return False

        try:
            self.playwright = sync_playwright().start()

            # Initialize browsers based on platform
            system = platform.system().lower()

            if system == "darwin":  # macOS
                self.browsers[BrowserType.CHROME] = self.playwright.chromium.launch()
                self.browsers[BrowserType.FIREFOX] = self.playwright.firefox.launch()
                self.browsers[BrowserType.SAFARI] = self.playwright.webkit.launch()
            elif system == "windows":
                self.browsers[BrowserType.CHROME] = self.playwright.chromium.launch()
                self.browsers[BrowserType.FIREFOX] = self.playwright.firefox.launch()
                self.browsers[BrowserType.EDGE] = self.playwright.chromium.launch(channel="msedge")
            else:  # Linux
                self.browsers[BrowserType.CHROME] = self.playwright.chromium.launch()
                self.browsers[BrowserType.FIREFOX] = self.playwright.firefox.launch()

            print(f"✅ Initialized {len(self.browsers)} browsers for testing")
            return True

        except Exception as e:
            print(f"❌ Failed to initialize browsers: {e}")
            return False

    def test_webgl_support(self, context: BrowserContext) -> Dict[str, Any]:
        """Test WebGL support and capabilities."""
        try:
            page = context.new_page()

            # Navigate to WebGL test page or inject test script
            page.goto("data:text/html,<html><body><canvas id='test'></canvas></body></html>")

            # Inject WebGL detection script
            webgl_result = page.evaluate("""
                (() => {
                    const canvas = document.getElementById('test');
                    let gl = null;
                    let version = 'none';

                    try {
                        gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                        if (gl) {
                            version = 'WebGL 1.0';
                            const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
                            if (debugInfo) {
                                const renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
                                version += ' (' + renderer + ')';
                            }
                        }
                    } catch (e) {
                        return { supported: false, version: 'none', error: e.message };
                    }

                    // Test WebGL 2.0
                    try {
                        const gl2 = canvas.getContext('webgl2');
                        if (gl2) {
                            version = 'WebGL 2.0';
                            const debugInfo = gl2.getExtension('WEBGL_debug_renderer_info');
                            if (debugInfo) {
                                const renderer = gl2.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
                                version += ' (' + renderer + ')';
                            }
                        }
                    } catch (e) {
                        // WebGL 2.0 not supported, but WebGL 1.0 might be
                    }

                    return {
                        supported: gl !== null,
                        version: version,
                        maxTextureSize: gl ? gl.getParameter(gl.MAX_TEXTURE_SIZE) : 0,
                        maxViewportDims: gl ? gl.getParameter(gl.MAX_VIEWPORT_DIMS) : [0, 0]
                    };
                })()
            """)

            page.close()
            return webgl_result

        except Exception as e:
            return {
                "supported": False,
                "version": "error",
                "error": str(e)
            }

    def test_performance_metrics(self, context: BrowserContext) -> Dict[str, float]:
        """Test browser performance metrics."""
        try:
            page = context.new_page()

            # Navigate to a test page that measures performance
            page.goto("data:text/html,<html><body><div id='test-area'></div></body></html>")

            # Inject performance test script
            performance_result = page.evaluate("""
                (() => {
                    const startTime = performance.now();

                    // Simulate 3D rendering workload
                    const canvas = document.createElement('canvas');
                    canvas.width = 800;
                    canvas.height = 600;
                    const gl = canvas.getContext('webgl');

                    if (!gl) {
                        return { fps: 0, frameTime: 0, error: 'WebGL not available' };
                    }

                    // Simple rendering loop simulation
                    let frameCount = 0;
                    const testDuration = 1000; // 1 second
                    const frameTimeTarget = 16.67; // 60 FPS target

                    const endTime = startTime + testDuration;

                    while (performance.now() < endTime) {
                        // Simulate frame rendering
                        gl.clear(gl.COLOR_BUFFER_BIT);
                        frameCount++;
                    }

                    const actualDuration = performance.now() - startTime;
                    const avgFrameTime = actualDuration / frameCount;
                    const fps = 1000 / avgFrameTime;

                    return {
                        fps: fps,
                        frameTime: avgFrameTime,
                        frameCount: frameCount,
                        testDuration: actualDuration
                    };
                })()
            """)

            page.close()
            return performance_result

        except Exception as e:
            return {
                "fps": 0,
                "frameTime": 0,
                "error": str(e)
            }

    def test_viewport_responsiveness(self, context: BrowserContext) -> Dict[str, bool]:
        """Test viewport and responsiveness features."""
        try:
            page = context.new_page()

            # Test different viewport sizes
            viewport_tests = {}

            viewport_sizes = [
                {"width": 1920, "height": 1080, "name": "desktop"},
                {"width": 1366, "height": 768, "name": "laptop"},
                {"width": 768, "height": 1024, "name": "tablet"},
                {"width": 375, "height": 667, "name": "mobile"}
            ]

            for viewport in viewport_sizes:
                try:
                    page.set_viewport_size({
                        "width": viewport["width"],
                        "height": viewport["height"]
                    })

                    # Test if page responds correctly to viewport changes
                    page.goto("data:text/html,<html><body><div style='width: 100%; height: 100vh; background: red;'></div></body></html>")

                    # Check if viewport size is applied correctly
                    viewport_info = page.evaluate("""
                        () => {
                            return {
                                width: window.innerWidth,
                                height: window.innerHeight,
                                devicePixelRatio: window.devicePixelRatio || 1
                            };
                        }
                    """)

                    # Verify viewport dimensions are reasonable
                    expected_width = viewport["width"]
                    expected_height = viewport["height"]

                    width_ok = abs(viewport_info["width"] - expected_width) <= 50
                    height_ok = abs(viewport_info["height"] - expected_height) <= 50

                    viewport_tests[viewport["name"]] = width_ok and height_ok

                except Exception as e:
                    viewport_tests[viewport["name"]] = False

            page.close()
            return viewport_tests

        except Exception as e:
            return {"error": str(e)}

    def test_feature_support(self, context: BrowserContext) -> Dict[str, bool]:
        """Test browser feature support for 3D visualization."""
        try:
            page = context.new_page()

            # Test various features required for 3D visualization
            feature_tests = {}

            # WebGL support (already tested separately)
            webgl_support = self.test_webgl_support(context)
            feature_tests["webgl"] = webgl_support.get("supported", False)

            # WebSocket support
            feature_tests["websockets"] = page.evaluate("""
                () => 'WebSocket' in window
            """)

            # Web Workers support
            feature_tests["web_workers"] = page.evaluate("""
                () => 'Worker' in window
            """)

            # Local Storage support
            feature_tests["local_storage"] = page.evaluate("""
                () => {
                    try {
                        return 'localStorage' in window && window.localStorage !== null;
                    } catch (e) {
                        return false;
                    }
                }
            """)

            # Geolocation support (for potential future features)
            feature_tests["geolocation"] = page.evaluate("""
                () => 'geolocation' in navigator
            """)

            # Device orientation (for mobile)
            feature_tests["device_orientation"] = page.evaluate("""
                () => 'DeviceOrientationEvent' in window
            """)

            # Touch events (for mobile)
            feature_tests["touch_events"] = page.evaluate("""
                () => 'ontouchstart' in window || navigator.maxTouchPoints > 0
            """)

            # Service Workers (for PWA features)
            feature_tests["service_workers"] = page.evaluate("""
                () => 'serviceWorker' in navigator
            """)

            page.close()
            return feature_tests

        except Exception as e:
            return {"error": str(e)}

    def test_single_browser(self, browser_type: BrowserType) -> BrowserTestResult:
        """Test a single browser for compatibility."""
        if browser_type not in self.browsers:
            return BrowserTestResult(
                browser_type=browser_type,
                version="unknown",
                platform=platform.system(),
                webgl_support=False,
                webgl_version="none",
                performance_score=0.0,
                errors=[f"Browser {browser_type.value} not available"],
                warnings=[],
                test_duration=0.0,
                viewport_tests={},
                feature_tests={}
            )

        start_time = time.time()
        browser = self.browsers[browser_type]
        context = browser.new_context()

        try:
            # Get browser version
            version = context.browser.version

            # Test WebGL support
            webgl_result = self.test_webgl_support(context)

            # Test performance
            perf_result = self.test_performance_metrics(context)

            # Test viewport responsiveness
            viewport_tests = self.test_viewport_responsiveness(context)

            # Test feature support
            feature_tests = self.test_feature_support(context)

            # Calculate performance score
            fps = perf_result.get("fps", 0)
            performance_score = min(fps / 60.0, 1.0)  # Normalize to 60 FPS baseline

            # Collect errors and warnings
            errors = []
            warnings = []

            if not webgl_result.get("supported", False):
                errors.append("WebGL not supported")

            if fps < 30:
                warnings.append(f"Low FPS: {fps:.1f}")

            if perf_result.get("error"):
                errors.append(f"Performance test error: {perf_result['error']}")

            test_duration = time.time() - start_time

            return BrowserTestResult(
                browser_type=browser_type,
                version=version,
                platform=platform.system(),
                webgl_support=webgl_result.get("supported", False),
                webgl_version=webgl_result.get("version", "none"),
                performance_score=performance_score,
                errors=errors,
                warnings=warnings,
                test_duration=test_duration,
                viewport_tests=viewport_tests,
                feature_tests=feature_tests
            )

        except Exception as e:
            test_duration = time.time() - start_time

            return BrowserTestResult(
                browser_type=browser_type,
                version="unknown",
                platform=platform.system(),
                webgl_support=False,
                webgl_version="error",
                performance_score=0.0,
                errors=[str(e)],
                warnings=[],
                test_duration=test_duration,
                viewport_tests={},
                feature_tests={}
            )

        finally:
            context.close()

    def run_compatibility_tests(self) -> CompatibilityReport:
        """Run complete compatibility test suite."""
        print("🌐 Running Cross-Browser Compatibility Tests...")

        if not self.initialize_browsers():
            return CompatibilityReport(
                timestamp=time.time(),
                overall_score=0.0,
                total_browsers_tested=0,
                compatible_browsers=0,
                results=[],
                recommendations=["Install Playwright for browser testing"]
            )

        # Test all available browsers
        for browser_type in self.browsers.keys():
            print(f"  Testing {browser_type.value}...")
            result = self.test_single_browser(browser_type)
            self.test_results.append(result)

            status = "✅" if result.webgl_support and result.performance_score > 0.5 else "⚠️"
            print(f"    {status} {result.browser_type.value} {result.version}")
            if result.errors:
                print(f"      Errors: {', '.join(result.errors)}")
            if result.warnings:
                print(f"      Warnings: {', '.join(result.warnings)}")

        # Calculate overall score
        total_browsers = len(self.test_results)
        compatible_browsers = sum(
            1 for result in self.test_results
            if result.webgl_support and result.performance_score > 0.3
        )

        overall_score = compatible_browsers / total_browsers if total_browsers > 0 else 0.0

        # Generate recommendations
        recommendations = self._generate_recommendations()

        # Cleanup
        for browser in self.browsers.values():
            browser.close()
        if self.playwright:
            self.playwright.stop()

        return CompatibilityReport(
            timestamp=time.time(),
            overall_score=overall_score,
            total_browsers_tested=total_browsers,
            compatible_browsers=compatible_browsers,
            results=self.test_results,
            recommendations=recommendations
        )

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []

        if not self.test_results:
            return ["No browser tests completed"]

        # Analyze results
        webgl_failures = sum(1 for r in self.test_results if not r.webgl_support)
        performance_issues = sum(1 for r in self.test_results if r.performance_score < 0.5)

        if webgl_failures > 0:
            recommendations.append(
                f"WebGL not supported in {webgl_failures} browser(s). "
                "Consider providing fallback 2D visualization."
            )

        if performance_issues > 0:
            recommendations.append(
                f"Performance issues detected in {performance_issues} browser(s). "
                "Consider reducing 3D complexity for better compatibility."
            )

        # Check viewport test results
        all_viewport_tests = {}
        for result in self.test_results:
            for viewport, passed in result.viewport_tests.items():
                if viewport not in all_viewport_tests:
                    all_viewport_tests[viewport] = []
                all_viewport_tests[viewport].append(passed)

        for viewport, results in all_viewport_tests.items():
            if not all(results):
                recommendations.append(
                    f"Viewport issues detected for {viewport} resolution. "
                    "Test responsive design thoroughly."
                )

        if not recommendations:
            recommendations.append("All browsers tested show good compatibility!")

        return recommendations

def run_browser_compatibility_tests() -> CompatibilityReport:
    """Run complete browser compatibility test suite."""
    tester = BrowserCompatibilityTester()
    return tester.run_compatibility_tests()

def generate_compatibility_report(report: CompatibilityReport) -> str:
    """Generate a human-readable compatibility report."""
    lines = []
    lines.append("=" * 80)
    lines.append("🌐 BROWSER COMPATIBILITY REPORT")
    lines.append("=" * 80)

    lines.append(f"Generated: {time.ctime(report.timestamp)}")
    lines.append(f"Overall Score: {report.overall_score*100:.1f}%")
    lines.append(f"Browsers Tested: {report.total_browsers_tested}")
    lines.append(f"Fully Compatible: {report.compatible_browsers}")
    lines.append("")

    if report.results:
        lines.append("DETAILED RESULTS:")
        lines.append("-" * 40)

        for result in report.results:
            status = "✅" if result.webgl_support and result.performance_score > 0.5 else "⚠️"
            lines.append(f"{status} {result.browser_type.value} {result.version}")
            lines.append(f"  Platform: {result.platform}")
            lines.append(f"  WebGL: {result.webgl_version}")
            lines.append(f"  Performance Score: {result.performance_score*100:.1f}%")
            lines.append(f"  Test Duration: {result.test_duration:.2f}s")

            if result.errors:
                lines.append(f"  Errors: {', '.join(result.errors)}")
            if result.warnings:
                lines.append(f"  Warnings: {', '.join(result.warnings)}")

            lines.append("")

    if report.recommendations:
        lines.append("RECOMMENDATIONS:")
        lines.append("-" * 40)
        for rec in report.recommendations:
            lines.append(f"• {rec}")
        lines.append("")

    # Save to file
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"browser_compatibility_report_{timestamp}.txt"

    with open(filename, 'w') as f:
        f.write('\n'.join(lines))

    lines.append(f"\n📄 Report saved to: {filename}")

    return '\n'.join(lines)

if __name__ == "__main__":
    print("🌐 Starting Browser Compatibility Tests...")

    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright not available. Install with:")
        print("   pip install playwright")
        print("   playwright install")
        sys.exit(1)

    report = run_browser_compatibility_tests()
    output = generate_compatibility_report(report)
    print(output)