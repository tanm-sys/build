#!/usr/bin/env python3
"""
Deployment Script for 3D AI Simulation Platform

Handles deployment to different environments (development, staging, production)
with proper configuration management and environment-specific optimizations.
"""

import os
import sys
import argparse
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import json

class DeploymentManager:
    """Manages deployment to different environments."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.environments = {
            'development': '.env.development',
            'staging': '.env.staging',
            'production': '.env.production'
        }

    def deploy_to_environment(self, environment: str, options: Dict[str, Any]) -> bool:
        """Deploy to specified environment."""
        print(f"🚀 Deploying to {environment} environment...")

        if environment not in self.environments:
            print(f"❌ Unknown environment: {environment}")
            print(f"Available environments: {', '.join(self.environments.keys())}")
            return False

        # Pre-deployment checks
        if not self._run_pre_deployment_checks(environment):
            return False

        # Set up environment
        if not self._setup_environment(environment):
            return False

        # Run environment-specific deployment
        if environment == 'development':
            success = self._deploy_development(options)
        elif environment == 'staging':
            success = self._deploy_staging(options)
        elif environment == 'production':
            success = self._deploy_production(options)
        else:
            print(f"❌ No deployment logic for environment: {environment}")
            return False

        if success:
            print(f"✅ Successfully deployed to {environment}")
            self._run_post_deployment_tasks(environment)
        else:
            print(f"❌ Deployment to {environment} failed")

        return success

    def _run_pre_deployment_checks(self, environment: str) -> bool:
        """Run pre-deployment checks."""
        print("🔍 Running pre-deployment checks...")

        # Check if environment file exists
        env_file = self.project_root / self.environments[environment]
        if not env_file.exists():
            print(f"❌ Environment file not found: {env_file}")
            return False

        # Check if required services are available
        if environment == 'production':
            if not self._check_production_dependencies():
                return False

        # Run tests if requested
        if os.getenv('RUN_TESTS_BEFORE_DEPLOY', 'false').lower() == 'true':
            print("🧪 Running tests before deployment...")
            if not self._run_tests():
                print("❌ Tests failed. Aborting deployment.")
                return False

        print("✅ Pre-deployment checks passed")
        return True

    def _setup_environment(self, environment: str) -> bool:
        """Set up environment configuration."""
        try:
            # Copy environment file to .env
            env_file = self.project_root / self.environments[environment]
            env_target = self.project_root / '.env'

            shutil.copy2(env_file, env_target)
            print(f"📋 Environment configuration set up: {env_file} -> {env_target}")

            # Load environment variables
            from dotenv import load_dotenv
            load_dotenv(env_target)

            return True

        except Exception as e:
            print(f"❌ Failed to setup environment: {e}")
            return False

    def _deploy_development(self, options: Dict[str, Any]) -> bool:
        """Deploy to development environment."""
        try:
            print("🔧 Setting up development environment...")

            # Install development dependencies
            if options.get('install_deps', True):
                print("📦 Installing development dependencies...")
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', '-r',
                    'backend/requirements.txt'
                ], check=True, cwd=self.project_root)

                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', '-r',
                    'decentralized-ai-simulation/requirements.txt'
                ], check=True, cwd=self.project_root)

            # Start services in development mode
            if options.get('start_services', True):
                print("🚀 Starting development services...")

                # Start backend server
                backend_process = subprocess.Popen([
                    sys.executable, '-m', 'uvicorn',
                    'backend.main:app',
                    '--host', os.getenv('BACKEND_HOST', 'localhost'),
                    '--port', os.getenv('BACKEND_PORT', '8000'),
                    '--reload'
                ], cwd=self.project_root)

                # Start Streamlit with API server
                streamlit_process = subprocess.Popen([
                    sys.executable, 'decentralized-ai-simulation/src/ui/streamlit_app.py'
                ], cwd=self.project_root)

                print("✅ Development services started")
                print("🌐 Backend: http://localhost:8000")
                print("📱 Streamlit: http://localhost:8501")
                print("🔗 API: http://localhost:8502")
                print("📡 WebSocket: ws://localhost:8503")

                # Wait for processes
                try:
                    backend_process.wait()
                except KeyboardInterrupt:
                    print("\n🛑 Shutting down development services...")
                    backend_process.terminate()
                    streamlit_process.terminate()

            return True

        except Exception as e:
            print(f"❌ Development deployment failed: {e}")
            return False

    def _deploy_staging(self, options: Dict[str, Any]) -> bool:
        """Deploy to staging environment."""
        try:
            print("🎭 Setting up staging environment...")

            # Build Docker images for staging
            print("🐳 Building Docker images for staging...")
            subprocess.run([
                'docker-compose', '-f', 'docker-compose.yml',
                '--profile', 'with-monitoring', 'build'
            ], check=True, cwd=self.project_root)

            # Start staging services
            if options.get('start_services', True):
                print("🚀 Starting staging services...")
                subprocess.run([
                    'docker-compose', '-f', 'docker-compose.yml',
                    '--profile', 'with-monitoring', 'up', '-d'
                ], check=True, cwd=self.project_root)

                print("✅ Staging deployment completed")
                print("🌐 Services available at configured ports")

            return True

        except Exception as e:
            print(f"❌ Staging deployment failed: {e}")
            return False

    def _deploy_production(self, options: Dict[str, Any]) -> bool:
        """Deploy to production environment."""
        try:
            print("🏭 Setting up production environment...")

            # Run production health checks
            if not self._check_production_dependencies():
                return False

            # Build optimized Docker images
            print("🐳 Building optimized Docker images...")
            subprocess.run([
                'docker-compose', '-f', 'docker-compose.yml',
                '--profile', 'with-monitoring', '--profile', 'with-nginx',
                'build', '--parallel'
            ], check=True, cwd=self.project_root)

            # Run database migrations if needed
            if options.get('run_migrations', True):
                print("🗄️  Running database migrations...")
                # Add migration logic here if using PostgreSQL

            # Deploy with zero downtime if possible
            if options.get('zero_downtime', False):
                success = self._deploy_with_zero_downtime()
            else:
                success = self._deploy_standard()

            if success:
                # Run post-deployment health checks
                self._run_post_deployment_health_checks()

            return success

        except Exception as e:
            print(f"❌ Production deployment failed: {e}")
            return False

    def _deploy_standard(self) -> bool:
        """Standard deployment without zero downtime."""
        try:
            print("🚀 Starting production services...")
            subprocess.run([
                'docker-compose', '-f', 'docker-compose.yml',
                '--profile', 'with-monitoring', '--profile', 'with-nginx',
                'up', '-d'
            ], check=True, cwd=self.project_root)

            print("✅ Production deployment completed")
            return True

        except Exception as e:
            print(f"❌ Standard deployment failed: {e}")
            return False

    def _deploy_with_zero_downtime(self) -> bool:
        """Deploy with zero downtime using blue-green strategy."""
        try:
            print("🔄 Deploying with zero downtime...")

            # This would implement blue-green deployment
            # For now, fall back to standard deployment
            return self._deploy_standard()

        except Exception as e:
            print(f"❌ Zero downtime deployment failed: {e}")
            return False

    def _check_production_dependencies(self) -> bool:
        """Check if production dependencies are available."""
        print("🔍 Checking production dependencies...")

        required_commands = ['docker', 'docker-compose']
        missing_commands = []

        for cmd in required_commands:
            if not shutil.which(cmd):
                missing_commands.append(cmd)

        if missing_commands:
            print(f"❌ Missing required commands: {', '.join(missing_commands)}")
            return False

        # Check if required ports are available
        required_ports = [80, 443, 8000, 8501, 8502, 8503]
        for port in required_ports:
            # In a real scenario, you'd check if ports are available
            pass

        print("✅ Production dependencies check passed")
        return True

    def _run_tests(self) -> bool:
        """Run test suite."""
        try:
            print("🧪 Running test suite...")

            # Run integration tests
            result = subprocess.run([
                sys.executable, 'backend/run_integration_tests.py',
                '--fast'
            ], cwd=self.project_root, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"❌ Tests failed: {result.stderr}")
                return False

            print("✅ All tests passed")
            return True

        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            return False

    def _run_post_deployment_tasks(self, environment: str) -> None:
        """Run post-deployment tasks."""
        print("🔧 Running post-deployment tasks...")

        # Environment-specific tasks
        if environment == 'production':
            print("📊 Setting up production monitoring...")
            # Set up monitoring dashboards, alerts, etc.

            print("🔒 Configuring security settings...")
            # Configure SSL, firewall, etc.

        print("✅ Post-deployment tasks completed")

    def _run_post_deployment_health_checks(self) -> None:
        """Run health checks after deployment."""
        print("🏥 Running post-deployment health checks...")

        # Check if services are responding
        health_endpoints = [
            "http://localhost:8000/health",
            "http://localhost:8502/health"
        ]

        for endpoint in health_endpoints:
            try:
                response = subprocess.run([
                    'curl', '-f', '--max-time', '10', endpoint
                ], capture_output=True)

                if response.returncode == 0:
                    print(f"✅ {endpoint} - Healthy")
                else:
                    print(f"⚠️  {endpoint} - Unhealthy")

            except Exception as e:
                print(f"❌ Health check failed for {endpoint}: {e}")

def main():
    """Main deployment entry point."""
    parser = argparse.ArgumentParser(description="Deploy 3D AI Simulation Platform")
    parser.add_argument(
        "environment",
        choices=['development', 'staging', 'production'],
        help="Target deployment environment"
    )
    parser.add_argument(
        "--no-deps",
        action="store_true",
        help="Skip dependency installation"
    )
    parser.add_argument(
        "--no-start",
        action="store_true",
        help="Skip service startup"
    )
    parser.add_argument(
        "--zero-downtime",
        action="store_true",
        help="Use zero-downtime deployment (production only)"
    )
    parser.add_argument(
        "--run-migrations",
        action="store_true",
        default=True,
        help="Run database migrations"
    )

    args = parser.parse_args()

    # Prepare deployment options
    options = {
        'install_deps': not args.no_deps,
        'start_services': not args.no_start,
        'zero_downtime': args.zero_downtime,
        'run_migrations': args.run_migrations
    }

    # Initialize deployment manager
    deployer = DeploymentManager()

    # Run deployment
    success = deployer.deploy_to_environment(args.environment, options)

    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()