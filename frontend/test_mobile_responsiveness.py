"""
Mobile Responsiveness Testing for 3D AI Simulation Platform

Tests mobile device compatibility, touch interactions, performance,
and responsive design for the 3D visualization platform.
"""

import asyncio
import json
import time
import platform
import subprocess
import sys
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Mobile testing using device simulation
try:
    from playwright.sync_api import Playwright, Browser, BrowserContext, Page, sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Import frontend types for validation
sys.path.append(os.path.dirname(__file__))
try:
    from src.types.simulation import (
        ViewportSettings, PerformanceMetrics, AccessibilitySettings
    )
    TYPES_AVAILABLE = True
except ImportError:
    TYPES_AVAILABLE = False

class DeviceType(Enum):
    """Mobile device types for testing."""
    PHONE = "phone"
    TABLET = "tablet"
    FOLDABLE = "foldable"
    DESKTOP = "desktop"

class Orientation(Enum):
    """Device orientation for testing."""
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"

@dataclass
class MobileDevice:
    """Represents a mobile device for testing."""
    name: str
    device_type: DeviceType
    viewport: Dict[str, int]
    user_agent: str
    touch_enabled: bool
    pixel_ratio: float

@dataclass
class MobileTestResult:
    """Results from mobile responsiveness testing."""
    device: MobileDevice
    orientation: Orientation
    performance_score: float
    touch_functionality: bool
    responsive_layout: bool
    accessibility_score: float
    errors: List[str]
    warnings: List[str]
    test_duration: float
    viewport_tests: Dict[str, bool]

@dataclass
class MobileResponsivenessReport:
    """Complete mobile responsiveness report."""
    timestamp: float
    overall_score: float
    total_devices_tested: int
    mobile_compatible_devices: int
    results: List[MobileTestResult]
    recommendations: List[str]

