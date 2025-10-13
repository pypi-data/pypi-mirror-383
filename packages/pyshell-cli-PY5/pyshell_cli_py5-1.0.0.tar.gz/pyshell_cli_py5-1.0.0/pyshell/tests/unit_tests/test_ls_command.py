#!/usr/bin/env python3
"""
Unit tests for ls command
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

from commands import ls
import shutil


class TestLsCommand(unittest.TestCase):
    """Test cases for ls command plugin."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_file = self.test_dir / 'test_file.txt'
        self.test_subdir = self.test_dir / 'subdir'

        # Create a mock shell object with current_dir attribute
        self.mock_shell = MagicMock()
        self.mock_shell.current_dir = self.test_dir

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up test directories
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)
    @patch('sys.stdout', new_callable=StringIO)
    def test_ls_default(self, mock_stdout):
        """Test ls with default behavior (current directory)."""
        with patch('commands.ls.list_directory') as mock_list:
            mock_list.return_value = [self.test_file, self.test_subdir]
            with patch('commands.ls.format_file_listing') as mock_format:
                mock_format.side_effect = lambda x: x.name
                ls.run([], self.mock_shell)
                output = mock_stdout.getvalue()

                self.assertIn('test_file.txt', output)
                self.assertIn('subdir', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_ls_specific_directory(self, mock_stdout):
        """Test ls with specific directory argument."""
        with patch('commands.ls.list_directory') as mock_list:
            mock_list.return_value = [self.test_file]
            with patch('commands.ls.format_file_listing') as mock_format:
                mock_format.side_effect = lambda x: x.name
                ls.run([str(self.test_dir)], self.mock_shell)
                output = mock_stdout.getvalue()

                self.assertIn('test_file.txt', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_ls_recursive_flag(self, mock_stdout):
        """Test ls with -R flag."""
        with patch('commands.ls.list_directory') as mock_list:
            mock_list.return_value = [self.test_file, self.test_subdir]
            with patch('commands.ls.format_file_listing') as mock_format:
                mock_format.side_effect = lambda x: x.name
                ls.run(['-R'], self.mock_shell)
                output = mock_stdout.getvalue()

                self.assertIn('test_file.txt', output)
                self.assertIn('subdir', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_ls_recursive_long_flag(self, mock_stdout):
        """Test ls with --recursive flag."""
        with patch('commands.ls.list_directory') as mock_list:
            mock_list.return_value = [self.test_file, self.test_subdir]
            with patch('commands.ls.format_file_listing') as mock_format:
                mock_format.side_effect = lambda x: x.name
                ls.run(['--recursive'], self.mock_shell)
                output = mock_stdout.getvalue()

                self.assertIn('test_file.txt', output)
                self.assertIn('subdir', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_ls_help_flag(self, mock_stdout):
        """Test ls with -h flag."""
        ls.run(['-h'], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertIn('Usage: ls [options] [directory]', output)
        self.assertIn('List directory contents', output)
        self.assertIn('Options:', output)
        self.assertIn('-R, --recursive', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_ls_help_long_flag(self, mock_stdout):
        """Test ls with --help flag."""
        ls.run(['--help'], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertIn('Usage: ls [options] [directory]', output)
        self.assertIn('Examples:', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_ls_file_target(self, mock_stdout):
        """Test ls with file as target (should print filename)."""
        with patch.object(Path, 'is_file', return_value=True):
            ls.run(['test_file.txt'], self.mock_shell)
            output = mock_stdout.getvalue()

            self.assertIn('test_file.txt', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_ls_empty_directory(self, mock_stdout):
        """Test ls with empty directory."""
        with patch('commands.ls.list_directory') as mock_list:
            mock_list.return_value = []
            ls.run([], self.mock_shell)
            output = mock_stdout.getvalue()

            self.assertEqual(output.strip(), '')

    @patch('sys.stderr', new_callable=StringIO)
    def test_ls_file_not_found(self, mock_stderr):
        """Test ls with non-existent directory."""
        with patch('commands.ls.list_directory') as mock_list:
            mock_list.side_effect = FileNotFoundError()
            result = ls.run(['/nonexistent'], self.mock_shell)
            output = mock_stderr.getvalue()

            self.assertEqual(result, 1)
            self.assertIn('No such file or directory', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_ls_permission_denied(self, mock_stderr):
        """Test ls with permission denied."""
        with patch('commands.ls.list_directory') as mock_list:
            mock_list.side_effect = PermissionError()
            ls.run(['/restricted'], self.mock_shell)
            output = mock_stderr.getvalue()

            self.assertIn('Permission denied', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_ls_recursive_with_subdirectories(self, mock_stdout):
        """Test ls -R with multiple subdirectories."""
        subdir1 = self.test_dir / 'subdir1'
        subdir2 = self.test_dir / 'subdir2'
        file1 = subdir1 / 'file1.txt'
        file2 = subdir2 / 'file2.txt'

        with patch('commands.ls.list_directory') as mock_list:
            mock_list.return_value = [self.test_file, subdir1, subdir2, file1, file2]
            with patch('commands.ls.format_file_listing') as mock_format:
                mock_format.side_effect = lambda x: x.name
                ls.run(['-R'], self.mock_shell)
                output = mock_stdout.getvalue()

                # Should contain directory headers and files
                self.assertIn('test_file.txt', output)
                self.assertIn('subdir1', output)
                self.assertIn('subdir2', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_ls_force_flag(self, mock_stdout):
        """Test ls with -f flag (force - ignore errors)."""
        with patch('commands.ls.list_directory') as mock_list:
            mock_list.side_effect = FileNotFoundError()
            result = ls.run(['-f', '/nonexistent'], self.mock_shell)
            output = mock_stdout.getvalue()

            # With force flag, should return 1 but not print error message
            self.assertEqual(result, 1)
            self.assertEqual(output.strip(), '')

    @patch('sys.stdout', new_callable=StringIO)
    def test_ls_force_long_flag(self, mock_stdout):
        """Test ls with --force flag (ignore errors)."""
        with patch('commands.ls.list_directory') as mock_list:
            mock_list.side_effect = PermissionError()
            result = ls.run(['--force', '/restricted'], self.mock_shell)
            output = mock_stdout.getvalue()

            # With force flag, should return 1 but not print error message
            self.assertEqual(result, 1)
            self.assertEqual(output.strip(), '')

    @patch('sys.stdout', new_callable=StringIO)
    def test_ls_force_flag_with_permission_error(self, mock_stdout):
        """Test ls with -f flag handles permission errors silently."""
        with patch('commands.ls.list_directory') as mock_list:
            mock_list.side_effect = PermissionError()
            result = ls.run(['-f', '/restricted'], self.mock_shell)
            output = mock_stdout.getvalue()

            # Should suppress error message with force flag
            self.assertNotIn('Permission denied', output)
            self.assertEqual(result, 1)

    @patch('sys.stdout', new_callable=StringIO)
    def test_ls_force_flag_with_general_exception(self, mock_stdout):
        """Test ls with -f flag handles general exceptions silently."""
        with patch('commands.ls.list_directory') as mock_list:
            mock_list.side_effect = Exception("General error")
            result = ls.run(['-f', '/error'], self.mock_shell)
            output = mock_stdout.getvalue()

            # Should suppress error message with force flag
            self.assertNotIn('General error', output)
            self.assertEqual(result, 1)

    @patch('sys.stderr', new_callable=StringIO)
    def test_ls_without_force_flag_shows_errors(self, mock_stderr):
        """Test ls without force flag shows error messages."""
        with patch('commands.ls.list_directory') as mock_list:
            mock_list.side_effect = FileNotFoundError()
            result = ls.run(['/nonexistent'], self.mock_shell)
            output = mock_stderr.getvalue()

            # Without force flag, should show error message
            self.assertEqual(result, 1)
            self.assertIn('No such file or directory', output)


class TestLsPrintHelp(unittest.TestCase):
    """Test cases for ls help function."""

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_help_function(self, mock_stdout):
        """Test the print_help function directly."""
        ls.print_help()
        output = mock_stdout.getvalue()

        self.assertIn('Usage: ls [options] [directory]', output)
        self.assertIn('List directory contents', output)
        self.assertIn('-R, --recursive', output)
        self.assertIn('-h, --help', output)
        self.assertIn('Examples:', output)


if __name__ == '__main__':
    unittest.main(verbosity=2)

