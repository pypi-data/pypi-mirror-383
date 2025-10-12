"""
Validation utilities for frappeye with comprehensive input validation.

Provides robust validation for paths, configurations, and data structures
with detailed error reporting and performance optimization.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from ..core.models import AppInfo, HookDefinition, ConflictSeverity


class ValidationError(Exception):
    """Custom exception for validation errors with detailed context."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        """Initialize validation error with context."""
        self.field = field
        self.value = value
        super().__init__(message)


class ValidationUtils:
    """Comprehensive validation utilities for frappeye operations."""
    
    # Regex patterns for validation
    PYTHON_IDENTIFIER_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
    MODULE_PATH_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_.]*[a-zA-Z0-9_]$')
    VERSION_PATTERN = re.compile(r'^\d+\.\d+\.\d+(?:-[a-zA-Z0-9]+)?$')
    
    @staticmethod
    def validate_path(path: Union[str, Path], must_exist: bool = True, must_be_dir: bool = False, must_be_file: bool = False) -> Path:
        """Validate path with comprehensive checks."""
        if not path:
            raise ValidationError("Path cannot be empty", "path", path)
        
        try:
            path_obj = Path(path).resolve()
        except (OSError, ValueError) as e:
            raise ValidationError(f"Invalid path format: {e}", "path", path)
        
        if must_exist and not path_obj.exists():
            raise ValidationError(f"Path does not exist: {path_obj}", "path", path)
        
        if must_be_dir and path_obj.exists() and not path_obj.is_dir():
            raise ValidationError(f"Path is not a directory: {path_obj}", "path", path)
        
        if must_be_file and path_obj.exists() and not path_obj.is_file():
            raise ValidationError(f"Path is not a file: {path_obj}", "path", path)
        
        return path_obj
    
    @staticmethod
    def validate_app_name(app_name: str) -> str:
        """Validate Frappe app name format."""
        if not app_name:
            raise ValidationError("App name cannot be empty", "app_name", app_name)
        
        if not isinstance(app_name, str):
            raise ValidationError("App name must be a string", "app_name", app_name)
        
        # App names should be valid Python identifiers
        if not ValidationUtils.PYTHON_IDENTIFIER_PATTERN.match(app_name):
            raise ValidationError(
                f"Invalid app name format: {app_name}. Must be a valid Python identifier.",
                "app_name", 
                app_name
            )
        
        # Additional Frappe-specific rules
        if app_name.startswith('_'):
            raise ValidationError(
                f"App name cannot start with underscore: {app_name}",
                "app_name",
                app_name
            )
        
        if len(app_name) > 50:
            raise ValidationError(
                f"App name too long (max 50 characters): {app_name}",
                "app_name",
                app_name
            )
        
        return app_name
    
    @staticmethod
    def validate_hook_name(hook_name: str) -> str:
        """Validate hook name format."""
        if not hook_name:
            raise ValidationError("Hook name cannot be empty", "hook_name", hook_name)
        
        if not isinstance(hook_name, str):
            raise ValidationError("Hook name must be a string", "hook_name", hook_name)
        
        # Hook names should be valid Python identifiers
        if not ValidationUtils.PYTHON_IDENTIFIER_PATTERN.match(hook_name):
            raise ValidationError(
                f"Invalid hook name format: {hook_name}. Must be a valid Python identifier.",
                "hook_name",
                hook_name
            )
        
        return hook_name
    
    @staticmethod
    def validate_handler_path(handler: str) -> str:
        """Validate handler function path format."""
        if not handler:
            raise ValidationError("Handler path cannot be empty", "handler", handler)
        
        if not isinstance(handler, str):
            raise ValidationError("Handler path must be a string", "handler", handler)
        
        # Handler should be in module.function format
        if '.' not in handler:
            raise ValidationError(
                f"Handler must be in module.function format: {handler}",
                "handler",
                handler
            )
        
        # Validate module path format
        if not ValidationUtils.MODULE_PATH_PATTERN.match(handler):
            raise ValidationError(
                f"Invalid handler path format: {handler}",
                "handler", 
                handler
            )
        
        # Check for common mistakes
        if handler.startswith('.') or handler.endswith('.'):
            raise ValidationError(
                f"Handler path cannot start or end with dot: {handler}",
                "handler",
                handler
            )
        
        if '..' in handler:
            raise ValidationError(
                f"Handler path cannot contain consecutive dots: {handler}",
                "handler",
                handler
            )
        
        return handler
    
    @staticmethod
    def validate_version(version: str) -> str:
        """Validate version string format."""
        if not version:
            return version  # Version is optional
        
        if not isinstance(version, str):
            raise ValidationError("Version must be a string", "version", version)
        
        if not ValidationUtils.VERSION_PATTERN.match(version):
            raise ValidationError(
                f"Invalid version format: {version}. Expected format: x.y.z or x.y.z-suffix",
                "version",
                version
            )
        
        return version
    
    @staticmethod
    def validate_app_info(app_info: AppInfo) -> AppInfo:
        """Validate AppInfo object comprehensively."""
        # Validate app name
        ValidationUtils.validate_app_name(app_info.name)
        
        # Validate paths
        ValidationUtils.validate_path(app_info.path, must_exist=True, must_be_dir=True)
        
        if app_info.hooks_file:
            ValidationUtils.validate_path(app_info.hooks_file, must_exist=True, must_be_file=True)
        
        # Validate version if present
        if app_info.version:
            ValidationUtils.validate_version(app_info.version)
        
        # Validate priority
        if not isinstance(app_info.priority, int) or app_info.priority < 0:
            raise ValidationError(
                f"Priority must be a non-negative integer: {app_info.priority}",
                "priority",
                app_info.priority
            )
        
        return app_info
    
    @staticmethod
    def validate_hook_definition(hook_def: HookDefinition) -> HookDefinition:
        """Validate HookDefinition object comprehensively."""
        # Validate app name
        ValidationUtils.validate_app_name(hook_def.app_name)
        
        # Validate hook name
        ValidationUtils.validate_hook_name(hook_def.hook_name)
        
        # Validate handler path
        ValidationUtils.validate_handler_path(hook_def.handler)
        
        # Validate file path
        ValidationUtils.validate_path(hook_def.file_path, must_exist=True, must_be_file=True)
        
        # Validate line number
        if not isinstance(hook_def.line_number, int) or hook_def.line_number < 0:
            raise ValidationError(
                f"Line number must be a non-negative integer: {hook_def.line_number}",
                "line_number",
                hook_def.line_number
            )
        
        # Validate priority
        if not isinstance(hook_def.priority, int) or hook_def.priority < 0:
            raise ValidationError(
                f"Priority must be a non-negative integer: {hook_def.priority}",
                "priority", 
                hook_def.priority
            )
        
        return hook_def
    
    @staticmethod
    def validate_scan_path(path: Union[str, Path]) -> Path:
        """Validate scan path and determine type."""
        from .paths import PathUtils
        
        path_obj = ValidationUtils.validate_path(path, must_exist=True, must_be_dir=True)
        
        # Check if it's a valid Frappe structure
        is_bench = PathUtils.is_frappe_bench(path_obj)
        is_site = PathUtils.is_frappe_site(path_obj)
        is_app = PathUtils.is_frappe_app(path_obj)
        
        if not (is_bench or is_site or is_app):
            raise ValidationError(
                f"Path is not a valid Frappe bench, site, or app: {path_obj}",
                "scan_path",
                path_obj
            )
        
        return path_obj
    
    @staticmethod
    def validate_output_format(format_name: str) -> str:
        """Validate output format name."""
        valid_formats = {'json', 'csv', 'table', 'markdown', 'html'}
        
        if not format_name:
            raise ValidationError("Output format cannot be empty", "format", format_name)
        
        format_lower = format_name.lower()
        if format_lower not in valid_formats:
            raise ValidationError(
                f"Invalid output format: {format_name}. Valid formats: {', '.join(valid_formats)}",
                "format",
                format_name
            )
        
        return format_lower
    
    @staticmethod
    def validate_severity_level(severity: Union[str, ConflictSeverity]) -> ConflictSeverity:
        """Validate and normalize severity level."""
        if isinstance(severity, ConflictSeverity):
            return severity
        
        if not isinstance(severity, str):
            raise ValidationError("Severity must be a string or ConflictSeverity enum", "severity", severity)
        
        try:
            return ConflictSeverity(severity.lower())
        except ValueError:
            valid_severities = [s.value for s in ConflictSeverity]
            raise ValidationError(
                f"Invalid severity level: {severity}. Valid levels: {', '.join(valid_severities)}",
                "severity",
                severity
            )
    
    @staticmethod
    def validate_hook_data(hook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate raw hook data structure."""
        if not isinstance(hook_data, dict):
            raise ValidationError("Hook data must be a dictionary", "hook_data", hook_data)
        
        # Check for required fields would go here
        # This is a placeholder for future validation rules
        
        return hook_data
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe file operations."""
        if not filename:
            raise ValidationError("Filename cannot be empty", "filename", filename)
        
        # Remove or replace invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove leading/trailing whitespace and dots
        sanitized = sanitized.strip(' .')
        
        # Ensure it's not empty after sanitization
        if not sanitized:
            raise ValidationError(f"Filename becomes empty after sanitization: {filename}", "filename", filename)
        
        # Limit length
        if len(sanitized) > 255:
            sanitized = sanitized[:255]
        
        return sanitized
    
    @staticmethod
    def validate_json_serializable(data: Any) -> bool:
        """Check if data is JSON serializable."""
        try:
            import json
            json.dumps(data, default=str)
            return True
        except (TypeError, ValueError):
            return False