"""
Tests for the HookScanner module with comprehensive coverage.

Tests scanning functionality, performance, caching, and error handling
across different Frappe structures and configurations.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from frappeye.core.scanner import HookScanner
from frappeye.core.models import HookDefinition, HookType


class TestHookScanner:
    """Test suite for HookScanner class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.scanner = HookScanner(max_workers=2, enable_cache=True)
    
    def test_scanner_initialization(self):
        """Test scanner initialization with different options."""
        # Default initialization
        scanner = HookScanner()
        assert scanner.max_workers > 0
        assert scanner.enable_cache is True
        
        # Custom initialization
        scanner = HookScanner(max_workers=4, enable_cache=False)
        assert scanner.max_workers == 4
        assert scanner.enable_cache is False
    
    def test_scan_app_with_valid_hooks(self):
        """Test scanning app with valid hooks.py file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            app_path = Path(temp_dir) / "test_app"
            app_path.mkdir()
            
            # Create __init__.py
            (app_path / "__init__.py").write_text("")
            
            # Create hooks.py with sample hooks
            hooks_content = '''
doc_events = {
    "Sales Invoice": {
        "before_save": "test_app.hooks.before_save_sales_invoice"
    }
}

override_whitelisted_methods = {
    "frappe.desk.form.save.savedocs": "test_app.overrides.custom_savedocs"
}
'''
            (app_path / "hooks.py").write_text(hooks_content)
            
            # Scan the app
            hooks = self.scanner.scan_app(app_path)
            
            # Verify results
            assert len(hooks) >= 2
            
            # Check doc_events hook
            doc_event_hooks = [h for h in hooks if h.hook_type == HookType.DOC_EVENTS]
            assert len(doc_event_hooks) >= 1
            
            # Check override hook
            override_hooks = [h for h in hooks if h.hook_type == HookType.OVERRIDE_WHITELISTED_METHODS]
            assert len(override_hooks) >= 1
    
    def test_scan_app_without_hooks(self):
        """Test scanning app without hooks.py file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            app_path = Path(temp_dir) / "test_app"
            app_path.mkdir()
            
            # Create __init__.py only
            (app_path / "__init__.py").write_text("")
            
            # Scan the app
            hooks = self.scanner.scan_app(app_path)
            
            # Should return empty list
            assert hooks == []
    
    def test_scan_invalid_app_path(self):
        """Test scanning invalid app path."""
        with pytest.raises(ValueError):
            self.scanner.scan_app("/nonexistent/path")
    
    def test_scan_multiple_apps(self):
        """Test scanning multiple apps in parallel."""
        with tempfile.TemporaryDirectory() as temp_dir:
            app_paths = []
            
            # Create multiple test apps
            for i in range(3):
                app_path = Path(temp_dir) / f"test_app_{i}"
                app_path.mkdir()
                
                # Create __init__.py
                (app_path / "__init__.py").write_text("")
                
                # Create hooks.py
                hooks_content = f'''
scheduler_events = {{
    "daily": ["test_app_{i}.tasks.daily_task"]
}}
'''
                (app_path / "hooks.py").write_text(hooks_content)
                app_paths.append(app_path)
            
            # Scan multiple apps
            hooks = self.scanner.scan_multiple_apps(app_paths)
            
            # Should have hooks from all apps
            assert len(hooks) >= 3
            
            # Check that we have hooks from different apps
            app_names = {h.app_name for h in hooks}
            assert len(app_names) == 3
    
    def test_caching_functionality(self):
        """Test that caching works correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            app_path = Path(temp_dir) / "test_app"
            app_path.mkdir()
            
            # Create __init__.py and hooks.py
            (app_path / "__init__.py").write_text("")
            (app_path / "hooks.py").write_text('fixtures = ["test_fixture"]')
            
            # First scan
            hooks1 = self.scanner.scan_app(app_path)
            
            # Second scan (should use cache)
            hooks2 = self.scanner.scan_app(app_path)
            
            # Results should be identical
            assert len(hooks1) == len(hooks2)
            assert hooks1[0].handler == hooks2[0].handler
    
    def test_cache_disable(self):
        """Test disabling cache functionality."""
        scanner = HookScanner(enable_cache=False)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            app_path = Path(temp_dir) / "test_app"
            app_path.mkdir()
            
            # Create __init__.py and hooks.py
            (app_path / "__init__.py").write_text("")
            (app_path / "hooks.py").write_text('fixtures = ["test_fixture"]')
            
            # Scan twice
            hooks1 = scanner.scan_app(app_path)
            hooks2 = scanner.scan_app(app_path)
            
            # Should still work but not use cache
            assert len(hooks1) == len(hooks2)
    
    def test_validate_hooks_syntax_valid(self):
        """Test validation of valid hooks.py file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            hooks_file = Path(temp_dir) / "hooks.py"
            hooks_file.write_text('''
doc_events = {
    "User": {
        "before_save": "myapp.user.before_save"
    }
}
''')
            
            issues = self.scanner.validate_hooks_syntax(hooks_file)
            assert issues == []
    
    def test_validate_hooks_syntax_invalid(self):
        """Test validation of invalid hooks.py file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            hooks_file = Path(temp_dir) / "hooks.py"
            hooks_file.write_text('''
# Invalid Python syntax
doc_events = {
    "User": {
        "before_save": invalid_handler_format
    }
}
''')
            
            issues = self.scanner.validate_hooks_syntax(hooks_file)
            assert len(issues) > 0
    
    def test_clear_cache(self):
        """Test cache clearing functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            app_path = Path(temp_dir) / "test_app"
            app_path.mkdir()
            
            # Create __init__.py and hooks.py
            (app_path / "__init__.py").write_text("")
            (app_path / "hooks.py").write_text('fixtures = ["test_fixture"]')
            
            self.scanner.scan_app(app_path)
            self.scanner.clear_cache()
            assert len(self.scanner._scan_cache) == 0
    
    def test_performance_statistics(self):
        """Test performance statistics collection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            app_path = Path(temp_dir) / "test_app"
            app_path.mkdir()
            
            # Create __init__.py and hooks.py
            (app_path / "__init__.py").write_text("")
            (app_path / "hooks.py").write_text('fixtures = ["test_fixture"]')
            
            self.scanner.scan_app(app_path)
            stats = self.scanner.get_scan_statistics()
            assert isinstance(stats, dict)
    
    @patch('frappeye.utils.frappe_utils.FrappeUtils.parse_hooks_file')
    def test_error_handling_in_scan(self, mock_parse):
        """Test error handling during scanning."""
        mock_parse.side_effect = Exception("Parse error")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            app_path = Path(temp_dir) / "test_app"
            app_path.mkdir()
            
            # Create __init__.py and hooks.py
            (app_path / "__init__.py").write_text("")
            (app_path / "hooks.py").write_text('fixtures = ["test_fixture"]')
            
            hooks = self.scanner.scan_app(app_path)
            assert hooks == []