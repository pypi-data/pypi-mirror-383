"""
Advanced reporting system for frappeye with multiple output formats.

Generates comprehensive reports in various formats including terminal tables,
JSON, CSV, and HTML with rich formatting and export capabilities.
"""

import csv
import json
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    import orjson
    HAS_ORJSON = True
except ImportError:
    HAS_ORJSON = False

from rich.console import Console
from rich.table import Table
from rich.text import Text
from tabulate import tabulate

from ..utils.performance import timed
from ..utils.validation import ValidationUtils
from .models import ConflictReport, ConflictSeverity, HookDefinition, ScanResult


class HookReporter:
    """
    Advanced reporting system with multiple output formats and rich formatting.
    
    Features:
    - Multiple output formats (table, JSON, CSV, HTML, Markdown)
    - Rich terminal formatting with colors and styling
    - Export capabilities for CI/CD integration
    - Performance-optimized serialization
    """
    
    def __init__(self, console: Optional[Console] = None):
        """
        Initialize reporter with optional custom console.
        
        Args:
            console: Rich console instance for terminal output
        """
        self.console = console or Console()
        
        # Color scheme for different severities
        self.severity_colors = {
            ConflictSeverity.CRITICAL: "red",
            ConflictSeverity.HIGH: "orange3",
            ConflictSeverity.MEDIUM: "yellow",
            ConflictSeverity.LOW: "blue",
            ConflictSeverity.INFO: "green",
        }
        
        # Icons for different severities
        self.severity_icons = {
            ConflictSeverity.CRITICAL: "🔴",
            ConflictSeverity.HIGH: "🟠", 
            ConflictSeverity.MEDIUM: "🟡",
            ConflictSeverity.LOW: "🔵",
            ConflictSeverity.INFO: "🟢",
        }
    
    @timed("generate_report")
    def generate_report(self, scan_result: ScanResult, format_type: str = "table", output_file: Optional[Union[str, Path]] = None) -> str:
        """
        Generate comprehensive report in specified format.
        
        Args:
            scan_result: Complete scan result to report on
            format_type: Output format (table, json, csv, html, markdown)
            output_file: Optional file path to save report
            
        Returns:
            Generated report as string
        """
        format_type = ValidationUtils.validate_output_format(format_type)
        
        # Generate report based on format
        if format_type == "table":
            report = self._generate_table_report(scan_result)
        elif format_type == "json":
            report = self._generate_json_report(scan_result)
        elif format_type == "csv":
            report = self._generate_csv_report(scan_result)
        elif format_type == "html":
            report = self._generate_html_report(scan_result)
        elif format_type == "markdown":
            report = self._generate_markdown_report(scan_result)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
        
        # Save to file if specified
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
        
        return report
    
    def _generate_table_report(self, scan_result: ScanResult) -> str:
        """Generate rich terminal table report."""
        output = StringIO()
        
        # Capture console output
        with self.console.capture() as capture:
            self._print_scan_summary(scan_result)
            
            if scan_result.conflicts:
                self._print_conflicts_table(scan_result.conflicts)
            else:
                self.console.print("\n✅ No conflicts detected!", style="green bold")
            
            if scan_result.hooks:
                self._print_hooks_summary(scan_result.hooks)
        
        return capture.get()
    
    def _print_scan_summary(self, scan_result: ScanResult):
        """Print scan summary with rich formatting."""
        self.console.print("\n📊 Scan Summary", style="bold blue")
        
        summary_table = Table(show_header=False, box=None)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="white")
        
        summary_table.add_row("Scan ID", scan_result.scan_id)
        summary_table.add_row("Timestamp", scan_result.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        summary_table.add_row("Scan Path", str(scan_result.scan_path))
        summary_table.add_row("Scan Type", scan_result.scan_type)
        summary_table.add_row("Apps Scanned", str(scan_result.total_apps))
        summary_table.add_row("Hooks Found", str(scan_result.total_hooks))
        summary_table.add_row("Conflicts Detected", str(scan_result.total_conflicts))
        summary_table.add_row("Duration", f"{scan_result.scan_duration:.3f}s")
        
        # Add critical status
        if scan_result.has_critical_conflicts():
            summary_table.add_row("Status", Text("❌ CRITICAL CONFLICTS", style="red bold"))
        else:
            summary_table.add_row("Status", Text("✅ No Critical Issues", style="green"))
        
        self.console.print(summary_table)
    
    def _print_conflicts_table(self, conflicts: List[ConflictReport]):
        """Print conflicts in a rich table format."""
        if not conflicts:
            return
        
        self.console.print(f"\n🔍 Conflicts Detected ({len(conflicts)})", style="bold red")
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Severity", width=10)
        table.add_column("Hook Type", width=15)
        table.add_column("Hook Name", width=20)
        table.add_column("Target", width=15)
        table.add_column("Apps", width=25)
        table.add_column("Winner", width=15)
        
        for conflict in conflicts:
            # Format severity with color and icon
            severity_text = Text(
                f"{self.severity_icons[conflict.severity]} {conflict.severity.value.upper()}",
                style=self.severity_colors[conflict.severity]
            )
            
            # Format apps list
            apps = ", ".join(conflict.get_affected_apps())
            if len(apps) > 23:
                apps = apps[:20] + "..."
            
            # Format winner
            winner_text = conflict.winner.app_name if conflict.winner else "N/A"
            
            table.add_row(
                severity_text,
                conflict.hook_type.value,
                conflict.hook_name,
                conflict.target or "N/A",
                apps,
                winner_text,
            )
        
        self.console.print(table)
        
        # Print detailed conflict descriptions
        self.console.print("\n📝 Conflict Details", style="bold yellow")
        for i, conflict in enumerate(conflicts, 1):
            self.console.print(f"\n{i}. {conflict.description}")
            if conflict.resolution_hint:
                self.console.print(f"   💡 {conflict.resolution_hint}", style="dim")
    
    def _print_hooks_summary(self, hooks: List[HookDefinition]):
        """Print hooks summary statistics."""
        if not hooks:
            return
        
        self.console.print(f"\n📋 Hooks Summary ({len(hooks)} total)", style="bold green")
        
        # Group by app
        by_app = {}
        by_type = {}
        
        for hook in hooks:
            by_app[hook.app_name] = by_app.get(hook.app_name, 0) + 1
            by_type[hook.hook_type.value] = by_type.get(hook.hook_type.value, 0) + 1
        
        # Apps table
        if by_app:
            app_table = Table(title="Hooks by App", show_header=True)
            app_table.add_column("App Name", style="cyan")
            app_table.add_column("Hook Count", style="white", justify="right")
            
            for app_name, count in sorted(by_app.items()):
                app_table.add_row(app_name, str(count))
            
            self.console.print(app_table)
        
        # Types table
        if by_type:
            type_table = Table(title="Hooks by Type", show_header=True)
            type_table.add_column("Hook Type", style="cyan")
            type_table.add_column("Count", style="white", justify="right")
            
            for hook_type, count in sorted(by_type.items()):
                type_table.add_row(hook_type, str(count))
            
            self.console.print(type_table)
    
    def _generate_json_report(self, scan_result: ScanResult) -> str:
        """Generate JSON report with optimized serialization."""
        # Convert to dictionary for serialization
        data = scan_result.dict()
        
        # Convert Path objects and enums to strings
        def serialize_obj(obj):
            if hasattr(obj, '__dict__'):
                return {k: serialize_obj(v) for k, v in obj.__dict__.items()}
            elif isinstance(obj, list):
                return [serialize_obj(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: serialize_obj(v) for k, v in obj.items()}
            elif hasattr(obj, 'value'):  # Enum
                return obj.value
            elif hasattr(obj, '__str__'):  # Path, datetime, etc.
                return str(obj)
            return obj
        
        serialized_data = serialize_obj(data)
        
        # Use orjson for better performance if available
        if HAS_ORJSON:
            return orjson.dumps(serialized_data, option=orjson.OPT_INDENT_2).decode('utf-8')
        else:
            return json.dumps(serialized_data, indent=2, ensure_ascii=False)
    
    def _generate_csv_report(self, scan_result: ScanResult) -> str:
        """Generate CSV report for conflicts."""
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "Scan ID", "Timestamp", "Severity", "Hook Type", "Hook Name", 
            "Target", "Apps", "Winner", "Description", "Resolution Hint"
        ])
        
        # Write conflict data
        for conflict in scan_result.conflicts:
            apps = "; ".join(conflict.get_affected_apps())
            winner = conflict.winner.app_name if conflict.winner else ""
            
            writer.writerow([
                scan_result.scan_id,
                scan_result.timestamp.isoformat(),
                conflict.severity.value,
                conflict.hook_type.value,
                conflict.hook_name,
                conflict.target or "",
                apps,
                winner,
                conflict.description,
                conflict.resolution_hint or "",
            ])
        
        return output.getvalue()
    
    def _generate_html_report(self, scan_result: ScanResult) -> str:
        """Generate HTML report with styling."""
        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "<title>FrappEye Scan Report</title>",
            "<style>",
            self._get_html_styles(),
            "</style>",
            "</head>",
            "<body>",
            f"<h1>FrappEye Scan Report</h1>",
            self._generate_html_summary(scan_result),
        ]
        
        if scan_result.conflicts:
            html_parts.extend([
                "<h2>Conflicts Detected</h2>",
                self._generate_html_conflicts_table(scan_result.conflicts),
            ])
        else:
            html_parts.append("<h2 class='success'>✅ No conflicts detected!</h2>")
        
        html_parts.extend([
            "</body>",
            "</html>",
        ])
        
        return "\n".join(html_parts)
    
    def _get_html_styles(self) -> str:
        """Get CSS styles for HTML report."""
        return """
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #2c3e50; }
        h2 { color: #34495e; }
        .summary { background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .summary-item { margin: 5px 0; }
        .success { color: #27ae60; }
        .critical { color: #e74c3c; font-weight: bold; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .severity-critical { background-color: #ffebee; color: #c62828; }
        .severity-high { background-color: #fff3e0; color: #ef6c00; }
        .severity-medium { background-color: #fffde7; color: #f57f17; }
        .severity-low { background-color: #e3f2fd; color: #1565c0; }
        .severity-info { background-color: #e8f5e8; color: #2e7d32; }
        """
    
    def _generate_html_summary(self, scan_result: ScanResult) -> str:
        """Generate HTML summary section."""
        status_class = "critical" if scan_result.has_critical_conflicts() else "success"
        status_text = "❌ CRITICAL CONFLICTS" if scan_result.has_critical_conflicts() else "✅ No Critical Issues"
        
        return f"""
        <div class="summary">
            <div class="summary-item"><strong>Scan ID:</strong> {scan_result.scan_id}</div>
            <div class="summary-item"><strong>Timestamp:</strong> {scan_result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</div>
            <div class="summary-item"><strong>Scan Path:</strong> {scan_result.scan_path}</div>
            <div class="summary-item"><strong>Apps Scanned:</strong> {scan_result.total_apps}</div>
            <div class="summary-item"><strong>Hooks Found:</strong> {scan_result.total_hooks}</div>
            <div class="summary-item"><strong>Conflicts:</strong> {scan_result.total_conflicts}</div>
            <div class="summary-item"><strong>Duration:</strong> {scan_result.scan_duration:.3f}s</div>
            <div class="summary-item"><strong>Status:</strong> <span class="{status_class}">{status_text}</span></div>
        </div>
        """
    
    def _generate_html_conflicts_table(self, conflicts: List[ConflictReport]) -> str:
        """Generate HTML table for conflicts."""
        if not conflicts:
            return ""
        
        rows = []
        for conflict in conflicts:
            severity_class = f"severity-{conflict.severity.value}"
            apps = ", ".join(conflict.get_affected_apps())
            winner = conflict.winner.app_name if conflict.winner else "N/A"
            
            rows.append(f"""
            <tr class="{severity_class}">
                <td>{conflict.severity.value.upper()}</td>
                <td>{conflict.hook_type.value}</td>
                <td>{conflict.hook_name}</td>
                <td>{conflict.target or 'N/A'}</td>
                <td>{apps}</td>
                <td>{winner}</td>
                <td>{conflict.description}</td>
            </tr>
            """)
        
        return f"""
        <table>
            <thead>
                <tr>
                    <th>Severity</th>
                    <th>Hook Type</th>
                    <th>Hook Name</th>
                    <th>Target</th>
                    <th>Apps</th>
                    <th>Winner</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        """
    
    def _generate_markdown_report(self, scan_result: ScanResult) -> str:
        """Generate Markdown report."""
        md_parts = [
            "# FrappEye Scan Report",
            "",
            "## Summary",
            "",
            f"- **Scan ID:** {scan_result.scan_id}",
            f"- **Timestamp:** {scan_result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            f"- **Scan Path:** `{scan_result.scan_path}`",
            f"- **Apps Scanned:** {scan_result.total_apps}",
            f"- **Hooks Found:** {scan_result.total_hooks}",
            f"- **Conflicts:** {scan_result.total_conflicts}",
            f"- **Duration:** {scan_result.scan_duration:.3f}s",
            "",
        ]
        
        # Status
        if scan_result.has_critical_conflicts():
            md_parts.append("**Status:** ❌ CRITICAL CONFLICTS DETECTED")
        else:
            md_parts.append("**Status:** ✅ No Critical Issues")
        
        md_parts.append("")
        
        # Conflicts section
        if scan_result.conflicts:
            md_parts.extend([
                "## Conflicts Detected",
                "",
                "| Severity | Hook Type | Hook Name | Target | Apps | Winner | Description |",
                "|----------|-----------|-----------|--------|------|--------|-------------|",
            ])
            
            for conflict in scan_result.conflicts:
                apps = ", ".join(conflict.get_affected_apps())
                winner = conflict.winner.app_name if conflict.winner else "N/A"
                
                md_parts.append(
                    f"| {conflict.severity.value.upper()} | {conflict.hook_type.value} | "
                    f"{conflict.hook_name} | {conflict.target or 'N/A'} | {apps} | "
                    f"{winner} | {conflict.description} |"
                )
        else:
            md_parts.extend([
                "## Conflicts",
                "",
                "✅ No conflicts detected!",
            ])
        
        return "\n".join(md_parts)
    
    def print_quick_summary(self, scan_result: ScanResult):
        """Print a quick summary to console."""
        if scan_result.has_critical_conflicts():
            self.console.print(f"❌ Found {scan_result.total_conflicts} conflicts ({len([c for c in scan_result.conflicts if c.severity == ConflictSeverity.CRITICAL])} critical)", style="red bold")
        elif scan_result.total_conflicts > 0:
            self.console.print(f"⚠️  Found {scan_result.total_conflicts} conflicts (no critical)", style="yellow")
        else:
            self.console.print("✅ No conflicts detected!", style="green bold")
    
    def export_for_ci(self, scan_result: ScanResult, output_file: Union[str, Path]) -> bool:
        """
        Export scan results in CI-friendly format.
        
        Returns:
            True if critical conflicts found (should fail CI), False otherwise
        """
        # Generate JSON report for CI consumption
        json_report = self._generate_json_report(scan_result)
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(json_report)
        
        return scan_result.has_critical_conflicts()