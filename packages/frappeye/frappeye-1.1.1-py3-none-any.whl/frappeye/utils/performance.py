"""
Performance utilities for frappeye with optimized operations and caching.

Provides timing utilities, caching decorators, and performance monitoring
tools to ensure frappeye operates at maximum efficiency.
"""

import functools
import time
from contextlib import contextmanager
from typing import Any, Callable, Dict, Optional, TypeVar, Union

F = TypeVar('F', bound=Callable[..., Any])


class PerformanceTimer:
    """High-precision timer for performance monitoring and optimization."""
    
    def __init__(self, name: str = "operation"):
        """Initialize timer with operation name."""
        self.name = name
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.duration: Optional[float] = None
    
    def start(self) -> 'PerformanceTimer':
        """Start the timer."""
        self.start_time = time.perf_counter()
        self.end_time = None
        self.duration = None
        return self
    
    def stop(self) -> float:
        """Stop the timer and return duration."""
        if self.start_time is None:
            raise RuntimeError("Timer not started")
        
        self.end_time = time.perf_counter()
        self.duration = self.end_time - self.start_time
        return self.duration
    
    def __enter__(self) -> 'PerformanceTimer':
        """Context manager entry."""
        return self.start()
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.stop()
    
    def __str__(self) -> str:
        """String representation of timer."""
        if self.duration is not None:
            return f"{self.name}: {self.duration:.4f}s"
        elif self.start_time is not None:
            current = time.perf_counter()
            elapsed = current - self.start_time
            return f"{self.name}: {elapsed:.4f}s (running)"
        else:
            return f"{self.name}: not started"


@contextmanager
def timer(name: str = "operation"):
    """Context manager for timing operations."""
    perf_timer = PerformanceTimer(name)
    perf_timer.start()
    try:
        yield perf_timer
    finally:
        perf_timer.stop()


def timed(name: Optional[str] = None):
    """Decorator to time function execution."""
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            timer_name = name or f"{func.__module__}.{func.__name__}"
            with timer(timer_name) as t:
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator


class cached_property:
    """
    Optimized cached property descriptor for expensive computations.
    
    Similar to functools.cached_property but with better performance
    and memory management for frappeye use cases.
    """
    
    def __init__(self, func: Callable):
        """Initialize cached property with function."""
        self.func = func
        self.attrname = None
        self.__doc__ = func.__doc__
    
    def __set_name__(self, owner, name):
        """Set attribute name when class is created."""
        if self.attrname is None:
            self.attrname = name
        elif name != self.attrname:
            raise RuntimeError(
                f"Cannot assign the same cached_property to two different names "
                f"({self.attrname!r} and {name!r})."
            )
    
    def __get__(self, instance, owner=None):
        """Get cached value or compute and cache it."""
        if instance is None:
            return self
        
        if self.attrname is None:
            raise TypeError(
                "Cannot use cached_property instance without calling __set_name__ on it."
            )
        
        try:
            cache = instance.__dict__
        except AttributeError:
            msg = (
                f"No '__dict__' attribute on {type(instance).__name__!r} "
                f"instance to cache {self.attrname!r} property."
            )
            raise TypeError(msg) from None
        
        val = cache.get(self.attrname, None)
        if val is None:
            with timer(f"cached_property.{self.attrname}"):
                val = self.func(instance)
            try:
                cache[self.attrname] = val
            except TypeError:
                msg = (
                    f"The '__dict__' attribute on {type(instance).__name__!r} instance "
                    f"does not support item assignment for caching {self.attrname!r} property."
                )
                raise TypeError(msg) from None
        return val


def memoize(maxsize: int = 128):
    """
    Optimized memoization decorator with size limit.
    
    Similar to functools.lru_cache but with better control
    and performance monitoring.
    """
    def decorator(func: F) -> F:
        cache: Dict[tuple, Any] = {}
        cache_info = {'hits': 0, 'misses': 0, 'maxsize': maxsize}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from args and kwargs
            key = (args, tuple(sorted(kwargs.items())))
            
            if key in cache:
                cache_info['hits'] += 1
                return cache[key]
            
            # Compute result
            result = func(*args, **kwargs)
            
            # Manage cache size
            if len(cache) >= maxsize:
                # Remove oldest entry (simple FIFO)
                oldest_key = next(iter(cache))
                del cache[oldest_key]
            
            cache[key] = result
            cache_info['misses'] += 1
            return result
        
        def cache_clear():
            """Clear the cache."""
            cache.clear()
            cache_info['hits'] = cache_info['misses'] = 0
        
        def cache_info_func():
            """Get cache statistics."""
            return cache_info.copy()
        
        wrapper.cache_clear = cache_clear
        wrapper.cache_info = cache_info_func
        return wrapper
    
    return decorator


class PerformanceMonitor:
    """Monitor and track performance metrics across frappeye operations."""
    
    def __init__(self):
        """Initialize performance monitor."""
        self.metrics: Dict[str, list] = {}
        self.active_timers: Dict[str, PerformanceTimer] = {}
    
    def start_timer(self, name: str) -> PerformanceTimer:
        """Start a named timer."""
        timer_obj = PerformanceTimer(name)
        timer_obj.start()
        self.active_timers[name] = timer_obj
        return timer_obj
    
    def stop_timer(self, name: str) -> Optional[float]:
        """Stop a named timer and record duration."""
        if name not in self.active_timers:
            return None
        
        timer_obj = self.active_timers.pop(name)
        duration = timer_obj.stop()
        
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(duration)
        
        return duration
    
    def record_metric(self, name: str, value: float):
        """Record a performance metric."""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(value)
    
    def get_stats(self, name: str) -> Dict[str, float]:
        """Get statistics for a metric."""
        if name not in self.metrics or not self.metrics[name]:
            return {}
        
        values = self.metrics[name]
        return {
            'count': len(values),
            'total': sum(values),
            'average': sum(values) / len(values),
            'min': min(values),
            'max': max(values),
        }
    
    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """Get statistics for all metrics."""
        return {name: self.get_stats(name) for name in self.metrics}
    
    def clear(self):
        """Clear all metrics and active timers."""
        self.metrics.clear()
        self.active_timers.clear()


# Global performance monitor instance
performance_monitor = PerformanceMonitor()