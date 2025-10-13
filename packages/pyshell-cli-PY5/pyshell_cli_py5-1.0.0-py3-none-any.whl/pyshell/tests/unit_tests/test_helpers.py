#!/usr/bin/env python3
"""
Unit tests for helpers.py utility functions
"""

import unittest
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# pylint: disable=wrong-import-position
from utils.helpers import resolve_path


class TestResolvePath(unittest.TestCase):
    """Test resolve_path function"""

    def setUp(self):
        """Set up test fixtures"""
        # Use absolute path that works on both Windows and Unix
        self.current_dir = Path.cwd() / "test_project"

    def test_resolve_relative_path(self):
        """Test resolving relative path"""
        result = resolve_path("file.txt", self.current_dir)
        self.assertEqual(result, self.current_dir / "file.txt")

    def test_resolve_absolute_path(self):
        """Test resolving absolute path"""
        abs_path = Path.cwd().drive + "/test/absolute" if Path.cwd().drive else "/etc/hosts"
        result = resolve_path(abs_path, self.current_dir)
        # Absolute paths should remain unchanged
        self.assertTrue(result.is_absolute())

    def test_resolve_parent_directory(self):
        """Test resolving parent directory (..)"""
        result = resolve_path("../file.txt", self.current_dir)
        # Result should contain the parent path logic
        expected = self.current_dir / "../file.txt"
        self.assertEqual(result, expected)

    def test_resolve_current_directory(self):
        """Test resolving current directory (.)"""
        result = resolve_path("./file.txt", self.current_dir)
        self.assertEqual(result, self.current_dir / "file.txt")

    def test_resolve_tilde_expansion(self):
        """Test tilde expansion"""
        result = resolve_path("~/documents/file.txt", self.current_dir)
        expected = Path.home() / "documents" / "file.txt"
        self.assertEqual(result, expected)

    def test_resolve_tilde_disabled(self):
        """Test tilde expansion when disabled"""
        result = resolve_path("~/documents", self.current_dir, expand_user=False)
        self.assertEqual(result, self.current_dir / "~/documents")

    def test_resolve_path_object(self):
        """Test resolving Path object instead of string"""
        result = resolve_path(Path("file.txt"), self.current_dir)
        self.assertEqual(result, self.current_dir / "file.txt")

    def test_resolve_with_symlinks(self):
        """Test path resolution with symlink resolution enabled"""
        # This test will actually resolve symlinks if they exist
        result = resolve_path(".", self.current_dir, resolve_symlinks=True)
        # Result should be an absolute path
        self.assertTrue(result.is_absolute())


if __name__ == '__main__':
    unittest.main()
