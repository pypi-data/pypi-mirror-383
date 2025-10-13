#!/usr/bin/env python3
"""
Unit tests for mkdir command
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

from commands import mkdir
import shutil


class TestMkdirCommand(unittest.TestCase):
    """Test cases for mkdir command."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())

        # Create a mock shell object with current_dir attribute
        self.mock_shell = MagicMock()
        self.mock_shell.current_dir = self.test_dir

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up any test directories
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)
    @patch('sys.stdout', new_callable=StringIO)
    def test_mkdir_help_short(self, mock_stdout):
        """Test mkdir with -h flag."""
        mkdir.run(['-h'], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertIn('mkdir - make directories', output)
        self.assertIn('Usage:', output)
        self.assertIn('Options:', output)
        self.assertIn('Examples:', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_mkdir_help_long(self, mock_stdout):
        """Test mkdir with --help flag."""
        mkdir.run(['--help'], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertIn('mkdir - make directories', output)
        self.assertIn('Usage:', output)
        self.assertIn('Options:', output)
        self.assertIn('Examples:', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_mkdir_no_args(self, mock_stderr):
        """Test mkdir with no arguments."""
        mkdir.run([], self.mock_shell)
        output = mock_stderr.getvalue()

        self.assertIn('missing operand', output)
        self.assertIn('Try \'mkdir --help\'', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_mkdir_single_directory(self, _mock_stdout):
        """Test mkdir with single directory."""
        test_path = self.test_dir / 'newdir'

        mkdir.run(['newdir'], self.mock_shell)

        self.assertTrue(test_path.exists())
        self.assertTrue(test_path.is_dir())

    @patch('sys.stdout', new_callable=StringIO)
    def test_mkdir_multiple_directories(self, _mock_stdout):
        """Test mkdir with multiple directories."""
        dir1 = self.test_dir / 'dir1'
        dir2 = self.test_dir / 'dir2'
        dir3 = self.test_dir / 'dir3'

        mkdir.run(['dir1', 'dir2', 'dir3'], self.mock_shell)

        self.assertTrue(dir1.exists())
        self.assertTrue(dir2.exists())
        self.assertTrue(dir3.exists())

    @patch('sys.stdout', new_callable=StringIO)
    def test_mkdir_absolute_path(self, _mock_stdout):
        """Test mkdir with absolute path."""
        test_path = Path(tempfile.mkdtemp())

        try:
            mkdir.run([str(test_path)], self.mock_shell)
            self.assertTrue(test_path.exists())
        finally:
            if test_path.exists():
                test_path.rmdir()
    @patch('sys.stderr', new_callable=StringIO)
    def test_mkdir_existing_directory(self, mock_stderr):
        """Test mkdir with existing directory."""
        existing_dir = self.test_dir / 'existing'
        existing_dir.mkdir()

        mkdir.run(['existing'], self.mock_shell)
        output = mock_stderr.getvalue()

        self.assertIn('Directory already exists', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_mkdir_invalid_name_dot(self, mock_stderr):
        """Test mkdir with invalid name '.'."""
        mkdir.run(['.'], self.mock_shell)
        output = mock_stderr.getvalue()

        self.assertIn('Cannot create directory', output)
        self.assertIn("'.'", output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_mkdir_invalid_name_dotdot(self, mock_stderr):
        """Test mkdir with invalid name '..'."""
        mkdir.run(['..'], self.mock_shell)
        output = mock_stderr.getvalue()

        self.assertIn('Cannot create directory', output)
        self.assertIn("'..'", output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_mkdir_invalid_name_empty(self, mock_stderr):
        """Test mkdir with empty name."""
        mkdir.run([''], self.mock_shell)
        output = mock_stderr.getvalue()

        self.assertIn('Directory name cannot be empty', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_mkdir_invalid_name_null_bytes(self, mock_stderr):
        """Test mkdir with null bytes in name."""
        mkdir.run(['test\x00dir'], self.mock_shell)
        output = mock_stderr.getvalue()

        self.assertIn('null bytes', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_mkdir_invalid_name_separators_only(self, mock_stderr):
        """Test mkdir with separators only."""
        mkdir.run(['///'], self.mock_shell)
        output = mock_stderr.getvalue()

        self.assertIn('separators', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_mkdir_permission_denied(self, mock_stderr):
        """Test mkdir with permission denied."""
        # Mock Path.mkdir to raise PermissionError
        with patch('pathlib.Path.mkdir', side_effect=PermissionError("Permission denied")):
            mkdir.run(['testdir'], self.mock_shell)
            output = mock_stderr.getvalue()

            self.assertIn('Permission denied', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_mkdir_path_too_long(self, mock_stderr):
        """Test mkdir with path too long."""
        # Create a very long directory name
        long_name = 'a' * 5000
        mkdir.run([long_name], self.mock_shell)
        output = mock_stderr.getvalue()

        # Accept both platform-specific error messages
        self.assertTrue(
            'Path too long' in output or 'File name too long' in output,
            f"Expected path/filename too long error, got: {output}"
        )

    @patch('sys.stderr', new_callable=StringIO)
    def test_mkdir_resolve_error(self, mock_stderr):
        """Test mkdir with resolve error."""
        # Mock Path.resolve to raise an error
        with patch('pathlib.Path.resolve', side_effect=OSError("Invalid path")):
            mkdir.run(['testdir'], self.mock_shell)
            output = mock_stderr.getvalue()

            self.assertIn('Invalid path', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_mkdir_os_error_file_name_too_long(self, mock_stderr):
        """Test mkdir with OSError file name too long."""
        with patch('pathlib.Path.mkdir', side_effect=OSError(36, "File name too long")):
            mkdir.run(['testdir'], self.mock_shell)
            output = mock_stderr.getvalue()

            # Accept both platform-specific error messages
            self.assertTrue(
                'Path too long' in output or 'File name too long' in output,
                f"Expected path/filename too long error, got: {output}"
            )

    @patch('sys.stderr', new_callable=StringIO)
    def test_mkdir_os_error_no_space(self, mock_stderr):
        """Test mkdir with OSError no space left."""
        with patch('pathlib.Path.mkdir', side_effect=OSError(28, "No space left on device")):
            mkdir.run(['testdir'], self.mock_shell)
            output = mock_stderr.getvalue()

            self.assertIn('No space left on device', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_mkdir_general_exception(self, mock_stderr):
        """Test mkdir with general exception."""
        with patch('pathlib.Path.mkdir', side_effect=Exception("Unexpected error")):
            mkdir.run(['testdir'], self.mock_shell)
            output = mock_stderr.getvalue()

            self.assertIn('Unexpected error', output)


class TestMkdirValidation(unittest.TestCase):
    """Test cases for mkdir validation functions."""

    def test_is_valid_directory_name_valid(self):
        """Test valid directory names."""
        valid_names = ['test', 'test123', 'test_dir', 'test-dir', 'test.dir']

        for name in valid_names:
            is_valid, error_msg = mkdir.is_valid_directory_name(name)
            self.assertTrue(is_valid)
            self.assertIsNone(error_msg)
    def test_is_valid_directory_name_empty(self):
        """Test empty directory name."""
        is_valid, error_msg = mkdir.is_valid_directory_name('')
        self.assertFalse(is_valid)
        self.assertIn('empty', error_msg)
    def test_is_valid_directory_name_whitespace_only(self):
        """Test whitespace-only directory name."""
        is_valid, error_msg = mkdir.is_valid_directory_name('   ')
        self.assertFalse(is_valid)
        self.assertIn('empty', error_msg)
    def test_is_valid_directory_name_dot(self):
        """Test directory name '.'."""
        is_valid, error_msg = mkdir.is_valid_directory_name('.')
        self.assertFalse(is_valid)
        self.assertIn("'.' or '..'", error_msg)
    def test_is_valid_directory_name_dotdot(self):
        """Test directory name '..'."""
        is_valid, error_msg = mkdir.is_valid_directory_name('..')
        self.assertFalse(is_valid)
        self.assertIn("'.' or '..'", error_msg)
    def test_is_valid_directory_name_null_bytes(self):
        """Test directory name with null bytes."""
        is_valid, error_msg = mkdir.is_valid_directory_name('test\x00dir')
        self.assertFalse(is_valid)
        self.assertIn('null bytes', error_msg)
    def test_is_valid_directory_name_separators_only(self):
        """Test directory name with separators only."""
        is_valid, error_msg = mkdir.is_valid_directory_name('///')
        self.assertFalse(is_valid)
        self.assertIn('separators', error_msg)
    def test_is_valid_directory_name_mixed_separators(self):
        """Test directory name with mixed separators."""
        is_valid, error_msg = mkdir.is_valid_directory_name('\\/\\/')
        self.assertFalse(is_valid)
        self.assertIn('separators', error_msg)


class TestMkdirPrintHelp(unittest.TestCase):
    """Test cases for mkdir help function."""
    @patch('sys.stdout', new_callable=StringIO)
    def test_print_help_function(self, mock_stdout):
        """Test the print_help function directly."""
        mkdir.print_help()
        output = mock_stdout.getvalue()
        self.assertIn('mkdir - make directories', output)
        self.assertIn('Usage: mkdir [OPTION]... DIRECTORY...', output)
        self.assertIn('-h, --help', output)
        self.assertIn('Examples:', output)
        self.assertIn('Exit Status:', output)


if __name__ == '__main__':
    unittest.main(verbosity=2)
