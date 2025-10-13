#!/usr/bin/env python3
"""
Unit tests for tail command
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

from commands import tail
import shutil


class TestTailCommand(unittest.TestCase):
    """Test cases for tail command."""

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
    def test_tail_help_short(self, mock_stdout):
        """Test tail with -h flag."""
        result = tail.run(['-h'], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertEqual(result, 0)
        self.assertIn('tail - output the last part of files', output)
        self.assertIn('Usage:', output)
        self.assertIn('Options:', output)
        self.assertIn('Examples:', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_tail_help_long(self, mock_stdout):
        """Test tail with --help flag."""
        result = tail.run(['--help'], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertEqual(result, 0)
        self.assertIn('tail - output the last part of files', output)
        self.assertIn('Usage:', output)
        self.assertIn('Options:', output)
        self.assertIn('Examples:', output)

    @patch('sys.stdin', new_callable=StringIO)
    def test_tail_no_args(self, mock_stdin):
        """Test tail with no arguments (reads from stdin)."""
        # When no file is provided, tail reads from stdin
        mock_stdin.write("Line 1\nLine 2\n")
        mock_stdin.seek(0)
        result = tail.run([], self.mock_shell)
        # Should succeed (exit code 0)
        self.assertEqual(result, 0)

    @patch('sys.stdout', new_callable=StringIO)
    def test_tail_default_lines(self, mock_stdout):
        """Test tail with default number of lines (10)."""
        test_file = self.test_dir / 'test.txt'
        test_file.write_text('\n'.join([f'Line {i}' for i in range(1, 16)]))

        result = tail.run([str(test_file)], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertEqual(result, 0)
        self.assertIn('Line 6', output)  # Last 10 lines from 16 total
        self.assertIn('Line 15', output)
        self.assertNotIn('Line 5', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_tail_n_flag(self, mock_stdout):
        """Test tail with -n flag."""
        test_file = self.test_dir / 'test.txt'
        test_file.write_text('\n'.join([f'Line {i}' for i in range(1, 16)]))

        result = tail.run(['-n', '5', str(test_file)], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertEqual(result, 0)
        self.assertIn('Line 11', output)
        self.assertIn('Line 15', output)
        self.assertNotIn('Line 10', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_tail_shortcut_flag(self, mock_stdout):
        """Test tail with shortcut flag (e.g., -3)."""
        test_file = self.test_dir / 'test.txt'
        test_file.write_text('\n'.join([f'Line {i}' for i in range(1, 16)]))

        result = tail.run(['-3', str(test_file)], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertEqual(result, 0)
        self.assertIn('Line 13', output)
        self.assertIn('Line 15', output)
        self.assertNotIn('Line 12', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_tail_multiple_files(self, mock_stdout):
        """Test tail with multiple files."""
        test_file1 = self.test_dir / 'test1.txt'
        test_file2 = self.test_dir / 'test2.txt'
        test_file1.write_text('File 1 Line 1\nFile 1 Line 2\nFile 1 Line 3')
        test_file2.write_text('File 2 Line 1\nFile 2 Line 2\nFile 2 Line 3')

        result = tail.run(['-2', str(test_file1), str(test_file2)], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertEqual(result, 0)
        self.assertIn('==>', output)
        self.assertIn('test1.txt', output)
        self.assertIn('test2.txt', output)
        self.assertIn('File 1 Line 2', output)
        self.assertIn('File 2 Line 2', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_tail_file_not_found(self, mock_stderr):
        """Test tail with nonexistent file."""
        result = tail.run(['nonexistent.txt'], self.mock_shell)
        output = mock_stderr.getvalue()

        self.assertEqual(result, 1)
        self.assertIn('No such file or directory', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_tail_permission_denied(self, mock_stderr):
        """Test tail with permission denied."""
        test_file = self.test_dir / 'restricted.txt'
        test_file.write_text('content')

        # On Windows, chmod might not work as expected, so we'll mock the open function
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            result = tail.run([str(test_file)], self.mock_shell)
            output = mock_stderr.getvalue()

            self.assertEqual(result, 1)
            self.assertIn('Permission denied', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_tail_is_directory(self, mock_stderr):
        """Test tail with directory."""
        result = tail.run([str(self.test_dir)], self.mock_shell)
        output = mock_stderr.getvalue()

        self.assertEqual(result, 1)
        # On Windows, trying to open a directory as a file results in PermissionError
        self.assertTrue('Is a directory' in output or 'Permission denied' in output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_tail_n_flag_missing_argument(self, mock_stderr):
        """Test tail with -n flag missing argument."""
        result = tail.run(['-n'], self.mock_shell)
        output = mock_stderr.getvalue()

        self.assertEqual(result, 1)
        self.assertIn('option requires an argument', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_tail_n_flag_invalid_number(self, mock_stderr):
        """Test tail with -n flag invalid number."""
        test_file = self.test_dir / 'test.txt'
        test_file.write_text('content')

        result = tail.run(['-n', 'invalid', str(test_file)], self.mock_shell)
        output = mock_stderr.getvalue()

        self.assertEqual(result, 1)
        self.assertIn('invalid number of lines', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_tail_empty_file(self, mock_stdout):
        """Test tail with empty file."""
        test_file = self.test_dir / 'empty.txt'
        test_file.write_text('')

        result = tail.run([str(test_file)], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertEqual(result, 0)
        self.assertEqual(output, '')

    @patch('sys.stdout', new_callable=StringIO)
    def test_tail_fewer_lines_than_requested(self, mock_stdout):
        """Test tail with file having fewer lines than requested."""
        test_file = self.test_dir / 'short.txt'
        test_file.write_text('Line 1\nLine 2')

        result = tail.run(['-10', str(test_file)], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertEqual(result, 0)
        self.assertIn('Line 1', output)
        self.assertIn('Line 2', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_tail_zero_lines(self, mock_stdout):
        """Test tail with 0 lines."""
        test_file = self.test_dir / 'test.txt'
        test_file.write_text('\n'.join([f'Line {i}' for i in range(1, 6)]))

        result = tail.run(['-0', str(test_file)], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertEqual(result, 0)
        self.assertEqual(output, '')

    @patch('sys.stdout', new_callable=StringIO)
    def test_tail_negative_lines(self, mock_stdout):
        """Test tail with negative number of lines (behavior varies)."""
        test_file = self.test_dir / 'test.txt'
        test_file.write_text('\n'.join([f'Line {i}' for i in range(1, 6)]))

        result = tail.run(['-n', '-5', str(test_file)], self.mock_shell)

        # Negative numbers behavior may vary, just ensure it doesn't crash
        self.assertIsInstance(result, int)

    @patch('sys.stderr', new_callable=StringIO)
    def test_tail_general_exception(self, mock_stderr):
        """Test tail with general exception."""
        with patch('builtins.open', side_effect=Exception("Unexpected error")):
            result = tail.run(['test.txt'], self.mock_shell)
            output = mock_stderr.getvalue()

            self.assertEqual(result, 1)
            self.assertIn('Unexpected error', output)

    def test_tail_mixed_valid_invalid_files(self):
        """Test tail with mix of valid and invalid files."""
        test_file = self.test_dir / 'valid.txt'
        test_file.write_text('Valid content')

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout, \
             patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            result = tail.run([str(test_file), 'nonexistent.txt'], self.mock_shell)
            stdout_output = mock_stdout.getvalue()
            stderr_output = mock_stderr.getvalue()

            self.assertEqual(result, 1)  # Should return error due to invalid file
            self.assertIn('Valid content', stdout_output)
            self.assertIn('No such file or directory', stderr_output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_tail_single_line_file(self, mock_stdout):
        """Test tail with single line file."""
        test_file = self.test_dir / 'single.txt'
        test_file.write_text('Single line')

        result = tail.run(['-5', str(test_file)], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertEqual(result, 0)
        self.assertIn('Single line', output)


class TestTailPrintHelp(unittest.TestCase):
    """Test cases for tail help function."""

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_help_function(self, mock_stdout):
        """Test the print_help function directly."""
        tail.print_help()
        output = mock_stdout.getvalue()

        self.assertIn('tail - output the last part of files', output)
        self.assertIn('Usage: tail [OPTION]... [FILE]...', output)
        self.assertIn('-n, --lines=NUMBER', output)
        self.assertIn('-NUMBER', output)
        self.assertIn('-h, --help', output)
        self.assertIn('Examples:', output)
        self.assertIn('Exit Status:', output)


if __name__ == '__main__':
    unittest.main(verbosity=2)
