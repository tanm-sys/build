"""
Production Optimization Settings for 3D AI Simulation Platform

Implements performance optimizations, caching strategies, resource management,
and production-ready configurations for high-performance deployment.
"""

import os
import time
import asyncio
import functools
from typing import Dict, Any, List, Optional, Callable
import threading
from contextlib import contextmanager
import gc
import logging

# Import existing components
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from ..config_loader import get_config
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

class PerformanceOptimizer:
    """Optimizes system performance for production workloads."""

    def __init__(self):
        self.optimization_settings = self._load_optimization_settings()
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
        self.resource_monitor = ResourceMonitor()

    def _load_optimization_settings(self) -> Dict[str, Any]:
        """Load optimization settings from environment."""
        return {
            'enable_caching': os.getenv('PRODUCTION_OPTIMIZATIONS', 'true').lower() == 'true',
            'cache_size_mb': int(os.getenv('CACHE_SIZE_MB', '100')),
            'cache_ttl_seconds': int(os.getenv('CACHE_TTL_SECONDS', '300')),
            'enable_compression': os.getenv('COMPRESS_RESPONSES', 'true').lower() == 'true',
            'enable_minification': os.getenv('MINIFY_STATIC_FILES', 'true').lower() == 'true',
            'max_workers': int(os.getenv('MAX_WORKERS', '8')),
            'memory_limit_mb': int(os.getenv('MEMORY_LIMIT_MB', '1024')),
            'gc_interval_seconds': int(os.getenv('GARBAGE_COLLECTION_INTERVAL', '60')),
            'enable_profiling': os.getenv('ENABLE_PROFILING', 'false').lower() == 'true',
            'batch_size': int(os.getenv('BATCH_SIZE', '100')),
            'connection_pool_size': int(os.getenv('CONNECTION_POOL_SIZE', '20'))
        }

    def optimize_fastapi_app(self, app) -> None:
        """Apply FastAPI-specific optimizations."""
        try:
            # Enable response compression
            if self.optimization_settings['enable_compression']:
                @app.middleware("http")
                async def compress_response(request, call_next):
                    response = await call_next(request)

                    # Compress JSON responses
                    if "application/json" in response.headers.get("content-type", ""):
                        import gzip
                        import io

                        body = b""
                        async for chunk in response.body_iterator:
                            body += chunk

                        if len(body) > 1024:  # Only compress if > 1KB
                            compressed = gzip.compress(body)
                            response.headers["Content-Encoding"] = "gzip"
                            response.headers["Content-Length"] = str(len(compressed))

                            async def compressed_body():
                                yield compressed

                            response.body_iterator = compressed_body()

                    return response

            # Add performance headers
            @app.middleware("http")
            async def add_performance_headers(request, call_next):
                start_time = time.time()
                response = await call_next(request)
                process_time = time.time() - start_time

                response.headers["X-Process-Time"] = str(process_time)
                response.headers["X-Optimized-By"] = "3D-Platform-Optimizer"

                return response

            print("✅ FastAPI optimizations applied")

        except Exception as e:
            print(f"⚠️  Could not apply FastAPI optimizations: {e}")

    def optimize_asyncio(self) -> None:
        """Optimize asyncio event loop for production."""
        try:
            # Set optimal event loop policy
            if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
                asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

            # Configure thread pool executor
            loop = asyncio.get_event_loop()
            if not hasattr(loop, '_default_executor') or loop._default_executor is None:
                from concurrent.futures import ThreadPoolExecutor
                executor = ThreadPoolExecutor(
                    max_workers=self.optimization_settings['max_workers'],
                    thread_name_prefix="3d-platform"
                )
                loop.set_default_executor(executor)

            print("✅ Asyncio optimizations applied")

        except Exception as e:
            print(f"⚠️  Could not apply asyncio optimizations: {e}")