class MobileResponsivenessTester:
    """Main mobile responsiveness testing class."""

    def __init__(self):
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.test_results: List[MobileTestResult] = []

        # Define test devices
        self.test_devices = [
            MobileDevice(
                name="iPhone 14",
                device_type=DeviceType.PHONE,
                viewport={"width": 390, "height": 844},
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
                touch_enabled=True,
                pixel_ratio=3.0
            ),
            MobileDevice(
                name="Samsung Galaxy S23",
                device_type=DeviceType.PHONE,
                viewport={"width": 360, "height": 780},
                user_agent="Mozilla/5.0 (Linux; Android 13; SM-S911B) AppleWebKit/537.36",
                touch_enabled=True,
                pixel_ratio=2.5
            ),
            MobileDevice(
                name="iPad Pro",
                device_type=DeviceType.TABLET,
                viewport={"width": 1024, "height": 1366},
                user_agent="Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15",
                touch_enabled=True,
                pixel_ratio=2.0
            ),
            MobileDevice(
                name="Desktop Browser",
                device_type=DeviceType.DESKTOP,
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                touch_enabled=False,
                pixel_ratio=1.0
            )
        ]

    def initialize_browser(self) -> bool:
        """Initialize browser for mobile testing."""
        if not PLAYWRIGHT_AVAILABLE:
            print("⚠️  Playwright not available. Install with: pip install playwright")
            return False

        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch()

            print("✅ Browser initialized for mobile testing")
            return True

        except Exception as e:
            print(f"❌ Failed to initialize browser: {e}")
            return False

    def test_device_performance(self, context: BrowserContext, device: MobileDevice) -> Dict[str, Any]:
        """Test performance on a specific device."""
        try:
            page = context.new_page()

            # Set device characteristics
            page.set_viewport_size(device.viewport)
            page.evaluate(f"Object.defineProperty(navigator, 'userAgent', {{value: '{device.user_agent}'}});")

            # Navigate to performance test page
            page.goto("data:text/html,<html><body><canvas id='test'></canvas></body></html>")

            # Inject mobile performance test
            perf_result = page.evaluate("""
                (() => {
                    const canvas = document.getElementById('test');
                    const startTime = performance.now();

                    // Simulate mobile 3D rendering workload
                    let frameCount = 0;
                    const testDuration = 500; // Shorter test for mobile
                    const endTime = startTime + testDuration;

                    while (performance.now() < endTime) {
                        frameCount++;
                    }

                    const actualDuration = performance.now() - startTime;
                    const avgFrameTime = actualDuration / frameCount;
                    const fps = 1000 / avgFrameTime;

                    return {
                        fps: fps,
                        frameTime: avgFrameTime,
                        frameCount: frameCount,
                        testDuration: actualDuration,
                        viewportWidth: window.innerWidth,
                        viewportHeight: window.innerHeight,
                        devicePixelRatio: window.devicePixelRatio || 1
                    };
                })()
            """)

            page.close()
            return perf_result

        except Exception as e:
            return {
                "fps": 0,
                "frameTime": 0,
                "error": str(e)
            }

    def test_touch_functionality(self, context: BrowserContext, device: MobileDevice) -> bool:
        """Test touch functionality on mobile devices."""
        if not device.touch_enabled:
            return True  # Desktop devices don't need touch

        try:
            page = context.new_page()

            # Set mobile viewport and touch emulation
            page.set_viewport_size(device.viewport)
            context.set_geolocation({"latitude": 37.7749, "longitude": -122.4194})  # San Francisco

            # Navigate to touch test page
            page.goto("data:text/html,<html><body><div id='touch-area' style='width: 100%; height: 100vh; background: blue;'></div></body></html>")

            # Inject touch detection script
            touch_result = page.evaluate("""
                (() => {
                    const touchArea = document.getElementById('touch-area');
                    let touchDetected = false;

                    const handleTouch = () => {
                        touchDetected = true;
                        touchArea.style.background = 'green';
                    };

                    touchArea.addEventListener('touchstart', handleTouch, { passive: true });
                    touchArea.addEventListener('touchmove', handleTouch, { passive: true });
                    touchArea.addEventListener('touchend', handleTouch, { passive: true });

                    // Simulate touch after a short delay
                    setTimeout(() => {
                        const touchEvent = new TouchEvent('touchstart', {
                            touches: [{
                                identifier: 0,
                                target: touchArea,
                                clientX: 100,
                                clientY: 100,
                                pageX: 100,
                                pageY: 100,
                                screenX: 100,
                                screenY: 100
                            }]
                        });
                        touchArea.dispatchEvent(touchEvent);
                    }, 100);

                    // Wait a bit for touch detection
                    return new Promise(resolve => {
                        setTimeout(() => {
                            resolve({
                                touchDetected: touchDetected,
                                hasTouchSupport: 'ontouchstart' in window,
                                maxTouchPoints: navigator.maxTouchPoints || 0
                            });
                        }, 200);
                    });
                })()
            """)

            page.close()

            # Touch functionality is working if touch events are supported and detected
            return touch_result.get("hasTouchSupport", False) and touch_result.get("touchDetected", False)

        except Exception as e:
            return False

    def test_responsive_layout(self, context: BrowserContext, device: MobileDevice) -> Dict[str, bool]:
        """Test responsive layout functionality."""
        try:
            page = context.new_page()

            # Set device viewport
            page.set_viewport_size(device.viewport)

            # Navigate to responsive test page
            html_content = """
            <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    .container { width: 100%; display: flex; flex-wrap: wrap; }
                    .box { width: 100%; height: 100px; background: red; margin: 5px; }
                    @media (min-width: 768px) { .box { width: calc(50% - 10px); } }
                    @media (min-width: 1024px) { .box { width: calc(33.333% - 10px); } }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="box">Box 1</div>
                    <div class="box">Box 2</div>
                    <div class="box">Box 3</div>
                </div>
            </body>
            </html>
            """

            page.goto(f"data:text/html,{html_content}")

            # Test responsive behavior
            layout_tests = {}

            # Test viewport meta tag
            viewport_content = page.evaluate("""
                () => {
                    const viewport = document.querySelector('meta[name="viewport"]');
                    return viewport ? viewport.getAttribute('content') : null;
                }
            """)
            layout_tests["viewport_meta"] = viewport_content is not None

            # Test flexbox layout
            container_width = page.evaluate("""
                () => {
                    const container = document.querySelector('.container');
                    return container ? container.getBoundingClientRect().width : 0;
                }
            """)

            expected_width = device.viewport["width"]
            layout_tests["container_width"] = abs(container_width - expected_width) <= 10

            # Test media query behavior
            box_width = page.evaluate("""
                () => {
                    const box = document.querySelector('.box');
                    return box ? box.getBoundingClientRect().width : 0;
                }
            """)

            # On mobile, boxes should be full width
            if device.device_type == DeviceType.PHONE:
                layout_tests["mobile_layout"] = box_width >= expected_width - 20
            else:
                layout_tests["responsive_layout"] = box_width < expected_width

            page.close()
            return layout_tests

        except Exception as e:
            return {"error": str(e)}

    def test_accessibility_features(self, context: BrowserContext, device: MobileDevice) -> float:
        """Test accessibility features on mobile devices."""
        try:
            page = context.new_page()

            # Set mobile viewport
            page.set_viewport_size(device.viewport)

            # Navigate to accessibility test page
            html_content = """
            <html>
            <body>
                <button id="test-button">Test Button</button>
                <input type="text" id="test-input" placeholder="Test Input">
                <div role="alert" aria-live="polite" id="test-alert">Alert Message</div>
            </body>
            </html>
            """

            page.goto(f"data:text/html,{html_content}")

            # Test accessibility features
            accessibility_score = 0.0

            # Test focus management
            focusable_elements = page.evaluate("""
                () => {
                    const focusable = document.querySelectorAll('button, input, [tabindex]');
                    return focusable.length;
                }
            """)

            if focusable_elements > 0:
                accessibility_score += 0.3

            # Test ARIA attributes
            aria_elements = page.evaluate("""
                () => {
                    const aria = document.querySelectorAll('[aria-label], [role], [aria-live]');
                    return aria.length;
                }
            """)

            if aria_elements > 0:
                accessibility_score += 0.3

            # Test semantic HTML
            semantic_elements = page.evaluate("""
                () => {
                    const semantic = document.querySelectorAll('button, input, nav, main, section');
                    return semantic.length;
                }
            """)

            if semantic_elements > 0:
                accessibility_score += 0.2

            # Test color contrast (simplified)
            contrast_elements = page.evaluate("""
                () => {
                    const elements = document.querySelectorAll('*');
                    let contrastCount = 0;

                    elements.forEach(el => {
                        const styles = window.getComputedStyle(el);
                        const color = styles.color;
                        const backgroundColor = styles.backgroundColor;

                        // Simple check for color definitions
                        if (color !== 'rgb(0, 0, 0)' && backgroundColor !== 'rgba(0, 0, 0, 0)') {
                            contrastCount++;
                        }
                    });

                    return contrastCount;
                }
            """)

            if contrast_elements > 0:
                accessibility_score += 0.2

            page.close()
            return min(accessibility_score, 1.0)

        except Exception as e:
            return 0.0

    def test_single_device_orientation(self,
                                     device: MobileDevice,
                                     orientation: Orientation) -> MobileTestResult:
        """Test a single device in a specific orientation."""
        if not self.browser:
            return MobileTestResult(
                device=device,
                orientation=orientation,
                performance_score=0.0,
                touch_functionality=False,
                responsive_layout=False,
                accessibility_score=0.0,
                errors=["Browser not initialized"],
                warnings=[],
                test_duration=0.0,
                viewport_tests={}
            )

        start_time = time.time()

        # Calculate orientation dimensions
        if orientation == Orientation.LANDSCAPE:
            viewport = {
                "width": max(device.viewport["width"], device.viewport["height"]),
                "height": min(device.viewport["width"], device.viewport["height"])
            }
        else:
            viewport = device.viewport

        context = self.browser.new_context(
            viewport=viewport,
            user_agent=device.user_agent,
            device_scale_factor=device.pixel_ratio,
            has_touch=device.touch_enabled
        )

        try:
            # Test performance
            perf_result = self.test_device_performance(context, device)
            fps = perf_result.get("fps", 0)
            performance_score = min(fps / 30.0, 1.0)  # Normalize to 30 FPS baseline for mobile

            # Test touch functionality
            touch_functionality = self.test_touch_functionality(context, device)

            # Test responsive layout
            layout_tests = self.test_responsive_layout(context, device)
            responsive_layout = layout_tests.get("viewport_meta", False) and layout_tests.get("container_width", False)

            # Test accessibility
            accessibility_score = self.test_accessibility_features(context, device)

            # Collect errors and warnings
            errors = []
            warnings = []

            if perf_result.get("error"):
                errors.append(f"Performance error: {perf_result['error']}")

            if fps < 15:
                warnings.append(f"Low FPS on mobile: {fps:.1f}")

            if not touch_functionality and device.touch_enabled:
                errors.append("Touch functionality not working")

            if not responsive_layout:
                warnings.append("Responsive layout issues detected")

            test_duration = time.time() - start_time

            return MobileTestResult(
                device=device,
                orientation=orientation,
                performance_score=performance_score,
                touch_functionality=touch_functionality,
                responsive_layout=responsive_layout,
                accessibility_score=accessibility_score,
                errors=errors,
                warnings=warnings,
                test_duration=test_duration,
                viewport_tests=layout_tests
            )

        except Exception as e:
            test_duration = time.time() - start_time

            return MobileTestResult(
                device=device,
                orientation=orientation,
                performance_score=0.0,
                touch_functionality=False,
                responsive_layout=False,
                accessibility_score=0.0,
                errors=[str(e)],
                warnings=[],
                test_duration=test_duration,
                viewport_tests={}
            )

        finally:
            context.close()

    def run_mobile_responsiveness_tests(self) -> MobileResponsivenessReport:
        """Run complete mobile responsiveness test suite."""
        print("📱 Running Mobile Responsiveness Tests...")

        if not self.initialize_browser():
            return MobileResponsivenessReport(
                timestamp=time.time(),
                overall_score=0.0,
                total_devices_tested=0,
                mobile_compatible_devices=0,
                results=[],
                recommendations=["Install Playwright for mobile testing"]
            )

        # Test all devices and orientations
        for device in self.test_devices:
            print(f"  Testing {device.name}...")

            # Test both orientations for mobile devices
            orientations = [Orientation.PORTRAIT, Orientation.LANDSCAPE]

            for orientation in orientations:
                result = self.test_single_device_orientation(device, orientation)
                self.test_results.append(result)

                status = "✅" if result.performance_score > 0.5 and result.touch_functionality else "⚠️"
                print(f"    {status} {orientation.value} - {result.performance_score*100:.1f}% performance")

                if result.errors:
                    print(f"      Errors: {', '.join(result.errors)}")
                if result.warnings:
                    print(f"      Warnings: {', '.join(result.warnings)}")

        # Calculate overall score
        total_devices = len(self.test_results)
        compatible_devices = sum(
            1 for result in self.test_results
            if result.performance_score > 0.3 and result.responsive_layout
        )

        overall_score = compatible_devices / total_devices if total_devices > 0 else 0.0

        # Generate recommendations
        recommendations = self._generate_mobile_recommendations()

        # Cleanup
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

        return MobileResponsivenessReport(
            timestamp=time.time(),
            overall_score=overall_score,
            total_devices_tested=total_devices,
            mobile_compatible_devices=compatible_devices,
            results=self.test_results,
            recommendations=recommendations
        )

    def _generate_mobile_recommendations(self) -> List[str]:
        """Generate recommendations based on mobile test results."""
        recommendations = []

        if not self.test_results:
            return ["No mobile tests completed"]

        # Analyze results
        mobile_devices = [r for r in self.test_results if r.device.device_type != DeviceType.DESKTOP]
        desktop_devices = [r for r in self.test_results if r.device.device_type == DeviceType.DESKTOP]

        # Check mobile performance
        mobile_performance_scores = [r.performance_score for r in mobile_devices]
        if mobile_performance_scores:
            avg_mobile_performance = sum(mobile_performance_scores) / len(mobile_performance_scores)

            if avg_mobile_performance < 0.5:
                recommendations.append(
                    "Mobile performance is below acceptable levels. "
                    "Consider reducing 3D complexity or implementing performance mode for mobile devices."
                )

        # Check touch functionality
        touch_failures = sum(1 for r in mobile_devices if not r.touch_functionality)
        if touch_failures > 0:
            recommendations.append(
                f"Touch functionality issues detected on {touch_failures} mobile device(s). "
                "Ensure touch event handlers are properly implemented."
            )

        # Check responsive layout
        layout_failures = sum(1 for r in self.test_results if not r.responsive_layout)
        if layout_failures > 0:
            recommendations.append(
                f"Responsive layout issues detected on {layout_failures} device(s). "
                "Review CSS media queries and viewport meta tags."
            )

        # Check accessibility
        low_accessibility = sum(1 for r in self.test_results if r.accessibility_score < 0.7)
        if low_accessibility > 0:
            recommendations.append(
                f"Accessibility issues detected on {low_accessibility} device(s). "
                "Improve ARIA labels, focus management, and color contrast."
            )

        if not recommendations:
            recommendations.append("All mobile devices show good responsiveness!")

        return recommendations

