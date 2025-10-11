"""
CLI command implementations for frappeye with comprehensive functionality.

Implements all CLI commands with proper error handling, validation,
and user-friendly output formatting.
"""

import sys
from pathlib import Path
from typing import Optional

from rich.console import Console

from ..core.api import FrappEye
from ..utils.paths import PathUtils

console = Console()


def scan_command(ctx, path, site, output_format, output, min_severity, strict, no_cache, max_workers):
    """Implementation of the scan command."""
    try:
        # Show scan start message
        console.print(f"🔍 Scanning {path}...", style="blue")
        
        # Initialize FrappEye with options
        frappeye = FrappEye(
            max_workers=max_workers,
            enable_cache=not no_cache,
            strict_mode=strict,
            console_output=True,
        )
        
        # Perform scan
        result = frappeye.scan(
            path=path,
            site_name=site,
            output_format=output_format,
            output_file=output,
            min_severity=min_severity,
        )
        
        # Show completion message
        if result.has_critical_conflicts():
            console.print(f"\n❌ Scan completed with {result.total_conflicts} conflicts ({len([c for c in result.conflicts if c.severity.value == 'critical'])} critical)", style="red bold")
            if ctx.obj.get('verbose'):
                console.print(f"Scanned {result.total_apps} apps, found {result.total_hooks} hooks in {result.scan_duration:.3f}s")
        elif result.total_conflicts > 0:
            console.print(f"\n⚠️  Scan completed with {result.total_conflicts} non-critical conflicts", style="yellow")
            if ctx.obj.get('verbose'):
                console.print(f"Scanned {result.total_apps} apps, found {result.total_hooks} hooks in {result.scan_duration:.3f}s")
        else:
            console.print(f"\n✅ Scan completed successfully - no conflicts found!", style="green bold")
            if ctx.obj.get('verbose'):
                console.print(f"Scanned {result.total_apps} apps, found {result.total_hooks} hooks in {result.scan_duration:.3f}s")
        
        # Save output file message
        if output:
            console.print(f"📄 Report saved to: {output}", style="dim")
        
        return 0
        
    except Exception as e:
        console.print(f"❌ Scan failed: {e}", style="red bold")
        if ctx.obj.get('verbose'):
            import traceback
            console.print(traceback.format_exc(), style="dim red")
        return 2


def check_command(ctx, path, exit_code, critical_only, strict, quiet):
    """Implementation of the check command."""
    try:
        if not quiet:
            console.print(f"🔍 Checking {path} for conflicts...", style="blue")
        
        # Initialize FrappEye
        frappeye = FrappEye(
            strict_mode=strict,
            console_output=not quiet,
        )
        
        # Perform check
        if critical_only:
            has_issues = frappeye.has_critical_conflicts(path)
            issue_type = "critical conflicts"
        else:
            has_issues = frappeye.check_conflicts_only(path)
            issue_type = "conflicts"
        
        # Output results
        if has_issues:
            if not quiet:
                console.print(f"❌ Found {issue_type}", style="red bold")
            return 1 if exit_code else 0
        else:
            if not quiet:
                console.print(f"✅ No {issue_type} found", style="green bold")
            return 0
            
    except Exception as e:
        if not quiet:
            console.print(f"❌ Check failed: {e}", style="red bold")
            if ctx.obj.get('verbose'):
                import traceback
                console.print(traceback.format_exc(), style="dim red")
        return 2


def validate_command(ctx, path, fix):
    """Implementation of the validate command."""
    try:
        console.print(f"🔧 Validating hooks in {path}...", style="blue")
        
        # Initialize FrappEye
        frappeye = FrappEye(console_output=True)
        
        # Determine what to validate
        path_obj = Path(path)
        
        if path_obj.is_file() and path_obj.name == "hooks.py":
            # Single hooks.py file
            issues = frappeye.validate_hooks(path_obj)
            files_checked = [path_obj]
            
        elif path_obj.is_dir() and PathUtils.is_frappe_app(path_obj):
            # Single app
            issues = frappeye.validate_hooks(path_obj)
            hooks_file = PathUtils.get_hooks_file_path(path_obj)
            files_checked = [hooks_file] if hooks_file else []
            
        elif path_obj.is_dir() and PathUtils.is_frappe_bench(path_obj):
            # Entire bench
            issues = []
            files_checked = []
            
            apps = PathUtils.discover_apps_in_bench(path_obj)
            for app_path in apps:
                hooks_file = PathUtils.get_hooks_file_path(app_path)
                if hooks_file:
                    app_issues = frappeye.validate_hooks(hooks_file)
                    issues.extend([f"{app_path.name}: {issue}" for issue in app_issues])
                    files_checked.append(hooks_file)
        else:
            console.print(f"❌ Invalid path: {path}", style="red")
            return 2
        
        # Report results
        console.print(f"\n📊 Validation Results:", style="bold")
        console.print(f"Files checked: {len(files_checked)}")
        
        if issues:
            console.print(f"Issues found: {len(issues)}", style="red")
            console.print("\n🔍 Issues:", style="bold red")
            
            for issue in issues:
                console.print(f"  • {issue}", style="red")
            
            if fix:
                console.print(f"\n🔧 Auto-fix is not yet implemented", style="yellow")
                console.print("Please fix the issues manually", style="dim")
            
            return 1
        else:
            console.print("Issues found: 0", style="green")
            console.print("\n✅ All hooks.py files are valid!", style="green bold")
            return 0
            
    except Exception as e:
        console.print(f"❌ Validation failed: {e}", style="red bold")
        if ctx.obj.get('verbose'):
            import traceback
            console.print(traceback.format_exc(), style="dim red")
        return 2


def export_command(ctx, path, output_file, export_format, site, fail_on_conflicts, fail_on_critical):
    """Implementation of the export command."""
    try:
        console.print(f"📤 Exporting scan results from {path}...", style="blue")
        
        # Initialize FrappEye
        frappeye = FrappEye(console_output=False)
        
        # Perform scan
        result = frappeye.scan(
            path=path,
            site_name=site,
            output_format=export_format,
            output_file=output_file,
        )
        
        # Determine exit code based on options
        exit_code = 0
        
        if fail_on_critical and result.has_critical_conflicts():
            exit_code = 1
            console.print(f"❌ Critical conflicts found - failing as requested", style="red bold")
        elif fail_on_conflicts and result.total_conflicts > 0:
            exit_code = 1
            console.print(f"❌ Conflicts found - failing as requested", style="red bold")
        
        # Success message
        console.print(f"✅ Export completed: {output_file}", style="green")
        console.print(f"📊 Summary: {result.total_apps} apps, {result.total_hooks} hooks, {result.total_conflicts} conflicts", style="dim")
        
        return exit_code
        
    except Exception as e:
        console.print(f"❌ Export failed: {e}", style="red bold")
        if ctx.obj.get('verbose'):
            import traceback
            console.print(traceback.format_exc(), style="dim red")
        return 2


def _format_file_list(files, max_display=5):
    """Format list of files for display."""
    if not files:
        return "None"
    
    if len(files) <= max_display:
        return ", ".join(str(f) for f in files)
    else:
        displayed = ", ".join(str(f) for f in files[:max_display])
        return f"{displayed} ... and {len(files) - max_display} more"


def _get_scan_type_description(path):
    """Get human-readable description of scan type."""
    path_obj = Path(path)
    
    if PathUtils.is_frappe_bench(path_obj):
        return "Frappe bench"
    elif PathUtils.is_frappe_site(path_obj):
        return "Frappe site"
    elif PathUtils.is_frappe_app(path_obj):
        return "Frappe app"
    else:
        return "Unknown"