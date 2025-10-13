#!/usr/bin/env python3
"""
Unit tests for file_ops.py utility functions
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# pylint: disable=wrong-import-position
from utils.file_ops import list_directory, find_files, format_file_listing, safe_remove_directory


class TestListDirectory(unittest.TestCase):
    """Test list_directory function"""

    def setUp(self):
        """Create temporary test directory"""
        self.test_dir = Path(tempfile.mkdtemp())
        (self.test_dir / "file1.txt").touch()
        (self.test_dir / "file2.txt").touch()
        (self.test_dir / ".hidden").touch()
        (self.test_dir / "subdir").mkdir()
        (self.test_dir / "subdir" / "nested.txt").touch()

    def tearDown(self):
        """Clean up test directory"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_list_non_recursive(self):
        """Test non-recursive directory listing"""
        items = list(list_directory(self.test_dir))
        names = [item.name for item in items]
        self.assertEqual(len(items), 3)  # 2 files + 1 subdir (no hidden)
        self.assertIn("file1.txt", names)
        self.assertNotIn(".hidden", names)

    def test_list_recursive(self):
        """Test recursive directory listing"""
        items = list(list_directory(self.test_dir, recursive=True))
        names = [item.name for item in items]
        self.assertIn("nested.txt", names)

    def test_list_show_hidden(self):
        """Test listing with hidden files"""
        items = list(list_directory(self.test_dir, show_hidden=True))
        names = [item.name for item in items]
        self.assertIn(".hidden", names)

    def test_list_nonexistent(self):
        """Test listing non-existent directory"""
        with self.assertRaises(FileNotFoundError):
            list(list_directory(self.test_dir / "nonexistent"))


class TestFindFiles(unittest.TestCase):
    """Test find_files function"""

    def setUp(self):
        """Create temporary test directory"""
        self.test_dir = Path(tempfile.mkdtemp())
        (self.test_dir / "test.txt").touch()
        (self.test_dir / "test.py").touch()
        (self.test_dir / "data.json").touch()
        (self.test_dir / "subdir").mkdir()
        (self.test_dir / "subdir" / "nested.txt").touch()

    def tearDown(self):
        """Clean up test directory"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_find_pattern(self):
        """Test finding files by pattern"""
        items = list(find_files(self.test_dir, r'\.txt$'))
        names = [item.name for item in items]
        self.assertEqual(len(items), 2)
        self.assertIn("test.txt", names)
        self.assertIn("nested.txt", names)

    def test_find_with_maxdepth(self):
        """Test finding files with depth limit"""
        items = list(find_files(self.test_dir, r'\.txt$', maxdepth=0))
        names = [item.name for item in items]
        self.assertEqual(len(items), 1)
        self.assertNotIn("nested.txt", names)

    def test_find_invalid_pattern(self):
        """Test finding with invalid regex pattern"""
        with self.assertRaises(ValueError):
            list(find_files(self.test_dir, r'['))


class TestFormatFileListing(unittest.TestCase):
    """Test format_file_listing function"""

    def test_format_simple(self):
        """Test simple filename formatting"""
        test_file = Path("test.txt")
        result = format_file_listing(test_file)
        self.assertEqual(result, "test.txt")


class TestSafeRemoveDirectory(unittest.TestCase):
    """Test safe_remove_directory function"""

    def setUp(self):
        """Create temporary test directory"""
        self.test_dir = Path(tempfile.mkdtemp())

    def test_remove_empty_directory(self):
        """Test removing empty directory"""
        empty_dir = self.test_dir / "empty"
        empty_dir.mkdir()
        result = safe_remove_directory(empty_dir)
        self.assertTrue(result)
        self.assertFalse(empty_dir.exists())

    def test_remove_non_empty_directory_fails(self):
        """Test that removing non-empty directory without recursive fails"""
        non_empty = self.test_dir / "non_empty"
        non_empty.mkdir()
        (non_empty / "file.txt").touch()
        result = safe_remove_directory(non_empty, recursive=False)
        self.assertFalse(result)
        self.assertTrue(non_empty.exists())

    def test_remove_recursive(self):
        """Test recursive directory removal"""
        dir_with_files = self.test_dir / "with_files"
        dir_with_files.mkdir()
        (dir_with_files / "file1.txt").touch()
        (dir_with_files / "subdir").mkdir()
        (dir_with_files / "subdir" / "file2.txt").touch()

        result = safe_remove_directory(dir_with_files, recursive=True)
        self.assertTrue(result)
        self.assertFalse(dir_with_files.exists())

    def tearDown(self):
        """Clean up test directory"""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)


if __name__ == '__main__':
    unittest.main()
