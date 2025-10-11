# 🔍 FrappEye

**Advanced Frappe hooks analyzer and conflict detector for multi-app environments**

[![PyPI version](https://badge.fury.io/py/frappeye.svg)](https://badge.fury.io/py/frappeye)
[![Python Support](https://img.shields.io/pypi/pyversions/frappeye.svg)](https://pypi.org/project/frappeye/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

FrappEye is a high-performance Python library and CLI tool designed to analyze, inspect, and report on hooks in Frappe applications. It provides complete visibility into `hooks.py` files across apps, detects conflicts and overlapping methods, and generates comprehensive reports for developers, teams, and CI/CD pipelines.

## 🚀 Key Features

- **🔍 Comprehensive Hook Scanning** - Analyzes all hook types including doc_events, method overrides, scheduler events, and custom hooks
- **⚡ Ultra-Fast Performance** - Optimized with parallel processing, intelligent caching, and performance monitoring
- **🎯 Intelligent Conflict Detection** - Detects overlapping hooks with severity classification (Critical, High, Medium, Low)
- **📊 Multiple Output Formats** - Rich terminal tables, JSON, CSV, HTML, and Markdown reports
- **🔄 CI/CD Integration** - Built-in support for automated testing and deployment pipelines
- **🎨 Rich Terminal UI** - Beautiful, colored output with progress indicators and detailed formatting
- **🏗️ App Hierarchy Awareness** - Understands Frappe app load order and priority for accurate conflict resolution

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install frappeye
```

### From Source

```bash
git clone https://github.com/thisissharath/frappeye.git
cd frappeye
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/thisissharath/frappeye.git
cd frappeye
pip install -e ".[dev]"
```

## 🛠️ Quick Start

### Command Line Usage

```bash
# Scan entire Frappe bench
frappeye scan /path/to/frappe-bench

# Scan specific site with app load order
frappeye scan /path/to/frappe-bench/sites/mysite

# Scan single app
frappeye scan /path/to/frappe-bench/apps/erpnext

# Export results for CI/CD
frappeye export /path/to/bench results.json --fail-on-critical

# Quick conflict check
frappeye check /path/to/bench --exit-code

# Validate hooks syntax
frappeye validate /path/to/app
```

### Python API Usage

```python
from frappeye import FrappEye

# Initialize scanner
scanner = FrappEye()

# Full comprehensive scan with all details
report = scanner.full_scan_report("/path/to/frappe-bench", save_to="report.json")
print(f"Found {report['summary']['total_conflicts']} conflicts")

# Quick scan for fast checks
quick = scanner.quick_scan("/path/to/frappe-bench")
print(f"Status: {quick['status']}, Critical: {quick['critical_conflicts']}")

# Export for CI/CD
scanner.export_for_ci("/path/to/bench", "ci-report.json")
```

## 📋 Supported Hook Types

FrappEye analyzes all Frappe hook types:

- **Doc Events** - `before_save`, `after_insert`, `on_submit`, etc.
- **Method Overrides** - `override_whitelisted_methods`, `override_doctype_class`
- **Scheduler Events** - `all`, `hourly`, `daily`, `weekly`, `monthly`, `cron`
- **Website Hooks** - `website_route_rules`, `website_redirects`
- **Boot Session** - `boot_session`
- **Jinja Filters** - `jinja`
- **Fixtures** - `fixtures`
- **Custom Hooks** - Any custom hook definitions

## 🎯 Conflict Detection

FrappEye uses sophisticated algorithms to detect various types of conflicts:

### Severity Levels

- **🔴 Critical** - Will cause runtime errors (method overrides, class overrides)
- **🟠 High** - Likely to cause issues (doc events, route conflicts)
- **🟡 Medium** - May cause unexpected behavior (scheduler conflicts)
- **🔵 Low** - Informational (jinja filters, fixtures)
- **🟢 Info** - Just informational

### Conflict Types

- **Method Override Conflicts** - Multiple apps overriding the same method
- **DocType Class Conflicts** - Multiple apps overriding the same DocType class
- **Doc Event Overlaps** - Multiple handlers for the same DocType event
- **Route Conflicts** - Conflicting website route rules
- **Scheduler Overlaps** - Duplicate scheduler event definitions

## 📊 Output Formats

### Terminal Table (Default)
Rich, colored tables with icons and formatting for immediate visual feedback.

### JSON Export
```json
{
  "scan_id": "abc123",
  "timestamp": "2024-01-15T10:30:00",
  "total_conflicts": 3,
  "conflicts": [
    {
      "severity": "critical",
      "hook_type": "override_whitelisted_methods",
      "description": "Multiple apps override get_item_details method",
      "affected_apps": ["erpnext", "custom_app"],
      "resolution_hint": "Consolidate method overrides into single app"
    }
  ]
}
```

### CSV Export
Structured data suitable for spreadsheets and data analysis tools.

### HTML Report
Professional reports with styling, perfect for documentation and sharing.

### Markdown
Documentation-friendly format for README files and wikis.

## 🔧 Configuration Options

### CLI Options

```bash
# Performance tuning
frappeye scan /path --max-workers 8 --no-cache

# Filtering and severity
frappeye scan /path --min-severity high --strict

# Output control
frappeye scan /path --format json --output report.json

# Site-specific scanning
frappeye scan /path/to/bench --site production
```

### Python API Options

```python
# Performance optimization
scanner = FrappEye(
    max_workers=8,           # Parallel processing threads
    enable_cache=True,       # Intelligent caching
    strict_mode=False,       # Treat all conflicts as high severity
    console_output=True      # Rich terminal output
)

# Scan with options
result = scanner.scan(
    path="/path/to/bench",
    site_name="production",  # App load order from site
    output_format="json",    # Output format
    min_severity="medium"    # Filter by severity
)
```

## 🚀 CI/CD Integration

### GitHub Actions

```yaml
name: Hook Conflict Check
on: [push, pull_request]

jobs:
  check-hooks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install FrappEye
        run: pip install frappeye
      
      - name: Check for hook conflicts
        run: frappeye check . --exit-code --critical-only
      
      - name: Generate report
        if: always()
        run: frappeye export . hook-report.json
      
      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: hook-analysis
          path: hook-report.json
```

### GitLab CI

```yaml
hook-analysis:
  stage: test
  image: python:3.11
  script:
    - pip install frappeye
    - frappeye check . --exit-code --critical-only
    - frappeye export . hook-report.json
  artifacts:
    reports:
      junit: hook-report.json
    when: always
```

## 🏗️ Architecture

FrappEye is built with a modular, high-performance architecture:

### Core Components

- **Scanner Module** - Fast, parallel hook discovery and parsing
- **Analyzer Module** - Intelligent conflict detection with severity classification
- **Reporter Module** - Multi-format report generation with rich formatting
- **CLI Module** - Comprehensive command-line interface

### Performance Features

- **Parallel Processing** - Multi-threaded scanning for large codebases
- **Intelligent Caching** - Avoids redundant file operations
- **Memory Optimization** - Efficient data structures for large apps
- **Performance Monitoring** - Built-in timing and metrics

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone repository
git clone https://github.com/thisissharath/frappeye.git
cd frappeye

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
black frappeye/
flake8 frappeye/
mypy frappeye/
```

## 📚 Documentation

- [API Reference](https://frappeye.readthedocs.io/en/latest/api/)
- [CLI Guide](https://frappeye.readthedocs.io/en/latest/cli/)
- [Integration Examples](https://frappeye.readthedocs.io/en/latest/examples/)
- [Performance Tuning](https://frappeye.readthedocs.io/en/latest/performance/)

## 🐛 Bug Reports & Feature Requests

Please use [GitHub Issues](https://github.com/thisissharath/frappeye/issues) to report bugs or request features.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built for the [Frappe Framework](https://frappeframework.com/) community
- Inspired by the need for better multi-app conflict detection
- Thanks to all contributors and users providing feedback

---

**Made with ❤️ by Sharath Kumar for the Frappe community**