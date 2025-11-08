#!/usr/bin/env python3
"""
Environment Validation Script

Validates environment variable configuration for both frontend and backend services.
Tests proper loading of environment variables and basic connectivity.

Author: Kilo Code
Date: November 2, 2025
"""

import os
import sys
import json
import requests
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# Color output for better readability
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

@dataclass
class ValidationResult:
    name: str
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None

def print_header(title: str):
    """Print formatted header."""
    separator = "=" * 60
    print(f"\n{Colors.BOLD}{Colors.CYAN}{separator}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}  {title}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{separator}{Colors.END}\n")

def print_result(result: ValidationResult):
    """Print validation result."""
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if result.success else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"{Colors.BOLD}{result.name}:{Colors.END} {status}")
    print(f"   {result.message}")
    if result.details:
        for key, value in result.details.items():
            print(f"   {Colors.PURPLE}{key}:{Colors.END} {value}")

def validate_backend_environment() -> List[ValidationResult]:
    """Validate backend environment variables."""
    results = []
    
    print_header("Backend Environment Validation")
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Load environment variables using dotenv
    try:
        from dotenv import load_dotenv
        env_file = backend_dir / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            print(f"{Colors.GREEN}✓{Colors.END} Loaded .env file: {env_file}")
        else:
            print(f"{Colors.RED}✗{Colors.END} .env file not found: {env_file}")
    except ImportError:
        print(f"{Colors.YELLOW}⚠{Colors.END} python-dotenv not available, skipping .env loading")
    except Exception as e:
        print(f"{Colors.RED}✗{Colors.END} Error loading .env file: {e}")
    
    # Required environment variables
    required_vars = {
        'ENVIRONMENT': 'development',
        'BACKEND_PORT': '8000',
        'DATABASE_PATH': 'ledger.db',
        'SIMULATION_NUM_AGENTS': '100',
        'SIMULATION_DEFAULT_AGENTS': '50',
        'SIMULATION_DEFAULT_STEPS': '100',
        'JWT_SECRET': None,  # Should exist but value doesn't matter
        'ENCRYPTION_KEY': None,  # Should exist but value doesn't matter
        'LOG_LEVEL': 'INFO'
    }
    
    for var_name, expected_value in required_vars.items():
        actual_value = os.getenv(var_name)
        if actual_value:
            if expected_value is None or actual_value == expected_value:
                results.append(ValidationResult(
                    name=f"Environment variable {var_name}",
                    success=True,
                    message="Loaded successfully",
                    details={"value": actual_value[:50] + "..." if len(actual_value) > 50 else actual_value}
                ))
            else:
                results.append(ValidationResult(
                    name=f"Environment variable {var_name}",
                    success=False,
                    message=f"Value mismatch (expected: {expected_value}, actual: {actual_value})"
                ))
        else:
            results.append(ValidationResult(
                name=f"Environment variable {var_name}",
                success=False,
                message="Environment variable not found"
            ))
    
    # Check CORS configuration
    cors_origins = os.getenv('BACKEND_CORS_ORIGINS')
    if cors_origins:
        try:
            origins_list = json.loads(cors_origins.replace("'", '"'))
            has_frontend = any('localhost:3000' in origin for origin in origins_list)
            results.append(ValidationResult(
                name="CORS Frontend Configuration",
                success=has_frontend,
                message=f"CORS configured with {len(origins_list)} origins" + (" (includes frontend)" if has_frontend else " (missing frontend)"),
                details={"origins": origins_list}
            ))
        except Exception as e:
            results.append(ValidationResult(
                name="CORS Frontend Configuration",
                success=False,
                message=f"Invalid CORS configuration: {e}"
            ))
    else:
        results.append(ValidationResult(
            name="CORS Frontend Configuration",
            success=False,
            message="CORS origins not configured"
        ))
    
    return results