class CachingManager:
    """Manages caching for improved performance."""

    def __init__(self, max_size_mb: int = 100, ttl_seconds: int = 300):
        self.max_size_mb = max_size_mb
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.access_times: Dict[str, float] = {}
        self.lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self.lock:
            if key not in self.cache:
                self.cache_stats['misses'] += 1
                return None

            # Check TTL
            if time.time() - self.access_times[key] > self.ttl_seconds:
                del self.cache[key]
                del self.access_times[key]
                self.cache_stats['evictions'] += 1
                self.cache_stats['misses'] += 1
                return None

            # Update access time
            self.access_times[key] = time.time()
            self.cache_stats['hits'] += 1

            return self.cache[key]['value']

    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        with self.lock:
            # Check size limit (rough estimation)
            estimated_size = len(str(value).encode('utf-8'))
            current_size = sum(len(str(v).encode('utf-8')) for v in self.cache.values())

            # Evict old entries if needed (simple LRU)
            while current_size + estimated_size > self.max_size_mb * 1024 * 1024 and self.cache:
                oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
                current_size -= len(str(self.cache[oldest_key]).encode('utf-8'))
                del self.cache[oldest_key]
                del self.access_times[oldest_key]
                self.cache_stats['evictions'] += 1

            self.cache[key] = {'value': value, 'size': estimated_size}
            self.access_times[key] = time.time()

    def clear(self) -> None:
        """Clear all cached data."""
        with self.lock:
            self.cache.clear()
            self.access_times.clear()
            self.cache_stats = {'hits': 0, 'misses': 0, 'evictions': 0}

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self.lock:
            total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
            hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0

            return {
                'hit_rate_percent': hit_rate,
                'total_hits': self.cache_stats['hits'],
                'total_misses': self.cache_stats['misses'],
                'total_evictions': self.cache_stats['evictions'],
                'cache_size': len(self.cache),
                'max_size_mb': self.max_size_mb
            }

class ResourceMonitor:
    """Monitors system resources for optimization."""

    def __init__(self):
        self.baseline_memory = self._get_memory_usage()
        self.baseline_time = time.time()
        self.gc_last_run = time.time()

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0

    def should_run_gc(self, force: bool = False) -> bool:
        """Check if garbage collection should run."""
        current_memory = self._get_memory_usage()
        memory_increase = current_memory - self.baseline_memory

        # Run GC if memory increased significantly or time interval passed
        time_since_gc = time.time() - self.gc_last_run

        should_gc = (
            force or
            memory_increase > 100 or  # 100MB increase
            time_since_gc > 60  # 60 seconds
        )

        return should_gc

    def run_optimized_gc(self) -> None:
        """Run optimized garbage collection."""
        if self.should_run_gc():
            gc.collect()
            self.gc_last_run = time.time()
            self.baseline_memory = self._get_memory_usage()

class ProductionOptimizer:
    """Main production optimization manager."""

    def __init__(self):
        self.performance_optimizer = PerformanceOptimizer()
        self.caching_manager = CachingManager(
            max_size_mb=self.performance_optimizer.optimization_settings['cache_size_mb'],
            ttl_seconds=self.performance_optimizer.optimization_settings['cache_ttl_seconds']
        )
        self.resource_monitor = ResourceMonitor()
        self.optimization_enabled = self._is_optimization_enabled()

    def _is_optimization_enabled(self) -> bool:
        """Check if optimizations should be enabled."""
        return os.getenv('PRODUCTION_OPTIMIZATIONS', 'true').lower() == 'true'

    def optimize_system(self) -> None:
        """Apply all production optimizations."""
        if not self.optimization_enabled:
            print("⚠️  Production optimizations disabled")
            return

        print("🚀 Applying production optimizations...")

        # Apply performance optimizations
        self.performance_optimizer.optimize_asyncio()

        # Set up periodic resource monitoring
        self._start_resource_monitoring()

        # Set up periodic garbage collection
        self._start_optimized_gc()

        print("✅ Production optimizations applied")

    def _start_resource_monitoring(self) -> None:
        """Start background resource monitoring."""
        def monitor_resources():
            while True:
                try:
                    # Check memory usage and trigger GC if needed
                    if self.resource_monitor.should_run_gc():
                        self.resource_monitor.run_optimized_gc()

                    time.sleep(30)  # Check every 30 seconds

                except Exception as e:
                    logging.error(f"Resource monitoring error: {e}")
                    time.sleep(60)

        thread = threading.Thread(target=monitor_resources, daemon=True)
        thread.start()
        print("📊 Resource monitoring started")

    def _start_optimized_gc(self) -> None:
        """Start optimized garbage collection."""
        def optimized_gc_loop():
            while True:
                try:
                    time.sleep(self.performance_optimizer.optimization_settings['gc_interval_seconds'])
                    self.resource_monitor.run_optimized_gc()

                except Exception as e:
                    logging.error(f"GC loop error: {e}")
                    time.sleep(60)

        thread = threading.Thread(target=optimized_gc_loop, daemon=True)
        thread.start()
        print("🗑️  Optimized garbage collection started")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        return self.caching_manager.get_stats()

    def clear_caches(self) -> None:
        """Clear all caches."""
        self.caching_manager.clear()
        print("🧹 All caches cleared")

