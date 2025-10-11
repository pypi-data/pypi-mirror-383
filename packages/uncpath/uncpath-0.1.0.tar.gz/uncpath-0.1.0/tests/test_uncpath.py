"""
Tests for uncpath module
"""
import pytest
from uncpath import is_unc_path, normalize_unc_path, __version__


def test_version():
    """Test that version is defined"""
    assert __version__ == "0.1.0"


class TestIsUncPath:
    """Tests for is_unc_path function"""
    
    def test_unc_path_with_backslashes(self):
        """Test UNC path with backslashes"""
        assert is_unc_path(r"\\server\share\file.txt") is True
    
    def test_unc_path_with_forward_slashes(self):
        """Test UNC path with forward slashes"""
        assert is_unc_path("//server/share/file.txt") is True
    
    def test_regular_windows_path(self):
        """Test regular Windows path"""
        assert is_unc_path(r"C:\Users\test\file.txt") is False
    
    def test_regular_unix_path(self):
        """Test regular Unix path"""
        assert is_unc_path("/home/user/file.txt") is False
    
    def test_empty_path(self):
        """Test empty path"""
        assert is_unc_path("") is False
    
    def test_relative_path(self):
        """Test relative path"""
        assert is_unc_path("folder/file.txt") is False


class TestNormalizeUncPath:
    """Tests for normalize_unc_path function"""
    
    def test_normalize_backslashes(self):
        """Test normalizing backslashes to forward slashes"""
        result = normalize_unc_path(r"\\server\share\folder\file.txt")
        assert result == "//server/share/folder/file.txt"
    
    def test_already_normalized(self):
        """Test path that's already normalized"""
        result = normalize_unc_path("//server/share/file.txt")
        assert result == "//server/share/file.txt"
    
    def test_mixed_slashes(self):
        """Test path with mixed slashes"""
        result = normalize_unc_path(r"\\server/share\file.txt")
        assert result == "//server/share/file.txt"
    
    def test_empty_path(self):
        """Test empty path"""
        result = normalize_unc_path("")
        assert result == ""