def validate_frontend_environment() -> List[ValidationResult]:
    """Validate frontend environment variables."""
    results = []
    
    print_header("Frontend Environment Validation")
    
    # Change to frontend directory
    frontend_dir = Path(__file__).parent.parent / "frontend"
    os.chdir(frontend_dir)
    
    # Load environment variables
    env_file = frontend_dir / ".env"
    env_vars = {}
    
    if env_file.exists():
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key] = value
            print(f"{Colors.GREEN}✓{Colors.END} Loaded .env file: {env_file}")
        except Exception as e:
            print(f"{Colors.RED}✗{Colors.END} Error loading .env file: {e}")
    else:
        print(f"{Colors.RED}✗{Colors.END} .env file not found: {env_file}")
    
    # Required environment variables
    required_vars = {
        'REACT_APP_API_URL': 'http://localhost:8000',
        'REACT_APP_WEBSOCKET_URL': 'ws://localhost:8000/ws/simulation',
        'NODE_ENV': 'development',
        'VITE_API_URL': 'http://localhost:8000',
        'VITE_WEBSOCKET_URL': 'ws://localhost:8000/ws/simulation'
    }
    
    for var_name, expected_value in required_vars.items():
        actual_value = env_vars.get(var_name)
        if actual_value:
            if actual_value == expected_value:
                results.append(ValidationResult(
                    name=f"Environment variable {var_name}",
                    success=True,
                    message="Configured correctly",
                    details={"value": actual_value}
                ))
            else:
                results.append(ValidationResult(
                    name=f"Environment variable {var_name}",
                    success=False,
                    message=f"Value mismatch (expected: {expected_value}, actual: {actual_value})"
                ))
        else:
            results.append(ValidationResult(
                name=f"Environment variable {var_name}",
                success=False,
                message="Environment variable not found"
            ))
    
    # Check API URL configuration matches backend
    frontend_api = env_vars.get('REACT_APP_API_URL')
    if frontend_api == 'http://localhost:8000':
        results.append(ValidationResult(
            name="Frontend-Backend API URL Match",
            success=True,
            message="Frontend API URL matches backend URL",
            details={"backend_url": frontend_api}
        ))
    else:
        results.append(ValidationResult(
            name="Frontend-Backend API URL Match",
            success=False,
            message="Frontend API URL doesn't match expected backend URL",
            details={"frontend_api": frontend_api, "expected": "http://localhost:8000"}
        ))
    
    return results

def test_backend_connectivity() -> List[ValidationResult]:
    """Test backend connectivity."""
    results = []
    
    print_header("Backend Connectivity Test")
    
    backend_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            results.append(ValidationResult(
                name="Backend Health Check",
                success=True,
                message="Backend is responding",
                details={"status": health_data.get("status", "unknown")}
            ))
        else:
            results.append(ValidationResult(
                name="Backend Health Check",
                success=False,
                message=f"Health endpoint returned status {response.status_code}"
            ))
    except requests.exceptions.ConnectionError:
        results.append(ValidationResult(
            name="Backend Health Check",
            success=False,
            message="Backend is not running or not accessible"
        ))
    except Exception as e:
        results.append(ValidationResult(
            name="Backend Health Check",
            success=False,
            message=f"Error connecting to backend: {e}"
        ))
    
    return results

def test_frontend_config() -> List[ValidationResult]:
    """Test frontend configuration."""
    results = []
    
    print_header("Frontend Configuration Test")
    
    # Check if frontend can be built
    frontend_dir = Path(__file__).parent.parent / "frontend"
    os.chdir(frontend_dir)
    
    try:
        # Check if package.json exists
        package_json = frontend_dir / "package.json"
        if package_json.exists():
            with open(package_json, 'r') as f:
                package_data = json.load(f)
            
            results.append(ValidationResult(
                name="Frontend Package Configuration",
                success=True,
                message="Package.json found and valid",
                details={
                    "name": package_data.get("name"),
                    "version": package_data.get("version"),
                    "scripts": list(package_data.get("scripts", {}).keys())
                }
            ))
        else:
            results.append(ValidationResult(
                name="Frontend Package Configuration",
                success=False,
                message="package.json not found"
            ))
        
        # Check vite configuration
        vite_config = frontend_dir / "vite.config.ts"
        if vite_config.exists():
            results.append(ValidationResult(
                name="Vite Configuration",
                success=True,
                message="vite.config.ts found"
            ))
        else:
            results.append(ValidationResult(
                name="Vite Configuration",
                success=False,
                message="vite.config.ts not found"
            ))
            
    except Exception as e:
        results.append(ValidationResult(
            name="Frontend Configuration",
            success=False,
            message=f"Error checking frontend configuration: {e}"
        ))
    
    return results