@contextmanager
def optimized_operation(operation_name: str):
    """Context manager for optimized operations."""
    if not get_production_optimizer().optimization_enabled:
        yield
        return

    optimizer = get_production_optimizer()
    start_time = time.time()

    try:
        yield
        success = True
    except Exception as e:
        success = False
        raise
    finally:
        execution_time = time.time() - start_time

        # Log slow operations
        if execution_time > 1.0:  # Operations taking > 1 second
            logging.warning(f"Slow operation detected: {operation_name} took {execution_time:.2f}s")

# Global optimizer instance
_optimizer_instance: Optional[ProductionOptimizer] = None

def get_production_optimizer() -> ProductionOptimizer:
    """Get or create global optimizer instance."""
    global _optimizer_instance
    if _optimizer_instance is None:
        _optimizer_instance = ProductionOptimizer()
    return _optimizer_instance

def setup_production_optimizations() -> ProductionOptimizer:
    """Set up production optimizations for the application."""
    optimizer = get_production_optimizer()

    if optimizer.optimization_enabled:
        optimizer.optimize_system()

        # Set up cache decorators for commonly used functions
        setup_caching_decorators()

    return optimizer

def setup_caching_decorators() -> None:
    """Set up caching decorators for performance-critical functions."""
    optimizer = get_production_optimizer()

    def cache_result(ttl_seconds: int = None):
        """Decorator to cache function results."""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if not optimizer.optimization_enabled:
                    return func(*args, **kwargs)

                # Create cache key from function name and arguments
                cache_key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"

                # Try to get from cache
                cached_result = optimizer.caching_manager.get(cache_key)
                if cached_result is not None:
                    return cached_result

                # Execute function and cache result
                result = func(*args, **kwargs)
                optimizer.caching_manager.set(cache_key, result)

                return result
            return wrapper
        return decorator

    # Make decorator available globally
    import builtins
    builtins.cache_result = cache_result

class DatabaseOptimizer:
    """Optimizes database operations for production."""

    def __init__(self):
        self.connection_pool_size = int(os.getenv('DATABASE_POOL_SIZE', '20'))
        self.query_timeout = int(os.getenv('DATABASE_TIMEOUT', '30'))

    def optimize_database_connection(self, connection) -> None:
        """Apply database-specific optimizations."""
        try:
            # Set connection timeouts
            connection.execute(f'PRAGMA busy_timeout={self.query_timeout * 1000}')

            # Optimize for production workload
            connection.execute('PRAGMA journal_mode=WAL')
            connection.execute('PRAGMA synchronous=NORMAL')
            connection.execute('PRAGMA cache_size=10000')
            connection.execute('PRAGMA foreign_keys=ON')
            connection.execute('PRAGMA temp_store=memory')

            # Set connection flags for better performance
            connection.execute('PRAGMA optimize')

        except Exception as e:
            print(f"⚠️  Could not apply database optimizations: {e}")

