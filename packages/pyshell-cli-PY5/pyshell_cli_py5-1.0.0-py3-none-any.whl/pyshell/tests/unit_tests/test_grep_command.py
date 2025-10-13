#!/usr/bin/env python3
"""
Unit tests for grep command
"""

import unittest
import sys
import os
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from commands import grep
import shutil


class TestGrepCommand(unittest.TestCase):
    """Test cases for grep command plugin."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_file = self.test_dir / 'test_file.txt'
        self.test_file2 = self.test_dir / 'test_file2.txt'

        # Create a mock shell object with current_dir attribute
        self.mock_shell = MagicMock()
        self.mock_shell.current_dir = self.test_dir

    def tearDown(self):
        """Clean up test fixtures."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    @patch('sys.stdout', new_callable=StringIO)
    def test_grep_help_flag(self, mock_stdout):
        """Test grep with -h flag."""
        grep.run(['-h'], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertIn('Usage: grep [options] pattern [file...]', output)
        self.assertIn('Search for patterns in files using regular expressions', output)
        self.assertIn('Options:', output)
        self.assertIn('-n', output)
        self.assertIn('-i', output)
        self.assertIn('-h, --help', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_grep_help_long_flag(self, mock_stdout):
        """Test grep with --help flag."""
        grep.run(['--help'], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertIn('Usage: grep [options] pattern [file...]', output)
        self.assertIn('Examples:', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_grep_missing_pattern(self, mock_stderr):
        """Test grep with no pattern."""
        grep.run([], self.mock_shell)
        output = mock_stderr.getvalue()

        self.assertIn('grep: missing pattern', output)

    @patch('sys.stdin', new_callable=StringIO)
    def test_grep_missing_file(self, mock_stdin):
        """Test grep with pattern but no file (reads from stdin)."""
        # When no file is provided, grep reads from stdin
        mock_stdin.write("")
        mock_stdin.seek(0)
        result = grep.run(['pattern'], self.mock_shell)
        # Should succeed (exit code 0) with no matches found
        self.assertEqual(result, 0)

    @patch('sys.stderr', new_callable=StringIO)
    def test_grep_empty_pattern(self, mock_stderr):
        """Test grep with empty pattern."""
        grep.run(['', 'file.txt'], self.mock_shell)
        output = mock_stderr.getvalue()

        self.assertIn('grep: invalid pattern: Empty pattern', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_grep_pattern_too_long(self, mock_stderr):
        """Test grep with pattern too long."""
        long_pattern = 'a' * 10001
        grep.run([long_pattern, 'file.txt'], self.mock_shell)
        output = mock_stderr.getvalue()

        self.assertIn('grep: invalid pattern: Pattern too long', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_grep_invalid_regex(self, mock_stderr):
        """Test grep with invalid regex pattern."""
        grep.run(['[invalid', 'file.txt'], self.mock_shell)
        output = mock_stderr.getvalue()

        self.assertIn('grep: invalid pattern:', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_grep_invalid_file_operand(self, mock_stderr):
        """Test grep with invalid file operand."""
        grep.run(['pattern', ''], self.mock_shell)
        output = mock_stderr.getvalue()

        self.assertIn('grep: invalid file operand', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_grep_file_not_found(self, mock_stderr):
        """Test grep with non-existent file."""
        with patch.object(Path, 'is_file', return_value=False):
            with patch.object(Path, 'is_dir', return_value=False):
                grep.run(['pattern', 'nonexistent.txt'], self.mock_shell)
                output = mock_stderr.getvalue()

                self.assertIn("grep: nonexistent.txt: No such file or directory", output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_grep_invalid_path(self, mock_stderr):
        """Test grep with invalid path."""
        with patch.object(Path, 'resolve', side_effect=OSError()):
            grep.run(['pattern', 'invalid_path'], self.mock_shell)
            output = mock_stderr.getvalue()

            self.assertIn("grep: invalid_path: Invalid path", output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_grep_permission_denied(self, mock_stderr):
        """Test grep with permission denied."""
        with patch.object(Path, 'is_file', return_value=True):
            with patch('commands.grep.search_in_file', side_effect=PermissionError()):
                grep.run(['pattern', 'restricted.txt'], self.mock_shell)
                output = mock_stderr.getvalue()

                self.assertIn("grep: restricted.txt: Permission denied", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_grep_directory_search(self, mock_stdout):
        """Test grep with directory as target."""
        with patch.object(Path, 'is_dir', return_value=True):
            with patch.object(Path, 'iterdir', return_value=[self.test_file, self.test_file2]):
                with patch.object(Path, 'is_file', return_value=True):
                    with patch.object(Path, 'is_symlink', return_value=False):
                        with patch('commands.grep.search_in_file', return_value=1):
                            grep.run(['pattern', 'test_dir'], self.mock_shell)
                            output = mock_stdout.getvalue()

                            # Should not have error messages
                            self.assertNotIn('Permission denied', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_grep_directory_permission_denied(self, mock_stderr):
        """Test grep with directory permission denied."""
        with patch.object(Path, 'is_dir', return_value=True):
            with patch.object(Path, 'iterdir', side_effect=PermissionError()):
                grep.run(['pattern', 'restricted_dir'], self.mock_shell)
                output = mock_stderr.getvalue()

                self.assertIn("grep: restricted_dir: Permission denied", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_grep_empty_directory(self, mock_stdout):
        """Test grep with empty directory."""
        with patch.object(Path, 'is_dir', return_value=True):
            with patch.object(Path, 'iterdir', return_value=[]):
                grep.run(['pattern', 'empty_dir'], self.mock_shell)
                output = mock_stdout.getvalue()

                # Should not have any output
                self.assertEqual(output.strip(), '')

    @patch('sys.stdout', new_callable=StringIO)
    def test_grep_with_line_numbers(self, mock_stdout):
        """Test grep with -n flag."""
        with patch.object(Path, 'is_file', return_value=True):
            with patch('commands.grep.search_in_file', return_value=2):
                grep.run(['-n', 'pattern', 'file.txt'], self.mock_shell)
                output = mock_stdout.getvalue()

                # Should not have error messages
                self.assertNotIn('Permission denied', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_grep_case_insensitive(self, mock_stdout):
        """Test grep with -i flag."""
        with patch.object(Path, 'is_file', return_value=True):
            with patch('commands.grep.search_in_file', return_value=1):
                grep.run(['-i', 'pattern', 'file.txt'], self.mock_shell)
                output = mock_stdout.getvalue()

                # Should not have error messages
                self.assertNotIn('Permission denied', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_grep_multiple_files(self, mock_stdout):
        """Test grep with multiple files."""
        with patch.object(Path, 'is_file', return_value=True):
            with patch('commands.grep.search_in_file', return_value=1):
                grep.run(['pattern', 'file1.txt', 'file2.txt'], self.mock_shell)
                output = mock_stdout.getvalue()

                # Should not have error messages
                self.assertNotIn('Permission denied', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_grep_general_exception(self, mock_stderr):
        """Test grep with general exception."""
        with patch.object(Path, 'is_file', return_value=True):
            with patch('commands.grep.search_in_file', side_effect=Exception("General error")):
                grep.run(['pattern', 'file.txt'], self.mock_shell)
                output = mock_stderr.getvalue()

                self.assertIn("grep: file.txt: General error", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_grep_fixed_string_flag(self, mock_stdout):
        """Test grep with -F flag (fixed string search)."""
        with patch.object(Path, 'is_file', return_value=True):
            with patch('commands.grep.search_in_file', return_value=1):
                # Pattern with special regex characters should be treated as literal
                grep.run(['-F', 'test.*pattern', 'file.txt'], self.mock_shell)
                output = mock_stdout.getvalue()

                # Should not have error messages
                self.assertNotIn('invalid pattern', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_grep_fixed_string_with_multiword_pattern(self, mock_stdout):
        """Test grep with -F flag and pattern containing spaces."""
        with patch.object(Path, 'is_file', return_value=True):
            with patch('commands.grep.search_in_file', return_value=2):
                # Pattern with spaces should work with -F flag
                result = grep.run(['-F', 'hello world', 'file.txt'], self.mock_shell)

                # Should not have error messages
                self.assertEqual(result, 0)

    @patch('sys.stdout', new_callable=StringIO)
    def test_grep_fixed_string_case_insensitive(self, mock_stdout):
        """Test grep with -F and -i flags together."""
        with patch.object(Path, 'is_file', return_value=True):
            with patch('commands.grep.search_in_file', return_value=1):
                grep.run(['-F', '-i', 'TEST', 'file.txt'], self.mock_shell)
                output = mock_stdout.getvalue()

                # Should not have error messages
                self.assertNotIn('invalid pattern', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_grep_fixed_string_with_special_chars(self, mock_stdout):
        """Test grep with -F flag and special regex characters."""
        with patch.object(Path, 'is_file', return_value=True):
            with patch('commands.grep.search_in_file', return_value=1):
                # Pattern with regex special chars should be treated literally
                grep.run(['-F', '[test]', 'file.txt'], self.mock_shell)
                output = mock_stdout.getvalue()

                # Should not have error messages
                self.assertNotIn('invalid pattern', output)
                self.assertNotIn('unbalanced bracket', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_grep_multiword_pattern_without_quotes_error(self, mock_stderr):
        """Test grep with multiword pattern - shell splits it into separate args.
        Since ArgumentParser handles quotes, patterns without quotes are treated as
        separate arguments. 'hello world' becomes ['hello', 'world'] by the shell."""
        # When user types: grep hello world file.txt
        # Shell tokenizer splits: ['grep', 'hello', 'world', 'file.txt']
        # ArgumentParser gets: ['hello', 'world', 'file.txt']
        # Pattern: 'hello', Files: ['world', 'file.txt']
        result = grep.run(['hello', 'world', 'file.txt'], self.mock_shell)
        output = mock_stderr.getvalue()

        # Since 'world' and 'file.txt' are treated as files, expect file not found error
        self.assertIn('No such file or directory', output)
        self.assertEqual(result, 1)

    @patch('sys.stderr', new_callable=StringIO)
    def test_grep_force_flag(self, mock_stderr):
        """Test grep with -f flag (force - ignore errors)."""
        with patch.object(Path, 'is_file', return_value=False):
            with patch.object(Path, 'is_dir', return_value=False):
                result = grep.run(['-f', 'pattern', 'nonexistent.txt'], self.mock_shell)
                output = mock_stderr.getvalue()

                # With force flag, should return 1 but not print error message
                self.assertEqual(result, 1)
                self.assertEqual(output.strip(), '')

    @patch('sys.stderr', new_callable=StringIO)
    def test_grep_force_long_flag(self, mock_stderr):
        """Test grep with --force flag (ignore errors)."""
        with patch.object(Path, 'is_file', return_value=False):
            with patch.object(Path, 'is_dir', return_value=False):
                result = grep.run(['--force', 'pattern', 'nonexistent.txt'], self.mock_shell)
                output = mock_stderr.getvalue()

                # With force flag, should return 1 but not print error message
                self.assertEqual(result, 1)
                self.assertEqual(output.strip(), '')

    @patch('sys.stderr', new_callable=StringIO)
    def test_grep_force_flag_with_invalid_pattern(self, mock_stderr):
        """Test grep with -f flag handles invalid pattern silently."""
        result = grep.run(['-f', '[invalid', 'file.txt'], self.mock_shell)
        output = mock_stderr.getvalue()

        # Should suppress error message with force flag
        self.assertNotIn('invalid pattern', output)
        self.assertEqual(result, 1)

    @patch('sys.stderr', new_callable=StringIO)
    def test_grep_force_flag_with_permission_error(self, mock_stderr):
        """Test grep with -f flag handles permission errors silently."""
        with patch.object(Path, 'is_file', return_value=True):
            with patch('commands.grep.search_in_file', side_effect=PermissionError()):
                result = grep.run(['-f', 'pattern', 'restricted.txt'], self.mock_shell)
                output = mock_stderr.getvalue()

                # Should suppress error message with force flag
                self.assertNotIn('Permission denied', output)
                self.assertEqual(result, 1)

    @patch('sys.stderr', new_callable=StringIO)
    def test_grep_force_flag_with_general_exception(self, mock_stderr):
        """Test grep with -f flag handles general exceptions silently."""
        with patch.object(Path, 'is_file', return_value=True):
            with patch('commands.grep.search_in_file', side_effect=Exception("General error")):
                result = grep.run(['-f', 'pattern', 'file.txt'], self.mock_shell)
                output = mock_stderr.getvalue()

                # Should suppress error message with force flag
                self.assertNotIn('General error', output)
                self.assertEqual(result, 1)

    @patch('sys.stderr', new_callable=StringIO)
    def test_grep_force_flag_with_invalid_path(self, mock_stderr):
        """Test grep with -f flag handles invalid path silently."""
        with patch.object(Path, 'resolve', side_effect=OSError()):
            result = grep.run(['-f', 'pattern', 'invalid_path'], self.mock_shell)
            output = mock_stderr.getvalue()

            # Should suppress error message with force flag
            self.assertNotIn('Invalid path', output)
            self.assertEqual(result, 1)

    @patch('sys.stderr', new_callable=StringIO)
    def test_grep_force_flag_with_directory_permission_error(self, mock_stderr):
        """Test grep with -f flag handles directory permission errors silently."""
        with patch.object(Path, 'is_dir', return_value=True):
            with patch.object(Path, 'iterdir', side_effect=PermissionError()):
                result = grep.run(['-f', 'pattern', 'restricted_dir'], self.mock_shell)
                output = mock_stderr.getvalue()

                # Should suppress error message with force flag
                self.assertNotIn('Permission denied', output)
                self.assertEqual(result, 1)

    @patch('sys.stderr', new_callable=StringIO)
    def test_grep_without_force_flag_shows_errors(self, mock_stderr):
        """Test grep without force flag shows error messages."""
        with patch.object(Path, 'is_file', return_value=False):
            with patch.object(Path, 'is_dir', return_value=False):
                result = grep.run(['pattern', 'nonexistent.txt'], self.mock_shell)
                output = mock_stderr.getvalue()

                # Without force flag, should show error message
                self.assertEqual(result, 1)
                self.assertIn('No such file or directory', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_grep_combined_flags(self, mock_stdout):
        """Test grep with multiple flags combined."""
        with patch.object(Path, 'is_file', return_value=True):
            with patch('commands.grep.search_in_file', return_value=2):
                # Test -F, -i, and -n flags together
                grep.run(['-F', '-i', '-n', 'pattern', 'file.txt'], self.mock_shell)
                output = mock_stdout.getvalue()

                # Should not have error messages
                self.assertNotIn('invalid', output)


class TestGrepSearchInFile(unittest.TestCase):
    """Test cases for search_in_file function."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_file = self.test_dir / 'test.txt'
        self.pattern = MagicMock()
        # Mock pattern that matches lines containing 'hello' or 'pattern' but not 'another'
        def mock_search(line):
            return 'hello' in line or 'pattern' in line
        self.pattern.search = mock_search

    def tearDown(self):
        """Clean up test fixtures."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    @patch('sys.stdout', new_callable=StringIO)
    def test_search_in_file_not_file(self, _mock_stdout):
        """Test search_in_file with non-file path."""
        with patch.object(Path, 'is_file', return_value=False):
            matches = grep.search_in_file(self.test_file, self.pattern, False, False)
            self.assertEqual(matches, 0)

    @patch('sys.stdout', new_callable=StringIO)
    def test_search_in_file_symlink(self, _mock_stdout):
        """Test search_in_file with symlink."""
        with patch.object(Path, 'is_file', return_value=True):
            with patch.object(Path, 'is_symlink', return_value=True):
                matches = grep.search_in_file(self.test_file, self.pattern, False, False)
                self.assertEqual(matches, 0)

    @patch('sys.stderr', new_callable=StringIO)
    def test_search_in_file_too_large(self, mock_stderr):
        """Test search_in_file with file too large."""
        with patch.object(Path, 'is_file', return_value=True):
            with patch.object(Path, 'is_symlink', return_value=False):
                with patch.object(Path, 'stat') as mock_stat:
                    mock_stat.return_value.st_size = 101 * 1024 * 1024  # 101MB
                    matches = grep.search_in_file(self.test_file, self.pattern, False, False)
                    output = mock_stderr.getvalue()

                    self.assertEqual(matches, 0)
                    self.assertIn('File too large, skipping', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_search_in_file_empty(self, _mock_stdout):
        """Test search_in_file with empty file."""
        with patch.object(Path, 'is_file', return_value=True):
            with patch.object(Path, 'is_symlink', return_value=False):
                with patch.object(Path, 'stat') as mock_stat:
                    mock_stat.return_value.st_size = 0
                    matches = grep.search_in_file(self.test_file, self.pattern, False, False)
                    self.assertEqual(matches, 0)

    @patch('sys.stdout', new_callable=StringIO)
    def test_search_in_file_binary(self, _mock_stdout):
        """Test search_in_file with binary file."""
        with patch.object(Path, 'is_file', return_value=True):
            with patch.object(Path, 'is_symlink', return_value=False):
                with patch.object(Path, 'stat') as mock_stat:
                    mock_stat.return_value.st_size = 100
                    with patch('commands.grep.is_binary_file', return_value=True):
                        matches = grep.search_in_file(self.test_file, self.pattern, False, False)
                        self.assertEqual(matches, 0)

    @patch('sys.stdout', new_callable=StringIO)
    def test_search_in_file_success(self, mock_stdout):
        """Test successful search_in_file."""
        with patch.object(Path, 'is_file', return_value=True):
            with patch.object(Path, 'is_symlink', return_value=False):
                with patch.object(Path, 'stat') as mock_stat:
                    mock_stat.return_value.st_size = 100
                    with patch('commands.grep.is_binary_file', return_value=False):
                        with patch('builtins.open', mock_open(read_data='hello world\npattern found\nanother line')):
                            matches = grep.search_in_file(self.test_file, self.pattern, False, False)
                            output = mock_stdout.getvalue()

                            self.assertEqual(matches, 2)
                            self.assertIn('hello world', output)
                            self.assertIn('pattern found', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_search_in_file_with_line_numbers(self, mock_stdout):
        """Test search_in_file with line numbers."""
        with patch.object(Path, 'is_file', return_value=True):
            with patch.object(Path, 'is_symlink', return_value=False):
                with patch.object(Path, 'stat') as mock_stat:
                    mock_stat.return_value.st_size = 100
                    with patch('commands.grep.is_binary_file', return_value=False):
                        with patch('builtins.open', mock_open(read_data='hello world\npattern found\nanother line')):
                            matches = grep.search_in_file(self.test_file, self.pattern, True, False)
                            output = mock_stdout.getvalue()

                            self.assertEqual(matches, 2)
                            self.assertIn('1:', output)
                            self.assertIn('2:', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_search_in_file_with_filename(self, mock_stdout):
        """Test search_in_file with filename."""
        with patch.object(Path, 'is_file', return_value=True):
            with patch.object(Path, 'is_symlink', return_value=False):
                with patch.object(Path, 'stat') as mock_stat:
                    mock_stat.return_value.st_size = 100
                    with patch('commands.grep.is_binary_file', return_value=False):
                        with patch.object(Path, 'name', 'test.txt'):
                            with patch('builtins.open', mock_open(read_data='hello world\npattern found\nanother line')):
                                matches = grep.search_in_file(self.test_file, self.pattern, False, True)
                                output = mock_stdout.getvalue()

                                self.assertEqual(matches, 2)
                                self.assertIn('test.txt:', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_search_in_file_long_line(self, mock_stdout):
        """Test search_in_file with very long line."""
        with patch.object(Path, 'is_file', return_value=True):
            with patch.object(Path, 'is_symlink', return_value=False):
                with patch.object(Path, 'stat') as mock_stat:
                    mock_stat.return_value.st_size = 100
                    with patch('commands.grep.is_binary_file', return_value=False):
                        long_line = 'a' * 100001
                        with patch('builtins.open', mock_open(read_data=f'{long_line}\npattern found')):
                            matches = grep.search_in_file(self.test_file, self.pattern, False, False)
                            output = mock_stdout.getvalue()

                            # Should skip the long line but find the second line
                            self.assertEqual(matches, 1)
                            self.assertIn('pattern found', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_search_in_file_unicode_error(self, _mock_stdout):
        """Test search_in_file with unicode decode error."""
        with patch.object(Path, 'is_file', return_value=True):
            with patch.object(Path, 'is_symlink', return_value=False):
                with patch.object(Path, 'stat') as mock_stat:
                    mock_stat.return_value.st_size = 100
                    with patch('commands.grep.is_binary_file', return_value=False):
                        with patch('builtins.open', side_effect=UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid')):
                            matches = grep.search_in_file(self.test_file, self.pattern, False, False)
                            self.assertEqual(matches, 0)

    @patch('sys.stderr', new_callable=StringIO)
    def test_search_in_file_memory_error(self, mock_stderr):
        """Test search_in_file with memory error."""
        with patch.object(Path, 'is_file', return_value=True):
            with patch.object(Path, 'is_symlink', return_value=False):
                with patch.object(Path, 'stat') as mock_stat:
                    mock_stat.return_value.st_size = 100
                    with patch('commands.grep.is_binary_file', return_value=False):
                        with patch('builtins.open', side_effect=MemoryError()):
                            matches = grep.search_in_file(self.test_file, self.pattern, False, False)
                            output = mock_stderr.getvalue()

                            self.assertEqual(matches, 0)
                            self.assertIn('File too large to process', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_search_in_file_permission_denied(self, mock_stderr):
        """Test search_in_file with permission denied."""
        with patch.object(Path, 'is_file', return_value=True):
            with patch.object(Path, 'is_symlink', return_value=False):
                with patch.object(Path, 'stat', side_effect=PermissionError()):
                    matches = grep.search_in_file(self.test_file, self.pattern, False, False)
                    output = mock_stderr.getvalue()

                    self.assertEqual(matches, 0)
                    self.assertIn('Permission denied', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_search_in_file_io_error(self, mock_stderr):
        """Test search_in_file with I/O error."""
        with patch.object(Path, 'is_file', return_value=True):
            with patch.object(Path, 'is_symlink', return_value=False):
                with patch.object(Path, 'stat') as mock_stat:
                    mock_stat.return_value.st_size = 100
                    with patch('commands.grep.is_binary_file', return_value=False):
                        with patch('builtins.open', side_effect=OSError(5, "I/O error")):
                            matches = grep.search_in_file(self.test_file, self.pattern, False, False)
                            output = mock_stderr.getvalue()

                            self.assertEqual(matches, 0)
                            self.assertIn('I/O error', output)


class TestGrepIsBinaryFile(unittest.TestCase):
    """Test cases for is_binary_file function."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_file = self.test_dir / 'test.txt'

    def tearDown(self):
        """Clean up test fixtures."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    def test_is_binary_file_with_null_bytes(self):
        """Test is_binary_file with null bytes."""
        with patch('builtins.open', mock_open(read_data=b'hello\x00world')):
            result = grep.is_binary_file(self.test_file)
            self.assertTrue(result)

    def test_is_binary_file_with_high_non_text_ratio(self):
        """Test is_binary_file with high non-text character ratio."""
        # Create data with >30% non-text characters
        binary_data = bytes(range(256))  # All possible byte values
        with patch('builtins.open', mock_open(read_data=binary_data)):
            result = grep.is_binary_file(self.test_file)
            self.assertTrue(result)

    def test_is_binary_file_text_file(self):
        """Test is_binary_file with text file."""
        with patch('builtins.open', mock_open(read_data=b'hello world\nthis is text')):
            result = grep.is_binary_file(self.test_file)
            self.assertFalse(result)

    def test_is_binary_file_exception(self):
        """Test is_binary_file with exception."""
        with patch('builtins.open', side_effect=Exception()):
            result = grep.is_binary_file(self.test_file)
            self.assertTrue(result)  # Should return True on exception


class TestGrepIsValidPattern(unittest.TestCase):
    """Test cases for is_valid_pattern function."""

    def test_is_valid_pattern_empty(self):
        """Test is_valid_pattern with empty pattern."""
        is_valid, error_msg = grep.is_valid_pattern('')
        self.assertFalse(is_valid)
        self.assertIn('Empty pattern', error_msg)

    def test_is_valid_pattern_whitespace_only(self):
        """Test is_valid_pattern with whitespace only pattern."""
        is_valid, error_msg = grep.is_valid_pattern('   ')
        self.assertFalse(is_valid)
        self.assertIn('Empty pattern', error_msg)

    def test_is_valid_pattern_too_long(self):
        """Test is_valid_pattern with pattern too long."""
        long_pattern = 'a' * 10001
        is_valid, error_msg = grep.is_valid_pattern(long_pattern)
        self.assertFalse(is_valid)
        self.assertIn('Pattern too long', error_msg)

    def test_is_valid_pattern_invalid_regex(self):
        """Test is_valid_pattern with invalid regex."""
        is_valid, error_msg = grep.is_valid_pattern('[invalid')
        self.assertFalse(is_valid)
        self.assertIn('unbalanced bracket', error_msg)

    def test_is_valid_pattern_valid(self):
        """Test is_valid_pattern with valid pattern."""
        is_valid, error_msg = grep.is_valid_pattern('hello.*world')
        self.assertTrue(is_valid)
        self.assertIsNone(error_msg)


class TestGrepPrintHelp(unittest.TestCase):
    """Test cases for grep help function."""

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_help_function(self, mock_stdout):
        """Test the print_help function directly."""
        grep.print_help()
        output = mock_stdout.getvalue()

        self.assertIn('Usage: grep [options] pattern [file...]', output)
        self.assertIn('Search for patterns in files using regular expressions', output)
        self.assertIn('-n', output)
        self.assertIn('-i', output)
        self.assertIn('-h, --help', output)
        self.assertIn('Examples:', output)
        self.assertIn('Note:', output)


if __name__ == '__main__':
    unittest.main(verbosity=2)

