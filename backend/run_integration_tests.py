#!/usr/bin/env python3
"""
Integration Test Runner for 3D AI Simulation Platform

Runs comprehensive integration tests for the complete system including
backend, API endpoints, WebSocket streaming, and data transformation.
"""

import subprocess
import sys
import os
import time
import argparse
from typing import List, Dict, Any
import json

class IntegrationTestRunner:
    """Manages and runs integration tests for the platform."""

    def __init__(self):
        self.test_results: Dict[str, Any] = {}
        self.start_time = time.time()

    def run_test_suite(self, test_files: List[str], verbose: bool = False) -> Dict[str, Any]:
        """Run a suite of integration tests."""
        print("🚀 Starting Integration Test Suite for 3D AI Simulation Platform")
        print("=" * 70)

        for test_file in test_files:
            print(f"\n📋 Running {test_file}...")
            self._run_single_test_file(test_file, verbose)

        # Generate summary report
        self._generate_summary_report()
        return self.test_results

    def _run_single_test_file(self, test_file: str, verbose: bool = False) -> None:
        """Run a single test file and capture results."""
        try:
            cmd = [sys.executable, "-m", "pytest", test_file, "-v" if verbose else "-q"]

            if verbose:
                cmd.append("--tb=short")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            # Parse results
            self.test_results[test_file] = {
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }

            if result.returncode == 0:
                print(f"✅ {test_file} - PASSED")
            else:
                print(f"❌ {test_file} - FAILED")

            if verbose and result.stdout:
                print(result.stdout)

            if result.stderr:
                print(f"Warnings/Errors: {result.stderr}")

        except subprocess.TimeoutExpired:
            print(f"⏰ {test_file} - TIMEOUT")
            self.test_results[test_file] = {
                "return_code": -1,
                "stdout": "",
                "stderr": "Test timeout",
                "success": False
            }
        except Exception as e:
            print(f"💥 {test_file} - ERROR: {e}")
            self.test_results[test_file] = {
                "return_code": -2,
                "stdout": "",
                "stderr": str(e),
                "success": False
            }

    def _generate_summary_report(self) -> None:
        """Generate a summary report of test results."""
        total_time = time.time() - self.start_time

        print("\n" + "=" * 70)
        print("📊 INTEGRATION TEST SUMMARY")
        print("=" * 70)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result["success"])
        failed_tests = total_tests - passed_tests

        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "N/A")
        print(f"Total Time: {total_time:.2f} seconds")

        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for test_file, result in self.test_results.items():
                if not result["success"]:
                    print(f"  - {test_file}: {result.get('stderr', 'Unknown error')}")

        print("\n" + "=" * 70)

        # Save detailed results to file
        self._save_detailed_results()

    def _save_detailed_results(self) -> None:
        """Save detailed test results to a JSON file."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"integration_test_results_{timestamp}.json"

        try:
            with open(filename, 'w') as f:
                json.dump({
                    "summary": {
                        "total_tests": len(self.test_results),
                        "passed_tests": sum(1 for r in self.test_results.values() if r["success"]),
                        "failed_tests": sum(1 for r in self.test_results.values() if not r["success"]),
                        "total_time": time.time() - self.start_time
                    },
                    "results": self.test_results
                }, f, indent=2)

            print(f"📄 Detailed results saved to: {filename}")

        except Exception as e:
            print(f"⚠️  Could not save detailed results: {e}")

def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(description="Run integration tests for 3D AI Simulation Platform")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fast", "-f", action="store_true", help="Run only fast tests")
    parser.add_argument("--backend-only", action="store_true", help="Run only backend tests")
    parser.add_argument("--api-only", action="store_true", help="Run only API tests")

    args = parser.parse_args()

    # Define test suites
    all_tests = [
        "test_integration.py",
        "../decentralized-ai-simulation/tests/integration/test_api_integration.py"
    ]

    backend_tests = [
        "test_integration.py"
    ]

    api_tests = [
        "../decentralized-ai-simulation/tests/integration/test_api_integration.py"
    ]

    # Select test suite based on arguments
    if args.backend_only:
        test_files = backend_tests
        print("🔧 Running Backend Integration Tests Only")
    elif args.api_only:
        test_files = api_tests
        print("🌐 Running API Integration Tests Only")
    else:
        test_files = all_tests
        print("🚀 Running Complete Integration Test Suite")

    # Change to backend directory for relative imports
    os.chdir(os.path.dirname(__file__))

    # Run tests
    runner = IntegrationTestRunner()
    results = runner.run_test_suite(test_files, args.verbose)

    # Exit with appropriate code
    failed_tests = sum(1 for result in results.values() if not result["success"])
    sys.exit(1 if failed_tests > 0 else 0)

if __name__ == "__main__":
    main()