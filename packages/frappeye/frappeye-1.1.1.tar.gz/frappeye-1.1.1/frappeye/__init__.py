"""
frappeye - Advanced Frappe hooks analyzer and conflict detector.

A high-performance Python library for analyzing, inspecting, and reporting
on hooks in Frappe applications. Provides complete visibility into hooks.py
files across apps, detects conflicts, and generates structured reports.

Key Features:
- Ultra-fast hook scanning and analysis
- Conflict detection with app hierarchy awareness  
- Multiple output formats (JSON, CSV, terminal tables)
- CI/CD pipeline integration
- Comprehensive reporting and auditing

Author: Frappe Community
License: MIT
"""

__version__ = "1.1.1"
__author__ = "Sharath Kumar"
__email__ = "imsharathkumarv@gmail.com"
__license__ = "MIT"

# Core imports for public API
from .core.scanner import HookScanner
from .core.analyzer import ConflictAnalyzer
from .core.reporter import HookReporter
from .core.models import (
    HookDefinition,
    ConflictReport,
    ScanResult,
    AppInfo,
    HookType,
    ConflictSeverity,
)

# Main API class
from .core.api import FrappEye

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    # Core classes
    "FrappEye",
    "HookScanner", 
    "ConflictAnalyzer",
    "HookReporter",
    # Data models
    "HookDefinition",
    "ConflictReport", 
    "ScanResult",
    "AppInfo",
    "HookType",
    "ConflictSeverity",
]