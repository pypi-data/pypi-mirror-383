"""
Tests for download functionality
"""

import os
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock

from xiaoshiai_hub.download import (
    _match_pattern,
    _should_download_file,
    hf_hub_download,
    snapshot_download,
)


class TestPatternMatching(unittest.TestCase):
    """Test pattern matching functions."""
    
    def test_match_pattern_exact(self):
        """Test exact pattern matching."""
        self.assertTrue(_match_pattern("config.yaml", "config.yaml"))
        self.assertFalse(_match_pattern("config.yml", "config.yaml"))
    
    def test_match_pattern_wildcard(self):
        """Test wildcard pattern matching."""
        self.assertTrue(_match_pattern("config.yaml", "*.yaml"))
        self.assertTrue(_match_pattern("model.yml", "*.yml"))
        self.assertFalse(_match_pattern("config.txt", "*.yaml"))
    
    def test_match_pattern_prefix(self):
        """Test prefix pattern matching."""
        self.assertTrue(_match_pattern("config.yaml", "config*"))
        self.assertTrue(_match_pattern("config_v2.yaml", "config*"))
        self.assertFalse(_match_pattern("model.yaml", "config*"))
    
    def test_should_download_file_no_patterns(self):
        """Test file download decision with no patterns."""
        self.assertTrue(_should_download_file("config.yaml"))
        self.assertTrue(_should_download_file("model.bin"))
    
    def test_should_download_file_allow_patterns(self):
        """Test file download decision with allow patterns."""
        allow = ["*.yaml", "*.yml"]
        self.assertTrue(_should_download_file("config.yaml", allow_patterns=allow))
        self.assertTrue(_should_download_file("model.yml", allow_patterns=allow))
        self.assertFalse(_should_download_file("model.bin", allow_patterns=allow))
    
    def test_should_download_file_ignore_patterns(self):
        """Test file download decision with ignore patterns."""
        ignore = [".git*", "*.tmp"]
        self.assertFalse(_should_download_file(".gitignore", ignore_patterns=ignore))
        self.assertFalse(_should_download_file("temp.tmp", ignore_patterns=ignore))
        self.assertTrue(_should_download_file("config.yaml", ignore_patterns=ignore))
    
    def test_should_download_file_both_patterns(self):
        """Test file download decision with both allow and ignore patterns."""
        allow = ["*.yaml", "*.yml"]
        ignore = [".git*"]
        
        self.assertTrue(_should_download_file("config.yaml", allow, ignore))
        self.assertFalse(_should_download_file(".gitignore", allow, ignore))
        self.assertFalse(_should_download_file("model.bin", allow, ignore))


class TestDownloadFunctions(unittest.TestCase):
    """Test download functions."""
    
    @patch('xiaoshiai_hub.download.HubClient')
    def test_hf_hub_download(self, mock_client_class):
        """Test hf_hub_download function."""
        # Setup mock
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_repo_info = Mock()
        mock_repo_info.default_branch = "main"
        mock_client.get_repository_info.return_value = mock_repo_info
        
        # Test download
        with tempfile.TemporaryDirectory() as tmpdir:
            result = hf_hub_download(
                repo_id="demo/demo",
                filename="config.yaml",
                local_dir=tmpdir,
                username="test",
                password="test",
            )
            
            # Verify client was created with correct params
            mock_client_class.assert_called_once()
            
            # Verify download was called
            mock_client.download_file.assert_called_once()
            
            # Verify result path
            self.assertIn("config.yaml", result)
    
    @patch('xiaoshiai_hub.download.HubClient')
    def test_snapshot_download(self, mock_client_class):
        """Test snapshot_download function."""
        # Setup mock
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        
        mock_repo_info = Mock()
        mock_repo_info.default_branch = "main"
        mock_client.get_repository_info.return_value = mock_repo_info
        
        # Mock content structure
        mock_file = Mock()
        mock_file.type = "file"
        mock_file.path = "config.yaml"
        
        mock_content = Mock()
        mock_content.entries = [mock_file]
        mock_client.get_repository_content.return_value = mock_content
        
        # Test download
        with tempfile.TemporaryDirectory() as tmpdir:
            result = snapshot_download(
                repo_id="demo/demo",
                local_dir=tmpdir,
                username="test",
                password="test",
                verbose=False,
            )
            
            # Verify client was created
            mock_client_class.assert_called_once()
            
            # Verify download was called
            mock_client.download_file.assert_called()
            
            # Verify result path
            self.assertEqual(result, tmpdir)


if __name__ == '__main__':
    unittest.main()

