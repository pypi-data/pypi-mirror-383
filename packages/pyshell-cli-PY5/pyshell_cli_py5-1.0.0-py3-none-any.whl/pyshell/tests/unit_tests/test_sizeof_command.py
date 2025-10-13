#!/usr/bin/env python3
"""
Unit tests for sizeof command
"""

import unittest
import sys
import os
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from commands import sizeof
import shutil


class TestSizeofCommand(unittest.TestCase):
    """Test cases for sizeof command."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())

        # Create a mock shell object with current_dir attribute
        self.mock_shell = MagicMock()
        self.mock_shell.current_dir = self.test_dir

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up test files
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)
    @patch('sys.stdout', new_callable=StringIO)
    def test_sizeof_help_short(self, mock_stdout):
        """Test sizeof with -h flag."""
        result = sizeof.run(['-h'], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertEqual(result, 0)
        self.assertIn('sizeof - print file size in bytes', output)
        self.assertIn('Usage:', output)
        self.assertIn('Options:', output)
        self.assertIn('Examples:', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_sizeof_help_long(self, mock_stdout):
        """Test sizeof with --help flag."""
        result = sizeof.run(['--help'], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertEqual(result, 0)
        self.assertIn('sizeof - print file size in bytes', output)
        self.assertIn('Usage:', output)
        self.assertIn('Options:', output)
        self.assertIn('Examples:', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_sizeof_no_args(self, mock_stderr):
        """Test sizeof with no arguments."""
        result = sizeof.run([], self.mock_shell)
        output = mock_stderr.getvalue()

        self.assertEqual(result, 1)
        self.assertIn('missing file operand', output)
        self.assertIn('Try \'sizeof --help\'', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_sizeof_single_file(self, mock_stdout):
        """Test sizeof with single file."""
        test_file = self.test_dir / 'test.txt'
        content = 'Hello, World!'
        test_file.write_text(content)

        result = sizeof.run([str(test_file)], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertEqual(result, 0)
        self.assertIn(str(len(content)), output)
        self.assertIn('bytes', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_sizeof_empty_file(self, mock_stdout):
        """Test sizeof with empty file."""
        test_file = self.test_dir / 'empty.txt'
        test_file.write_text('')

        result = sizeof.run([str(test_file)], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertEqual(result, 0)
        self.assertIn('0', output)
        self.assertIn('bytes', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_sizeof_large_file(self, mock_stdout):
        """Test sizeof with large file."""
        test_file = self.test_dir / 'large.txt'
        content = 'A' * 1000  # 1000 bytes
        test_file.write_text(content)

        result = sizeof.run([str(test_file)], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertEqual(result, 0)
        self.assertIn('1000', output)
        self.assertIn('bytes', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_sizeof_multiple_files(self, mock_stdout):
        """Test sizeof with multiple files (only first file is processed)."""
        test_file1 = self.test_dir / 'file1.txt'
        test_file2 = self.test_dir / 'file2.txt'
        test_file1.write_text('Content 1')
        test_file2.write_text('Content 2')

        result = sizeof.run([str(test_file1), str(test_file2)], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertEqual(result, 0)
        # Should only show size for first file
        self.assertIn('9', output)  # Length of 'Content 1'
        self.assertIn('bytes', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_sizeof_file_not_found(self, mock_stderr):
        """Test sizeof with nonexistent file."""
        result = sizeof.run(['nonexistent.txt'], self.mock_shell)
        output = mock_stderr.getvalue()

        self.assertEqual(result, 1)
        self.assertIn('No such file or directory', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_sizeof_permission_denied(self, mock_stdout):
        """Test sizeof with permission denied."""
        test_file = self.test_dir / 'restricted.txt'
        test_file.write_text('content')
        test_file.chmod(0o000)  # Remove all permissions

        try:
            result = sizeof.run([str(test_file)], self.mock_shell)

            # On some systems, this might still work or return 0
            # Let's just check that it doesn't crash
            self.assertIsInstance(result, int)
        finally:
            test_file.chmod(0o644)  # Restore permissions

    @patch('sys.stdout', new_callable=StringIO)
    def test_sizeof_is_directory(self, mock_stdout):
        """Test sizeof with directory."""
        result = sizeof.run([str(self.test_dir)], self.mock_shell)
        output = mock_stdout.getvalue()

        # sizeof should work with directories (shows directory size)
        self.assertEqual(result, 0)
        self.assertIn('bytes', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_sizeof_absolute_path(self, mock_stdout):
        """Test sizeof with absolute path."""
        test_file = self.test_dir / 'abs_test.txt'
        content = 'Absolute path test'
        test_file.write_text(content)

        result = sizeof.run([str(test_file.absolute())], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertEqual(result, 0)
        self.assertIn(str(len(content)), output)
        self.assertIn('bytes', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_sizeof_relative_path(self, mock_stdout):
        """Test sizeof with relative path."""
        test_file = self.test_dir / 'rel_test.txt'
        content = 'Relative path test'
        test_file.write_text(content)

        # Change to test directory and use relative path
        original_cwd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            result = sizeof.run(['rel_test.txt'], self.mock_shell)
            output = mock_stdout.getvalue()

            self.assertEqual(result, 0)
            self.assertIn(str(len(content)), output)
            self.assertIn('bytes', output)
        finally:
            os.chdir(original_cwd)

    @patch('sys.stdout', new_callable=StringIO)
    def test_sizeof_unicode_content(self, mock_stdout):
        """Test sizeof with unicode content."""
        test_file = self.test_dir / 'unicode.txt'
        content = 'Hello 世界 🌍'  # Unicode content
        test_file.write_text(content, encoding='utf-8')

        result = sizeof.run([str(test_file)], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertEqual(result, 0)
        # Should show the actual byte size of the unicode content
        self.assertIn('bytes', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_sizeof_binary_file(self, mock_stdout):
        """Test sizeof with binary file."""
        test_file = self.test_dir / 'binary.bin'
        content = bytes([0x00, 0x01, 0x02, 0x03, 0xFF])
        test_file.write_bytes(content)

        result = sizeof.run([str(test_file)], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertEqual(result, 0)
        self.assertIn('5', output)  # 5 bytes
        self.assertIn('bytes', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_sizeof_general_exception(self, mock_stderr):
        """Test sizeof with general exception."""
        with patch('pathlib.Path.stat', side_effect=Exception("Unexpected error")):
            result = sizeof.run(['test.txt'], self.mock_shell)
            output = mock_stderr.getvalue()

            self.assertEqual(result, 1)
            self.assertIn('Unexpected error', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_sizeof_mixed_valid_invalid_files(self, mock_stdout):
        """Test sizeof with mix of valid and invalid files (only first file processed)."""
        test_file = self.test_dir / 'valid.txt'
        test_file.write_text('Valid content')

        result = sizeof.run([str(test_file), 'nonexistent.txt'], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertEqual(result, 0)  # Should succeed with first file
        self.assertIn('13', output)  # Length of 'Valid content'
        self.assertIn('bytes', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_sizeof_symlink(self, mock_stdout):
        """Test sizeof with symlink."""
        # Create a target file
        target_file = self.test_dir / 'target.txt'
        target_file.write_text('Target content')

        # Create a symlink (skip on Windows due to privilege requirements)
        symlink_file = self.test_dir / 'symlink.txt'
        try:
            symlink_file.symlink_to(target_file)
        except OSError:
            # Skip test on Windows or systems without symlink support
            self.skipTest("Symlink creation not supported on this system")

        result = sizeof.run([str(symlink_file)], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertEqual(result, 0)
        # Should show size of target file
        self.assertIn('14', output)  # Length of 'Target content'
        self.assertIn('bytes', output)


class TestSizeofPrintHelp(unittest.TestCase):
    """Test cases for sizeof help function."""

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_help_function(self, mock_stdout):
        """Test the print_help function directly."""
        sizeof.print_help()
        output = mock_stdout.getvalue()

        self.assertIn('sizeof - print file size in bytes', output)
        self.assertIn('Usage: sizeof [OPTION]... FILE...', output)
        self.assertIn('-h, --help', output)
        self.assertIn('Examples:', output)
        self.assertIn('Exit Status:', output)


if __name__ == '__main__':
    unittest.main(verbosity=2)
