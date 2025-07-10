#!/usr/bin/env python3
"""
Basic tests for VSCode Sync Tool
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

# Import the main module (adjust path as needed)
import sys
sys.path.insert(0, 'vscode_sync')
from main import VSCodeSync, get_recommendations

class TestVSCodeSync(unittest.TestCase):
    
    def setUp(self):
        self.sync = VSCodeSync()
    
    def test_init(self):
        """Test VSCodeSync initialization"""
        self.assertIsNotNone(self.sync.system)
        self.assertIsNotNone(self.sync.settings_path)
        self.assertIsNotNone(self.sync.extensions_path)
    
    def test_settings_path_detection(self):
        """Test settings path detection for different OS"""
        # The path should be a Path object
        self.assertIsInstance(self.sync.settings_path, Path)
        
        # Should contain expected path components
        path_str = str(self.sync.settings_path)
        self.assertTrue(any(x in path_str for x in ['Code', 'User', 'settings.json']))
    
    @patch('subprocess.run')
    def test_check_vscode_installed_success(self, mock_run):
        """Test VSCode installation check - success case"""
        mock_run.return_value.returncode = 0
        self.assertTrue(self.sync._check_vscode_installed())
    
    @patch('subprocess.run')
    def test_check_vscode_installed_failure(self, mock_run):
        """Test VSCode installation check - failure case"""
        mock_run.side_effect = FileNotFoundError()
        self.assertFalse(self.sync._check_vscode_installed())
    
    @patch('subprocess.run')
    def test_get_installed_extensions_success(self, mock_run):
        """Test getting installed extensions - success case"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "ext1\next2\next3\n"
        
        extensions = self.sync.get_installed_extensions()
        self.assertEqual(extensions, ["ext1", "ext2", "ext3"])
    
    @patch('subprocess.run')
    def test_get_installed_extensions_failure(self, mock_run):
        """Test getting installed extensions - failure case"""
        mock_run.side_effect = FileNotFoundError()
        extensions = self.sync.get_installed_extensions()
        self.assertEqual(extensions, [])
    
    def test_get_settings_file_not_found(self):
        """Test getting settings when file doesn't exist"""
        with patch.object(self.sync.settings_path, 'exists', return_value=False):
            settings = self.sync.get_settings()
            self.assertEqual(settings, {})
    
    def test_get_settings_success(self):
        """Test getting settings successfully"""
        mock_settings = {"editor.fontSize": 14, "workbench.colorTheme": "Dark+"}
        
        with patch.object(self.sync.settings_path, 'exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=json.dumps(mock_settings))):
                settings = self.sync.get_settings()
                self.assertEqual(settings, mock_settings)
    
    def test_get_settings_invalid_json(self):
        """Test getting settings with invalid JSON"""
        with patch.object(self.sync.settings_path, 'exists', return_value=True):
            with patch('builtins.open', mock_open(read_data="invalid json")):
                settings = self.sync.get_settings()
                self.assertEqual(settings, {})
    
    def test_export_to_json(self):
        """Test exporting configuration to JSON"""
        config = {
            "metadata": {"created_at": "2025-01-15T10:30:00"},
            "extensions": ["ext1", "ext2"],
            "settings": {"editor.fontSize": 14}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            result = self.sync._export_to_json(config, temp_path)
            self.assertTrue(result)
            
            # Verify file contents
            with open(temp_path, 'r') as f:
                loaded_config = json.load(f)
                self.assertEqual(loaded_config, config)
        finally:
            temp_path.unlink()
    
    def test_import_from_json(self):
        """Test importing configuration from JSON"""
        config = {
            "metadata": {"created_at": "2025-01-15T10:30:00"},
            "extensions": ["ext1", "ext2"],
            "settings": {"editor.fontSize": 14}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            temp_path = Path(f.name)
        
        try:
            result = self.sync._import_from_json(temp_path)
            self.assertEqual(result, config)
        finally:
            temp_path.unlink()
    
    def test_import_from_json_invalid(self):
        """Test importing from invalid JSON file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json")
            temp_path = Path(f.name)
        
        try:
            result = self.sync._import_from_json(temp_path)
            self.assertIsNone(result)
        finally:
            temp_path.unlink()


class TestRecommendations(unittest.TestCase):
    
    def test_get_recommendations_frontend(self):
        """Test getting recommendations for frontend development"""
        recommendations = get_recommendations("frontend", ["javascript", "typescript"])
        
        # Should include base extensions
        self.assertIn("ms-vscode.vscode-typescript-next", recommendations)
        self.assertIn("esbenp.prettier-vscode", recommendations)
        
        # Should include frontend-specific extensions
        self.assertTrue(any("react" in ext.lower() for ext in recommendations))
    
    def test_get_recommendations_backend(self):
        """Test getting recommendations for backend development"""
        recommendations = get_recommendations("backend", ["python", "node"])
        
        # Should include base extensions
        self.assertIn("ms-python.python", recommendations)
        
        # Should include backend-specific extensions
        self.assertIn("ms-vscode.vscode-docker", recommendations)
    
    def test_get_recommendations_data_science(self):
        """Test getting recommendations for data science"""
        recommendations = get_recommendations("data-science", ["python"])
        
        # Should include Python and Jupyter extensions
        self.assertIn("ms-python.python", recommendations)
        self.assertIn("ms-toolsai.jupyter", recommendations)
    
    def test_get_recommendations_removes_duplicates(self):
        """Test that recommendations don't include duplicates"""
        recommendations = get_recommendations("fullstack", ["javascript", "python"])
        
        # Should not have duplicates
        self.assertEqual(len(recommendations), len(set(recommendations)))


class TestCLIIntegration(unittest.TestCase):
    """Integration tests for CLI functionality"""
    
    def test_config_export_import_cycle(self):
        """Test full export/import cycle"""
        sync = VSCodeSync()
        
        # Mock data
        mock_extensions = ["ext1", "ext2", "ext3"]
        mock_settings = {"editor.fontSize": 14, "workbench.colorTheme": "Dark+"}
        
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            # Mock the methods to return test data
            with patch.object(sync, 'get_installed_extensions', return_value=mock_extensions):
                with patch.object(sync, 'get_settings', return_value=mock_settings):
                    # Export
                    export_success = sync.export_config(str(temp_path))
                    self.assertTrue(export_success)
                    
                    # Verify file was created
                    self.assertTrue(temp_path.exists())
                    
                    # Import back
                    imported_config = sync._import_from_json(temp_path)
                    self.assertIsNotNone(imported_config)
                    
                    # Verify data integrity
                    self.assertEqual(imported_config['extensions'], mock_extensions)
                    self.assertEqual(imported_config['settings'], mock_settings)
                    
        finally:
            if temp_path.exists():
                temp_path.unlink()


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
