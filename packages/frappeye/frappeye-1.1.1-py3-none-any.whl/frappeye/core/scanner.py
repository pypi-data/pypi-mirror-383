"""
High-performance hook scanner for frappeye with optimized file operations.

Scans Frappe apps for hook definitions with intelligent caching, parallel
processing capabilities, and comprehensive error handling.
"""

import concurrent.futures
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Union

from ..utils.frappe_utils import FrappeUtils
from ..utils.paths import PathUtils
from ..utils.performance import PerformanceTimer, timed, performance_monitor
from ..utils.validation import ValidationUtils
from .models import AppInfo, HookDefinition, HookType


class HookScanner:
    """
    Ultra-fast scanner for Frappe hook definitions with intelligent optimization.
    
    Features:
    - Parallel scanning for maximum performance
    - Intelligent caching to avoid redundant operations
    - Comprehensive error handling and recovery
    - Memory-efficient processing for large codebases
    """
    
    def __init__(self, max_workers: Optional[int] = None, enable_cache: bool = True):
        """
        Initialize hook scanner with performance optimizations.
        
        Args:
            max_workers: Maximum number of worker threads for parallel scanning
            enable_cache: Whether to enable intelligent caching
        """
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self.enable_cache = enable_cache
        self._scan_cache: Dict[str, List[HookDefinition]] = {}
        
    @timed("scan_bench")
    def scan_bench(self, bench_path: Union[str, Path], site_name: Optional[str] = None) -> List[HookDefinition]:
        """
        Scan entire Frappe bench for hook definitions.
        
        Args:
            bench_path: Path to Frappe bench directory
            site_name: Optional site name to get app load order
            
        Returns:
            List of all hook definitions found in the bench
        """
        bench_path = ValidationUtils.validate_scan_path(bench_path)
        
        if not PathUtils.is_frappe_bench(bench_path):
            raise ValueError(f"Path is not a valid Frappe bench: {bench_path}")
        
        performance_monitor.start_timer("scan_bench_total")
        
        try:
            if site_name:
                site_path = bench_path / "sites" / site_name
                if site_path.exists():
                    apps = FrappeUtils.get_app_load_order(site_path, bench_path)
                else:
                    apps = self._discover_all_apps(bench_path)
            else:
                apps = self._discover_all_apps(bench_path)
            
            all_hooks = []
            for app in apps:
                try:
                    hooks = self.scan_app(app.path)
                    for hook in hooks:
                        hook.app_name = app.name
                        hook.priority = app.priority
                    all_hooks.extend(hooks)
                except (OSError, PermissionError):
                    continue
                except Exception:
                    continue
            
            return all_hooks
        except (OSError, PermissionError) as e:
            raise RuntimeError(f"File system access error: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Bench scan failed: {e}") from e
            
        finally:
            duration = performance_monitor.stop_timer("scan_bench_total")
            performance_monitor.record_metric("hooks_per_second", len(all_hooks) / max(duration, 0.001))
    
    @timed("scan_site")
    def scan_site(self, site_path: Union[str, Path], bench_path: Optional[Union[str, Path]] = None) -> List[HookDefinition]:
        """
        Scan Frappe site for hook definitions with proper app load order.
        
        Args:
            site_path: Path to Frappe site directory
            bench_path: Optional bench path (auto-detected if not provided)
            
        Returns:
            List of hook definitions in site's app load order
        """
        site_path = ValidationUtils.validate_scan_path(site_path)
        
        if not PathUtils.is_frappe_site(site_path):
            raise ValueError(f"Path is not a valid Frappe site: {site_path}")
        
        try:
            if not bench_path:
                bench_path = PathUtils.find_bench_root(site_path)
                if not bench_path:
                    raise ValueError(f"Could not find bench root for site: {site_path}")
            else:
                bench_path = ValidationUtils.validate_scan_path(bench_path)
            
            apps = FrappeUtils.get_app_load_order(site_path, bench_path)
            
            all_hooks = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_app = {
                    executor.submit(self.scan_app, app.path): app 
                    for app in apps if app.hooks_file and app.hooks_file.exists()
                }
                
                for future in concurrent.futures.as_completed(future_to_app):
                    app = future_to_app[future]
                    try:
                        hooks = future.result(timeout=30)
                        for hook in hooks:
                            hook.app_name = app.name
                            hook.priority = app.priority
                        all_hooks.extend(hooks)
                    except (concurrent.futures.TimeoutError, OSError, PermissionError):
                        continue
                    except Exception:
                        continue
        except (OSError, PermissionError) as e:
            raise RuntimeError(f"Site access error: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Site scan failed: {e}") from e
        
        return all_hooks
    
    @timed("scan_app")
    def scan_app(self, app_path: Union[str, Path]) -> List[HookDefinition]:
        """
        Scan single Frappe app for hook definitions.
        
        Args:
            app_path: Path to Frappe app directory
            
        Returns:
            List of hook definitions found in the app
        """
        app_path = ValidationUtils.validate_scan_path(app_path)
        
        if not PathUtils.is_frappe_app(app_path):
            raise ValueError(f"Path is not a valid Frappe app: {app_path}")
        
        # Check cache first
        cache_key = str(app_path)
        if self.enable_cache and cache_key in self._scan_cache:
            return self._scan_cache[cache_key].copy()
        
        # Find hooks.py file
        hooks_file = PathUtils.get_hooks_file_path(app_path)
        if not hooks_file:
            return []
        
        # Parse hooks file
        hooks_data = FrappeUtils.parse_hooks_file(hooks_file)
        if not hooks_data:
            return []
        
        # Convert to HookDefinition objects
        hook_definitions = []
        app_name = app_path.name
        
        for hook_name, hook_value in hooks_data.items():
            try:
                # Classify hook type
                hook_type = FrappeUtils.classify_hook_type(hook_name, hook_value)
                
                # Extract handlers
                handlers = FrappeUtils.extract_hook_handlers(hook_name, hook_value)
                
                # Create HookDefinition for each handler
                for target, handler in handlers:
                    if FrappeUtils.validate_handler_path(handler):
                        hook_def = HookDefinition(
                            app_name=app_name,
                            hook_type=hook_type,
                            hook_name=hook_name,
                            target=target or None,
                            handler=handler,
                            line_number=0,  # TODO: Extract actual line number
                            file_path=hooks_file,
                            priority=0,  # Will be set by caller
                            raw_definition={hook_name: hook_value},
                        )
                        hook_definitions.append(hook_def)
                        
            except Exception as e:
                # Log warning but continue processing
                print(f"Warning: Failed to process hook {hook_name} in {app_name}: {e}")
        
        # Cache results
        if self.enable_cache:
            self._scan_cache[cache_key] = hook_definitions.copy()
        
        return hook_definitions
    
    def scan_multiple_apps(self, app_paths: List[Union[str, Path]]) -> List[HookDefinition]:
        """
        Scan multiple apps in parallel for maximum performance.
        
        Args:
            app_paths: List of paths to Frappe app directories
            
        Returns:
            Combined list of hook definitions from all apps
        """
        if not app_paths:
            return []
        
        all_hooks = []
        
        # Use parallel processing for multiple apps
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_path = {
                executor.submit(self.scan_app, app_path): app_path 
                for app_path in app_paths
            }
            
            for future in concurrent.futures.as_completed(future_to_path):
                app_path = future_to_path[future]
                try:
                    hooks = future.result()
                    all_hooks.extend(hooks)
                except Exception as e:
                    print(f"Warning: Failed to scan app at {app_path}: {e}")
        
        return all_hooks
    
    def _discover_all_apps(self, bench_path: Path) -> List[AppInfo]:
        """Discover all apps in bench directory."""
        app_paths = PathUtils.discover_apps_in_bench(bench_path)
        apps = []
        
        for priority, app_path in enumerate(app_paths):
            app_info = PathUtils.get_app_info_from_path(app_path, priority)
            if app_info:
                apps.append(app_info)
        
        return apps
    
    def get_scan_statistics(self) -> Dict[str, any]:
        """Get performance statistics for scan operations."""
        return performance_monitor.get_all_stats()
    
    def clear_cache(self):
        """Clear internal caches to free memory."""
        self._scan_cache.clear()
        FrappeUtils.clear_cache()
        PathUtils.clear_cache()
    
    def set_cache_enabled(self, enabled: bool):
        """Enable or disable caching."""
        self.enable_cache = enabled
        if not enabled:
            self.clear_cache()
    
    def preload_apps(self, app_paths: List[Union[str, Path]]):
        """Preload apps into cache for faster subsequent scans."""
        if not self.enable_cache:
            return
        
        for app_path in app_paths:
            try:
                self.scan_app(app_path)
            except Exception as e:
                print(f"Warning: Failed to preload app {app_path}: {e}")
    
    def validate_hooks_syntax(self, hooks_file: Union[str, Path]) -> List[str]:
        """
        Validate hooks.py file syntax and return list of issues.
        
        Args:
            hooks_file: Path to hooks.py file
            
        Returns:
            List of syntax issues found (empty if valid)
        """
        hooks_file = Path(hooks_file)
        issues = []
        
        if not hooks_file.exists():
            issues.append(f"Hooks file does not exist: {hooks_file}")
            return issues
        
        try:
            # Try to parse the file
            hooks_data = FrappeUtils.parse_hooks_file(hooks_file)
            
            # Validate each hook
            for hook_name, hook_value in hooks_data.items():
                try:
                    # Validate hook name
                    ValidationUtils.validate_hook_name(hook_name)
                    
                    # Extract and validate handlers
                    handlers = FrappeUtils.extract_hook_handlers(hook_name, hook_value)
                    for target, handler in handlers:
                        if not FrappeUtils.validate_handler_path(handler):
                            issues.append(f"Invalid handler format in {hook_name}: {handler}")
                            
                except Exception as e:
                    issues.append(f"Invalid hook {hook_name}: {e}")
                    
        except Exception as e:
            issues.append(f"Failed to parse hooks file: {e}")
        
        return issues