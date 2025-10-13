#!/usr/bin/env python3
"""
Unit tests for clear command
"""

import unittest
import sys
import os
from io import StringIO
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from commands import clear


class TestClearCommand(unittest.TestCase):
    """Test cases for clear command plugin."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path('/home/user/test')
        # Create a mock shell object with current_dir attribute
        self.mock_shell = MagicMock()
        self.mock_shell.current_dir = self.test_dir

    @patch('sys.stdout', new_callable=StringIO)
    def test_clear_default(self, mock_stdout):
        """Test clear with default behavior."""
        result = clear.run([], self.mock_shell)

        # Clear command should return 0 (success)
        self.assertEqual(result, 0)

        # Should output ANSI escape sequences for clearing
        output = mock_stdout.getvalue()
        self.assertIn('\033[2J\033[H', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_clear_help_short(self, mock_stdout):
        """Test clear with -h flag."""
        result = clear.run(['-h'], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertEqual(result, 0)
        self.assertIn('clear - clear the terminal screen', output)
        self.assertIn('Usage:', output)
        self.assertIn('Options:', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_clear_help_long(self, mock_stdout):
        """Test clear with --help flag."""
        result = clear.run(['--help'], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertEqual(result, 0)
        self.assertIn('clear - clear the terminal screen', output)
        self.assertIn('Examples:', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_clear_with_arguments(self, mock_stderr):
        """Test clear with invalid arguments."""
        result = clear.run(['invalid'], self.mock_shell)
        output = mock_stderr.getvalue()

        self.assertEqual(result, 1)
        self.assertIn('clear: invalid operand(s) provided', output)
        self.assertIn('Try \'clear --help\'', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_clear_multiple_arguments(self, mock_stderr):
        """Test clear with multiple invalid arguments."""
        result = clear.run(['arg1', 'arg2'], self.mock_shell)
        output = mock_stderr.getvalue()

        self.assertEqual(result, 1)
        self.assertIn('clear: invalid operand(s) provided', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_clear_with_flags_and_args(self, mock_stdout):
        """Test clear with flags and arguments."""
        result = clear.run(['-h', 'invalid'], self.mock_shell)
        output = mock_stdout.getvalue()

        # Should show help (help flag takes precedence)
        self.assertEqual(result, 0)
        self.assertIn('clear - clear the terminal screen', output)

    @patch('os.name', 'nt')  # Mock Windows
    @patch('os.system')
    @patch('sys.stdout', new_callable=StringIO)
    def test_clear_windows_fallback(self, mock_stdout, mock_system):
        """Test clear on Windows (uses cls command)."""
        result = clear.run([], self.mock_shell)

        self.assertEqual(result, 0)
        # Should call both ANSI escape and Windows cls
        mock_system.assert_called_with('cls')

    @patch('os.name', 'posix')  # Mock Unix/Linux
    @patch('os.system')
    @patch('sys.stdout', new_callable=StringIO)
    def test_clear_unix_fallback(self, mock_stdout, mock_system):
        """Test clear on Unix/Linux (uses clear command)."""
        result = clear.run([], self.mock_shell)

        self.assertEqual(result, 0)
        # Should call both ANSI escape and Unix clear
        mock_system.assert_called_with('clear')

    @patch('sys.stdout', new_callable=StringIO)
    def test_clear_output_format(self, mock_stdout):
        """Test that clear outputs the correct ANSI escape sequences."""
        result = clear.run([], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertEqual(result, 0)
        # Should contain ANSI escape sequences for clearing screen and moving cursor
        self.assertIn('\033[2J', output)  # Clear screen
        self.assertIn('\033[H', output)   # Move cursor to home position


class TestClearPrintHelp(unittest.TestCase):
    """Test cases for clear help function."""

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_help_function(self, mock_stdout):
        """Test the print_help function directly."""
        clear.print_help()
        output = mock_stdout.getvalue()

        # Check for key elements in help text
        self.assertIn('clear - clear the terminal screen', output)
        self.assertIn('Usage:', output)
        self.assertIn('Options:', output)
        self.assertIn('Examples:', output)
        self.assertIn('Exit Status:', output)
        self.assertIn('-h, --help', output)
        self.assertIn('clear          Clear the terminal screen', output)


if __name__ == '__main__':
    unittest.main()