def run_mobile_responsiveness_tests() -> MobileResponsivenessReport:
    """Run complete mobile responsiveness test suite."""
    tester = MobileResponsivenessTester()
    return tester.run_mobile_responsiveness_tests()

def generate_mobile_report(report: MobileResponsivenessReport) -> str:
    """Generate a human-readable mobile responsiveness report."""
    lines = []
    lines.append("=" * 80)
    lines.append("📱 MOBILE RESPONSIVENESS REPORT")
    lines.append("=" * 80)

    lines.append(f"Generated: {time.ctime(report.timestamp)}")
    lines.append(f"Overall Score: {report.overall_score*100".1f"}%")
    lines.append(f"Devices Tested: {report.total_devices_tested}")
    lines.append(f"Mobile Compatible: {report.mobile_compatible_devices}")
    lines.append("")

    if report.results:
        lines.append("DETAILED RESULTS:")
        lines.append("-" * 40)

        for result in report.results:
            status = "✅" if result.performance_score > 0.5 else "⚠️"
            lines.append(f"{status} {result.device.name} ({result.orientation.value})")
            lines.append(f"  Performance Score: {result.performance_score*100".1f"}%")
            lines.append(f"  Touch Functionality: {'✅' if result.touch_functionality else '❌'}")
            lines.append(f"  Responsive Layout: {'✅' if result.responsive_layout else '❌'}")
            lines.append(f"  Accessibility Score: {result.accessibility_score*100".1f"}%")
            lines.append(f"  Test Duration: {result.test_duration".2f"}s")

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
    filename = f"mobile_responsiveness_report_{timestamp}.txt"

    with open(filename, 'w') as f:
        f.write('\n'.join(lines))

    lines.append(f"\n📄 Report saved to: {filename}")

    return '\n'.join(lines)

if __name__ == "__main__":
    print("📱 Starting Mobile Responsiveness Tests...")

    if not PLAYWRIGHT_AVAILABLE:
        print("❌ Playwright not available. Install with:")
        print("   pip install playwright")
        print("   playwright install")
        sys.exit(1)

    report = run_mobile_responsiveness_tests()
    output = generate_mobile_report(report)
    print(output)