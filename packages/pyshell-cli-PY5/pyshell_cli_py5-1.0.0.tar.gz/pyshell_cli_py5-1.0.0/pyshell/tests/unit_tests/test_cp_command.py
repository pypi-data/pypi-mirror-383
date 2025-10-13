#!/usr/bin/env python3
"""
Simple unit tests for cp command
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

from commands import cp


class TestCpCommand(unittest.TestCase):
    """Test cases for cp command plugin."""

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
    def test_cp_help(self, mock_stdout):
        """Test cp help flag."""
        cp.run(['-h'], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertIn('cp - copy files and directories', output)
        self.assertIn('-r, --recursive', output)
        self.assertIn('-i, --interactive', output)
        self.assertIn('-u, --update', output)
        self.assertIn('-v, --verbose', output)

    def test_cp_basic_file_copy(self):
        """Test basic file copy."""
        test_file = self.test_dir / "source.txt"
        test_file.write_text("Hello World!\nLine 2\n")

        cp.run(['source.txt', 'dest.txt'], self.mock_shell)

        dest_file = self.test_dir / "dest.txt"
        self.assertTrue(dest_file.exists())
        self.assertEqual(test_file.read_text(), dest_file.read_text())

    def test_cp_verbose_copy(self):
        """Test verbose copy."""
        test_file = self.test_dir / "source.txt"
        test_file.write_text("Test content\n")

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cp.run(['-v', 'source.txt', 'verbose.txt'], self.mock_shell)
            output = mock_stdout.getvalue()

            # Check for source and destination in verbose output
            self.assertIn("source.txt", output)
            self.assertIn("verbose.txt", output)

        verbose_file = self.test_dir / "verbose.txt"
        self.assertTrue(verbose_file.exists())

    def test_cp_multiple_files(self):
        """Test copying multiple files to directory."""
        file1 = self.test_dir / "file1.txt"
        file2 = self.test_dir / "file2.txt"
        file1.write_text("File 1 content\n")
        file2.write_text("File 2 content\n")

        cp.run(['file1.txt', 'file2.txt', 'backup_dir'], self.mock_shell)

        backup_dir = self.test_dir / "backup_dir"
        self.assertTrue(backup_dir.exists())
        self.assertTrue(backup_dir.is_dir())

        # Check files were copied
        self.assertTrue((backup_dir / "file1.txt").exists())
        self.assertTrue((backup_dir / "file2.txt").exists())

    def test_cp_recursive_directory(self):
        """Test recursive directory copy."""
        source_dir = self.test_dir / "source_dir"
        source_dir.mkdir()
        (source_dir / "file1.txt").write_text("File 1\n")
        (source_dir / "file2.txt").write_text("File 2\n")

        cp.run(['-r', 'source_dir', 'dest_dir'], self.mock_shell)

        dest_dir = self.test_dir / "dest_dir"
        self.assertTrue(dest_dir.exists())
        self.assertTrue((dest_dir / "file1.txt").exists())
        self.assertTrue((dest_dir / "file2.txt").exists())

    def test_cp_recursive_verbose(self):
        """Test recursive copy with verbose output."""
        source_dir = self.test_dir / "source_dir"
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("Content\n")

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cp.run(['-r', '-v', 'source_dir', 'dest_dir'], self.mock_shell)
            output = mock_stdout.getvalue()

            # Check for source and destination in verbose output
            self.assertIn("source_dir", output)
            self.assertIn("dest_dir", output)
            self.assertIn("file.txt", output)

    def test_cp_interactive_decline(self):
        """Test interactive mode - user declines."""
        test_file = self.test_dir / "source.txt"
        test_file.write_text("Source content\n")

        # Create existing file
        existing_file = self.test_dir / "existing.txt"
        existing_file.write_text("Existing content\n")

        with patch('builtins.input', return_value='n'):
            cp.run(['-i', 'source.txt', 'existing.txt'], self.mock_shell)

        # File should not be overwritten
        self.assertEqual(existing_file.read_text(), "Existing content\n")

    def test_cp_interactive_accept(self):
        """Test interactive mode - user accepts."""
        test_file = self.test_dir / "source.txt"
        test_file.write_text("New content\n")

        # Create existing file
        existing_file = self.test_dir / "existing.txt"
        existing_file.write_text("Old content\n")

        with patch('builtins.input', return_value='y'):
            cp.run(['-i', 'source.txt', 'existing.txt'], self.mock_shell)

        # File should be overwritten
        self.assertEqual(existing_file.read_text(), "New content\n")

    def test_cp_update_newer(self):
        """Test update mode - source is newer."""
        test_file = self.test_dir / "source.txt"
        test_file.write_text("New content\n")

        # Create older file
        old_file = self.test_dir / "old.txt"
        old_file.write_text("Old content\n")

        # Make source file newer
        import time
        time.sleep(0.1)
        test_file.touch()

        cp.run(['-u', 'source.txt', 'old.txt'], self.mock_shell)

        # File should be updated
        self.assertEqual(old_file.read_text(), "New content\n")

    def test_cp_update_older(self):
        """Test update mode - source is older."""
        test_file = self.test_dir / "source.txt"
        test_file.write_text("Old content\n")

        # Create newer file
        new_file = self.test_dir / "new.txt"
        new_file.write_text("New content\n")

        # Make destination file newer
        import time
        time.sleep(0.1)
        new_file.touch()

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cp.run(['-u', '-v', 'source.txt', 'new.txt'], self.mock_shell)
            output = mock_stdout.getvalue()

            self.assertIn("(not newer, skipped)", output)

        # File should not be updated
        self.assertEqual(new_file.read_text(), "New content\n")

    def test_cp_nonexistent_source(self):
        """Test copying nonexistent source file."""
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            cp.run(['nonexistent.txt', 'dest.txt'], self.mock_shell)
            output = mock_stderr.getvalue()

            self.assertIn("No such file or directory", output)

    def test_cp_directory_without_recursive(self):
        """Test copying directory without -r flag."""
        source_dir = self.test_dir / "source_dir"
        source_dir.mkdir()

        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            cp.run(['source_dir', 'dest.txt'], self.mock_shell)
            output = mock_stderr.getvalue()

            self.assertIn("omitting directory", output)
            self.assertIn("use -r to copy directories", output)

    def test_cp_missing_operands(self):
        """Test cp with missing operands."""
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            cp.run([], self.mock_shell)
            output = mock_stderr.getvalue()

            self.assertIn("missing file operand", output)

    def test_cp_invalid_flag(self):
        """Test cp with invalid flag."""
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            result = cp.run(['--invalid', 'source.txt', 'dest.txt'], self.mock_shell)
            output = mock_stderr.getvalue()

            self.assertEqual(result, 1)
            self.assertIn("Invalid option -- 'invalid'", output)

    def test_cp_combined_flags(self):
        """Test cp with combined flags."""
        test_file = self.test_dir / "source.txt"
        test_file.write_text("Test content\n")

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cp.run(['-r', '-v', 'source.txt', 'dest.txt'], self.mock_shell)
            output = mock_stdout.getvalue()

            # Check for source and destination in verbose output
            self.assertIn("source.txt", output)
            self.assertIn("dest.txt", output)

        dest_file = self.test_dir / "dest.txt"
        self.assertTrue(dest_file.exists())


class TestCpHelperFunctions(unittest.TestCase):
    """Test cases for cp helper functions."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_copy_file_basic(self):
        """Test copy_file function."""
        source_file = self.test_dir / "source.txt"
        source_file.write_text("Test content\n")
        dest_file = self.test_dir / "dest.txt"

        cp.copy_file(source_file, dest_file)

        self.assertTrue(dest_file.exists())
        self.assertEqual(source_file.read_text(), dest_file.read_text())

    def test_copy_file_verbose(self):
        """Test copy_file function with verbose output."""
        source_file = self.test_dir / "source.txt"
        source_file.write_text("Test content\n")
        dest_file = self.test_dir / "dest.txt"

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cp.copy_file(source_file, dest_file, verbose=True)
            output = mock_stdout.getvalue()

            # Check for source and destination in verbose output
            self.assertIn("source.txt", output)
            self.assertIn("dest.txt", output)

    def test_copy_directory_basic(self):
        """Test copy_directory function."""
        source_dir = self.test_dir / "source_dir"
        source_dir.mkdir()
        (source_dir / "file1.txt").write_text("File 1\n")
        (source_dir / "file2.txt").write_text("File 2\n")

        dest_dir = self.test_dir / "dest_dir"

        cp.copy_directory(source_dir, dest_dir, self.test_dir, recursive=True)

        self.assertTrue(dest_dir.exists())
        self.assertTrue((dest_dir / "file1.txt").exists())
        self.assertTrue((dest_dir / "file2.txt").exists())

    def test_copy_directory_verbose(self):
        """Test copy_directory function with verbose output."""
        source_dir = self.test_dir / "source_dir"
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("Content\n")

        dest_dir = self.test_dir / "dest_dir"

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cp.copy_directory(source_dir, dest_dir, self.test_dir, recursive=True, verbose=True)
            output = mock_stdout.getvalue()

            # Check for source and destination in verbose output
            self.assertIn("source_dir", output)
            self.assertIn("dest_dir", output)
            self.assertIn("file.txt", output)

    def test_copy_item_file(self):
        """Test copy_item function with file."""
        source_file = self.test_dir / "source.txt"
        source_file.write_text("Test content\n")
        dest_path = self.test_dir / "dest.txt"

        cp.copy_item(source_file, dest_path, self.test_dir)

        self.assertTrue(dest_path.exists())
        self.assertEqual(source_file.read_text(), dest_path.read_text())

    def test_copy_item_directory(self):
        """Test copy_item function with directory."""
        source_dir = self.test_dir / "source_dir"
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("Content\n")

        dest_path = self.test_dir / "dest_dir"

        cp.copy_item(source_dir, dest_path, self.test_dir, recursive=True)

        self.assertTrue(dest_path.exists())
        self.assertTrue((dest_path / "file.txt").exists())

    def test_copy_item_nonexistent(self):
        """Test copy_item function with nonexistent source."""
        nonexistent = self.test_dir / "nonexistent.txt"
        dest_path = self.test_dir / "dest.txt"

        with self.assertRaises(FileNotFoundError):
            cp.copy_item(nonexistent, dest_path, self.test_dir)


if __name__ == '__main__':
    unittest.main(verbosity=2)

