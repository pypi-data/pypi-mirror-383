#!/usr/bin/env python3
"""
Simple unit tests for cat command
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

from commands import cat


class TestCatCommand(unittest.TestCase):
    """Test cases for cat command plugin."""

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
    def test_cat_help(self, mock_stdout):
        """Test cat help flag."""
        cat.run(['-h'], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertIn('cat - concatenate and display file contents', output)
        self.assertIn('-n, --number', output)
        self.assertIn('-b, --number-nonblank', output)
        self.assertIn('-s, --squeeze-blank', output)
        self.assertIn('cat file.txt > output.txt', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_cat_basic(self, mock_stdout):
        """Test basic cat functionality."""
        test_file = self.test_dir / "test.txt"
        test_file.write_text("Line 1\nLine 2\nLine 3\n")

        cat.run(['test.txt'], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertIn('Line 1', output)
        self.assertIn('Line 2', output)
        self.assertIn('Line 3', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_cat_number_lines(self, mock_stdout):
        """Test cat with line numbers."""
        test_file = self.test_dir / "test.txt"
        test_file.write_text("Line 1\nLine 2\n")

        cat.run(['-n', 'test.txt'], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertIn('1\tLine 1', output)
        self.assertIn('2\tLine 2', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_cat_number_nonblank(self, mock_stdout):
        """Test cat with non-blank line numbers."""
        test_file = self.test_dir / "test.txt"
        test_file.write_text("Line 1\n\nLine 3\n")

        cat.run(['-b', 'test.txt'], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertIn('1\tLine 1', output)
        self.assertIn('2\tLine 3', output)
        # Should not number the blank line
        self.assertNotIn('2\t\n', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_cat_squeeze_blank(self, mock_stdout):
        """Test cat with squeezed blank lines."""
        test_file = self.test_dir / "test.txt"
        test_file.write_text("Line 1\n\n\nLine 4\n")

        cat.run(['-s', 'test.txt'], self.mock_shell)
        output = mock_stdout.getvalue()

        # Should have only one blank line between Line 1 and Line 4
        lines = output.strip().split('\n')
        self.assertEqual(len(lines), 3)  # Line 1, blank line, Line 4

    @patch('sys.stdout', new_callable=StringIO)
    def test_cat_multiple_files(self, mock_stdout):
        """Test cat with multiple files."""
        file1 = self.test_dir / "file1.txt"
        file2 = self.test_dir / "file2.txt"
        file1.write_text("File 1\n")
        file2.write_text("File 2\n")

        cat.run(['file1.txt', 'file2.txt'], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertIn('File 1', output)
        self.assertIn('File 2', output)

    def test_cat_nonexistent_file(self):
        """Test cat with nonexistent file."""
        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            cat.run(['nonexistent.txt'], self.mock_shell)
            output = mock_stderr.getvalue()

            self.assertIn('No such file or directory', output)

    def test_cat_directory(self):
        """Test cat with directory."""
        test_dir = self.test_dir / "testdir"
        test_dir.mkdir()

        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            cat.run(['testdir'], self.mock_shell)
            output = mock_stderr.getvalue()

            self.assertIn('Is a directory', output)

    def test_cat_combined_flags(self):
        """Test cat with combined flags."""
        test_file = self.test_dir / "test.txt"
        test_file.write_text("Line 1\n\nLine 3\n")

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cat.run(['-n', '-s', 'test.txt'], self.mock_shell)
            output = mock_stdout.getvalue()

            self.assertIn('1\tLine 1', output)
            self.assertIn('3\tLine 3', output)  # Line 3 is numbered as 3 because blank line is also numbered

    def test_cat_invalid_flag(self):
        """Test cat with invalid flag."""
        test_file = self.test_dir / "test.txt"
        test_file.write_text("content")

        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            result = cat.run(['--invalid', 'test.txt'], self.mock_shell)
            output = mock_stderr.getvalue()

            self.assertEqual(result, 1)
            self.assertIn("Invalid option -- 'invalid'", output)

    def test_cat_with_dash_argument(self):
        """Test cat treats '>' as a filename when passed directly.

        Note: The shell's parser handles redirection syntax errors.
        When '>' is passed as an argument to cat, it's treated as a filename.
        """
        test_file = self.test_dir / "input.txt"
        test_file.write_text("Line 1\n")

        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            # Cat tries to read '>' as a file, which doesn't exist
            result = cat.run(['input.txt', '>'], self.mock_shell)
            output = mock_stderr.getvalue()

            self.assertEqual(result, 1)
            self.assertIn("No such file or directory", output)

    def test_cat_with_append_operator_as_filename(self):
        """Test cat treats '>>' as a filename when passed directly.

        Note: The shell's parser handles redirection syntax errors.
        When '>>' is passed as an argument to cat, it's treated as a filename.
        """
        test_file = self.test_dir / "input.txt"
        test_file.write_text("Line 1\n")

        with patch('sys.stderr', new_callable=StringIO) as mock_stderr:
            # Cat tries to read '>>' as a file, which doesn't exist
            result = cat.run(['input.txt', '>>'], self.mock_shell)
            output = mock_stderr.getvalue()

            self.assertEqual(result, 1)
            self.assertIn("No such file or directory", output)

    @patch('sys.stdin', new_callable=StringIO)
    def test_cat_stdin(self, mock_stdin):
        """Test cat reading from stdin."""
        mock_stdin.write("stdin content\n")
        mock_stdin.seek(0)

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cat.run(['-'], self.mock_shell)
            output = mock_stdout.getvalue()

            self.assertIn('stdin content', output)


class TestCatHelperFunctions(unittest.TestCase):
    """Test cases for cat helper functions."""

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_read_file_lines(self):
        """Test read_file_lines function."""
        test_file = self.test_dir / "test.txt"
        test_file.write_text("Line 1\nLine 2\n")

        lines = cat.read_file_lines(test_file)
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0], "Line 1\n")
        self.assertEqual(lines[1], "Line 2\n")

    def test_read_file_lines_nonexistent(self):
        """Test read_file_lines with nonexistent file."""
        nonexistent = self.test_dir / "nonexistent.txt"

        with self.assertRaises(FileNotFoundError):
            cat.read_file_lines(nonexistent)

    def test_read_file_lines_directory(self):
        """Test read_file_lines with directory."""
        test_dir = self.test_dir / "testdir"
        test_dir.mkdir()

        with self.assertRaises(IsADirectoryError):
            cat.read_file_lines(test_dir)

    @patch('sys.stdin', new_callable=StringIO)
    def test_read_stdin(self, mock_stdin):
        """Test read_stdin function."""
        mock_stdin.write("stdin line 1\nstdin line 2\n")
        mock_stdin.seek(0)

        lines = cat.read_stdin()
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0], "stdin line 1\n")
        self.assertEqual(lines[1], "stdin line 2\n")

    def test_display_lines_basic(self):
        """Test display_lines function with basic input."""
        lines = ["Line 1\n", "Line 2\n"]

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cat.display_lines(lines, number_lines=False, number_nonblank=False, squeeze_blank=False)
            output = mock_stdout.getvalue()

            self.assertIn('Line 1', output)
            self.assertIn('Line 2', output)

    def test_display_lines_numbered(self):
        """Test display_lines function with line numbers."""
        lines = ["Line 1\n", "Line 2\n"]

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cat.display_lines(lines, number_lines=True, number_nonblank=False, squeeze_blank=False)
            output = mock_stdout.getvalue()

            self.assertIn('1\tLine 1', output)
            self.assertIn('2\tLine 2', output)

    def test_display_lines_squeeze_blank(self):
        """Test display_lines function with squeezed blanks."""
        lines = ["Line 1\n", "\n", "\n", "Line 4\n"]

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            cat.display_lines(lines, number_lines=False, number_nonblank=False, squeeze_blank=True)
            output = mock_stdout.getvalue()

            lines_output = output.strip().split('\n')
            self.assertEqual(len(lines_output), 3)  # Line 1, blank line, Line 4



if __name__ == '__main__':
    unittest.main(verbosity=2)