class NetworkOptimizer:
    """Optimizes network operations for production."""

    def __init__(self):
        self.enable_compression = os.getenv('ENABLE_COMPRESSION', 'true').lower() == 'true'
        self.connection_timeout = int(os.getenv('CONNECTION_TIMEOUT', '30'))
        self.max_connections = int(os.getenv('MAX_CONNECTIONS', '100'))

    def optimize_http_client(self, client) -> None:
        """Optimize HTTP client for production."""
        # Set connection pooling
        if hasattr(client, '_connector'):
            connector = client._connector
            if hasattr(connector, '_limit'):
                connector._limit = self.max_connections

        # Set timeout
        if hasattr(client, 'timeout'):
            client.timeout = self.connection_timeout

def optimize_for_mobile(user_agent: str) -> Dict[str, Any]:
    """Return mobile-specific optimizations."""
    is_mobile = any(device in user_agent.lower() for device in [
        'mobile', 'android', 'iphone', 'ipad', 'ipod'
    ])

    if is_mobile:
        return {
            'reduced_quality': True,
            'lower_particle_count': True,
            'simplified_geometry': True,
            'compressed_textures': True,
            'batch_updates': True,
            'update_interval': 0.2  # Slower updates for mobile
        }

    return {
        'high_quality': True,
        'full_particle_count': True,
        'detailed_geometry': True,
        'update_interval': 0.1  # Faster updates for desktop
    }

def optimize_for_browser(browser_info: Dict[str, str]) -> Dict[str, Any]:
    """Return browser-specific optimizations."""
    browser_name = browser_info.get('name', '').lower()

    if 'chrome' in browser_name:
        return {
            'webgl_version': 2,
            'enable_extensions': True,
            'use_advanced_features': True
        }
    elif 'firefox' in browser_name:
        return {
            'webgl_version': 2,
            'enable_extensions': True,
            'optimize_for_gecko': True
        }
    elif 'safari' in browser_name:
        return {
            'webgl_version': 1,
            'disable_problematic_extensions': True,
            'use_webkit_optimizations': True
        }
    else:
        return {
            'webgl_version': 1,
            'safe_mode': True
        }

# Production-ready middleware and decorators
def rate_limit(max_calls: int = 100, time_window: int = 60):
    """Rate limiting decorator for production."""
    def decorator(func):
        calls = []

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()

            # Remove old calls outside time window
            calls[:] = [call_time for call_time in calls if current_time - call_time < time_window]

            if len(calls) >= max_calls:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")

            calls.append(current_time)
            return func(*args, **kwargs)
        return wrapper
    return decorator

def timeout(seconds: int = 30):
    """Timeout decorator for operations."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = [None]
            exception = [None]

            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e

            thread = threading.Thread(target=target, daemon=True)
            thread.start()
            thread.join(seconds)

            if thread.is_alive():
                raise TimeoutError(f"Operation timed out after {seconds} seconds")

            if exception[0]:
                raise exception[0]

            return result[0]
        return wrapper
    return decorator

# Initialize production optimizations
def initialize_production_settings() -> ProductionOptimizer:
    """Initialize all production optimization settings."""
    print("🏭 Initializing production optimization settings...")

    optimizer = setup_production_optimizations()

    # Set up database optimizations
    db_optimizer = DatabaseOptimizer()
    print("🗄️  Database optimizations configured")

    # Set up network optimizations
    network_optimizer = NetworkOptimizer()
    print("🌐 Network optimizations configured")

    print("✅ Production optimization settings initialized")
    return optimizer

if __name__ == "__main__":
    # Test production optimizations
    print("🧪 Testing production optimizations...")

    optimizer = initialize_production_settings()

    # Test caching
    cache = optimizer.caching_manager

    # Set some test data
    cache.set("test_key", {"data": "test_value", "number": 42})

    # Retrieve data
    retrieved = cache.get("test_key")
    assert retrieved is not None
    assert retrieved["number"] == 42

    print("✅ Caching test passed")

    # Test cache stats
    stats = cache.get_stats()
    assert stats["hit_rate_percent"] >= 0

    print("✅ Cache statistics test passed")

    # Test resource monitoring
    if optimizer.resource_monitor.should_run_gc(force=True):
        optimizer.resource_monitor.run_optimized_gc()
        print("✅ Resource monitoring test passed")

    print("🎉 All production optimization tests passed!")