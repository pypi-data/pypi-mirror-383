#!/usr/bin/env python3
"""
Unit tests for rm command
"""

import unittest
import sys
import os
from io import StringIO
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from commands import rm


class TestRmCommand(unittest.TestCase):
    """Test cases for rm command plugin."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.current_dir = self.test_dir
        # Create a mock shell object with current_dir attribute
        self.mock_shell = MagicMock()
        self.mock_shell.current_dir = self.test_dir

    def tearDown(self):
        """Clean up test fixtures."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    @patch('sys.stdout', new_callable=StringIO)
    def test_rm_help(self, mock_stdout):
        """Test rm help flag."""
        rm.run(['-h'], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertIn('rm - remove files or directories', output)
        self.assertIn('-r', output)
        self.assertIn('-v, --verbose', output)
        self.assertIn('-i, --interactive', output)
        self.assertIn('-f, --force', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_rm_no_args(self, mock_stderr):
        """Test rm with no arguments."""
        rm.run([], self.mock_shell)
        output = mock_stderr.getvalue()

        self.assertIn('missing operand', output)

    def test_rm_single_file(self):
        """Test removing a single file."""
        test_file = self.test_dir / "test.txt"
        test_file.write_text("content")

        self.assertTrue(test_file.exists())
        rm.run(['test.txt'], self.mock_shell)
        self.assertFalse(test_file.exists())

    def test_rm_multiple_files(self):
        """Test removing multiple files."""
        file1 = self.test_dir / "file1.txt"
        file2 = self.test_dir / "file2.txt"
        file1.write_text("content1")
        file2.write_text("content2")

        rm.run(['file1.txt', 'file2.txt'], self.mock_shell)

        self.assertFalse(file1.exists())
        self.assertFalse(file2.exists())

    @patch('sys.stderr', new_callable=StringIO)
    def test_rm_nonexistent_file(self, mock_stderr):
        """Test removing a non-existent file."""
        rm.run(['nonexistent.txt'], self.mock_shell)
        output = mock_stderr.getvalue()

        self.assertIn('cannot remove', output)
        self.assertIn('No such file or directory', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_rm_directory_without_recursive(self, mock_stderr):
        """Test removing a directory without -r flag."""
        test_dir = self.test_dir / "testdir"
        test_dir.mkdir()

        rm.run(['testdir'], self.mock_shell)
        output = mock_stderr.getvalue()

        self.assertIn('Is a directory', output)
        self.assertTrue(test_dir.exists())  # Should still exist

    def test_rm_directory_with_recursive(self):
        """Test removing a directory with -r flag."""
        test_dir = self.test_dir / "testdir"
        test_dir.mkdir()
        (test_dir / "file.txt").write_text("content")

        rm.run(['-r', 'testdir'], self.mock_shell)
        self.assertFalse(test_dir.exists())

    @patch('sys.stdout', new_callable=StringIO)
    def test_rm_verbose(self, mock_stdout):
        """Test rm with verbose flag."""
        test_file = self.test_dir / "test.txt"
        test_file.write_text("content")

        rm.run(['-v', 'test.txt'], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertIn('removed', output)
        self.assertFalse(test_file.exists())

    def test_rm_force_nonexistent(self):
        """Test rm with force flag on nonexistent file."""
        # Should not raise an error
        rm.run(['-f', 'nonexistent.txt'], self.mock_shell)

    def test_rm_force_existing(self):
        """Test rm with force flag on existing file."""
        test_file = self.test_dir / "test.txt"
        test_file.write_text("content")

        rm.run(['-f', 'test.txt'], self.mock_shell)
        self.assertFalse(test_file.exists())

    def test_rm_interactive_decline(self):
        """Test rm with interactive flag - user declines."""
        test_file = self.test_dir / "test.txt"
        test_file.write_text("content")

        with patch('builtins.input', return_value='n'):
            rm.run(['-i', 'test.txt'], self.mock_shell)

        self.assertTrue(test_file.exists())  # File should still exist

    def test_rm_interactive_accept(self):
        """Test rm with interactive flag - user accepts."""
        test_file = self.test_dir / "test.txt"
        test_file.write_text("content")

        with patch('builtins.input', return_value='y'):
            rm.run(['-i', 'test.txt'], self.mock_shell)

        self.assertFalse(test_file.exists())  # File should be removed

    def test_rm_combined_flags(self):
        """Test rm with combined flags."""
        test_dir = self.test_dir / "testdir"
        test_dir.mkdir()
        (test_dir / "file.txt").write_text("content")

        rm.run(['-r', '-v', '-f', 'testdir'], self.mock_shell)
        self.assertFalse(test_dir.exists())


class TestRmHelperFunctions(unittest.TestCase):
    """Test cases for rm helper functions."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_remove_item_file(self):
        """Test remove_item function with file."""
        test_file = self.test_dir / "test.txt"
        test_file.write_text("content")

        rm.remove_item(test_file, recursive=False, verbose=False)
        self.assertFalse(test_file.exists())

    def test_remove_item_directory_not_recursive(self):
        """Test remove_item raises error for directory without recursive."""
        test_dir = self.test_dir / "testdir"
        test_dir.mkdir()

        with self.assertRaises(IsADirectoryError):
            rm.remove_item(test_dir, recursive=False, verbose=False)

    def test_remove_item_nonexistent(self):
        """Test remove_item raises error for non-existent path."""
        nonexistent = self.test_dir / "nonexistent.txt"

        with self.assertRaises(FileNotFoundError):
            rm.remove_item(nonexistent, recursive=False, verbose=False)


if __name__ == '__main__':
    unittest.main(verbosity=2)

