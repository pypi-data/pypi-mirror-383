#!/usr/bin/env python3
"""
Unit tests for pwd command
"""

import unittest
import sys
import os
from io import StringIO
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from commands import pwd


class TestPwdCommand(unittest.TestCase):
    """Test cases for pwd command plugin."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path('/home/user/test')
        # Create a mock shell object with current_dir attribute
        self.mock_shell = MagicMock()
        self.mock_shell.current_dir = self.test_dir

    @patch('sys.stdout', new_callable=StringIO)
    def test_pwd_default(self, mock_stdout):
        """Test pwd with default behavior (logical path)."""
        pwd.run([], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertIn(str(self.test_dir.absolute()), output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_pwd_logical_flag(self, mock_stdout):
        """Test pwd with -L flag."""
        pwd.run(['-L'], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertIn(str(self.test_dir.absolute()), output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_pwd_physical_flag(self, mock_stdout):
        """Test pwd with -P flag (resolves symlinks)."""
        pwd.run(['-P'], self.mock_shell)
        output = mock_stdout.getvalue()

        # Should contain resolved path
        self.assertIn(str(self.test_dir.resolve()), output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_pwd_help_flag(self, mock_stdout):
        """Test pwd with -h flag."""
        pwd.run(['-h'], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertIn('pwd - print working directory', output)
        self.assertIn('Usage:', output)
        self.assertIn('Options:', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_pwd_help_long_flag(self, mock_stdout):
        """Test pwd with --help flag."""
        pwd.run(['--help'], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertIn('pwd - print working directory', output)
        self.assertIn('Examples:', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_pwd_conflicting_flags(self, mock_stderr):
        """Test pwd with both -L and -P (should error)."""
        pwd.run(['-L', '-P'], self.mock_shell)
        output = mock_stderr.getvalue()

        self.assertIn('cannot specify both -P and -L', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_pwd_long_form_flags(self, mock_stdout):
        """Test pwd with --logical and --physical flags."""
        pwd.run(['--logical'], self.mock_shell)
        output1 = mock_stdout.getvalue()

        mock_stdout.truncate(0)
        mock_stdout.seek(0)

        pwd.run(['--physical'], self.mock_shell)
        output2 = mock_stdout.getvalue()

        self.assertTrue(len(output1) > 0)
        self.assertTrue(len(output2) > 0)

    @patch('sys.stderr', new_callable=StringIO)
    def test_pwd_physical_with_mock_error(self, mock_stderr):
        """Test pwd -P with mocked resolve error."""
        mock_dir = MagicMock(spec=Path)
        mock_dir.resolve.side_effect = Exception("Permission denied")

        # Create a mock shell with the mock directory
        mock_shell = MagicMock()
        mock_shell.current_dir = mock_dir

        pwd.run(['-P'], mock_shell)
        output = mock_stderr.getvalue()

        self.assertIn('error resolving physical path', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_pwd_output_is_single_line(self, mock_stdout):
        """Test that pwd output is a single line."""
        pwd.run([], self.mock_shell)
        output = mock_stdout.getvalue().strip()

        lines = output.split('\n')
        self.assertEqual(len(lines), 1)


class TestPwdPrintHelp(unittest.TestCase):
    """Test cases for pwd help function."""

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_help_function(self, mock_stdout):
        """Test the print_help function directly."""
        pwd.print_help()
        output = mock_stdout.getvalue()

        self.assertIn('pwd - print working directory', output)
        self.assertIn('Usage: pwd [OPTION]', output)
        self.assertIn('-L, --logical', output)
        self.assertIn('-P, --physical', output)
        self.assertIn('-h, --help', output)
        self.assertIn('Examples:', output)
        self.assertIn('Exit Status:', output)


if __name__ == '__main__':
    unittest.main(verbosity=2)