def test_service_communication() -> List[ValidationResult]:
    """Test communication between services."""
    results = []
    
    print_header("Service Communication Test")
    
    # Test if frontend can connect to backend
    frontend_api_url = "http://localhost:8000"
    
    try:
        # Test API endpoint
        response = requests.get(f"{frontend_api_url}/agents", timeout=5)
        if response.status_code in [200, 401]:  # 401 is expected without auth
            results.append(ValidationResult(
                name="Frontend-Backend API Communication",
                success=True,
                message="Frontend can reach backend API",
                details={"status_code": response.status_code}
            ))
        else:
            results.append(ValidationResult(
                name="Frontend-Backend API Communication",
                success=False,
                message=f"Unexpected status code: {response.status_code}"
            ))
    except requests.exceptions.ConnectionError:
        results.append(ValidationResult(
            name="Frontend-Backend API Communication",
            success=False,
            message="Cannot connect to backend API"
        ))
    except Exception as e:
        results.append(ValidationResult(
            name="Frontend-Backend API Communication",
            success=False,
            message=f"Error testing API communication: {e}"
        ))
    
    # Test WebSocket endpoint
    try:
        import websockets
        import asyncio
        
        async def test_websocket():
            try:
                async with websockets.connect("ws://localhost:8000/ws/simulation") as websocket:
                    await websocket.send(json.dumps({"type": "ping"}))
                    response = await asyncio.wait_for(websocket.recv(), timeout=5)
                    return True
            except Exception:
                return False
        
        # Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        ws_success = loop.run_until_complete(test_websocket())
        loop.close()
        
        results.append(ValidationResult(
            name="WebSocket Communication",
            success=ws_success,
            message="WebSocket connection " + ("successful" if ws_success else "failed")
        ))
        
    except ImportError:
        results.append(ValidationResult(
            name="WebSocket Communication",
            success=False,
            message="websockets library not available for testing"
        ))
    except Exception as e:
        results.append(ValidationResult(
            name="WebSocket Communication",
            success=False,
            message=f"Error testing WebSocket: {e}"
        ))
    
    return results

def generate_summary(all_results: List[ValidationResult]) -> None:
    """Generate summary of all validation results."""
    print_header("Validation Summary")
    
    total_tests = len(all_results)
    passed_tests = sum(1 for result in all_results if result.success)
    failed_tests = total_tests - passed_tests
    
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"{Colors.BOLD}Total Tests:{Colors.END} {total_tests}")
    print(f"{Colors.GREEN}Passed:{Colors.END} {passed_tests}")
    print(f"{Colors.RED}Failed:{Colors.END} {failed_tests}")
    print(f"{Colors.BOLD}Success Rate:{Colors.END} {success_rate:.1f}%")
    
    if failed_tests > 0:
        print(f"\n{Colors.RED}{Colors.BOLD}Failed Tests:{Colors.END}")
        for result in all_results:
            if not result.success:
                print(f"  • {result.name}: {result.message}")
    
    # Recommendations
    print(f"\n{Colors.CYAN}{Colors.BOLD}Recommendations:{Colors.END}")
    if failed_tests == 0:
        print(f"{Colors.GREEN}✓ All tests passed! Environment is properly configured.{Colors.END}")
    else:
        print(f"{Colors.YELLOW}• Review failed tests and update configuration accordingly{Colors.END}")
        print(f"{Colors.YELLOW}• Ensure backend service is running before testing connectivity{Colors.END}")
        print(f"{Colors.YELLOW}• Verify both .env files are in the correct locations{Colors.END}")

def main():
    """Main validation function."""
    print(f"{Colors.BOLD}{Colors.CYAN}{Colors.UNDERLINE}")
    print("Environment Variable Configuration Validation")
    print(f"3D AI Simulation Platform{Colors.END}")
    print(f"Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all validations
    all_results = []
    
    # Backend validation
    backend_results = validate_backend_environment()
    all_results.extend(backend_results)
    
    # Frontend validation
    frontend_results = validate_frontend_environment()
    all_results.extend(frontend_results)
    
    # Backend connectivity test
    backend_connectivity_results = test_backend_connectivity()
    all_results.extend(backend_connectivity_results)
    
    # Frontend configuration test
    frontend_config_results = test_frontend_config()
    all_results.extend(frontend_config_results)
    
    # Service communication test
    communication_results = test_service_communication()
    all_results.extend(communication_results)
    
    # Print all results
    print_header("Detailed Results")
    for result in all_results:
        print_result(result)
    
    # Generate summary
    generate_summary(all_results)
    
    # Exit with appropriate code
    failed_count = sum(1 for result in all_results if not result.success)
    sys.exit(0 if failed_count == 0 else 1)

if __name__ == "__main__":
    main()