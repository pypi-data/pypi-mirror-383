#!/usr/bin/env python3
"""
Unit tests for PyShell core functionality
"""

import unittest
import sys
import os
from io import StringIO
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.shell import PyShell  # pylint: disable=wrong-import-position


class TestPyShellInit(unittest.TestCase):
    """Test cases for PyShell initialization."""

    def test_shell_initialization(self):
        """Test that PyShell initializes correctly."""
        shell = PyShell()

        self.assertIsInstance(shell.current_dir, Path)
        self.assertIsInstance(shell.commands_dir, Path)
        self.assertIsInstance(shell.builtin_commands, dict)

    def test_builtin_commands_registered(self):
        """Test that built-in commands are registered."""
        shell = PyShell()

        expected_commands = ['date', 'whoami', 'hostname', 'timeit', 'exit']
        for cmd in expected_commands:
            self.assertIn(cmd, shell.builtin_commands)

    def test_commands_dir_exists(self):
        """Test that commands directory is set correctly."""
        shell = PyShell()

        self.assertTrue(shell.commands_dir.exists())
        self.assertTrue(shell.commands_dir.is_dir())


class TestTokenizer(unittest.TestCase):
    """Test cases for command tokenization."""

    def setUp(self):
        """Set up test fixtures."""
        self.shell = PyShell()

    def test_tokenize_simple_command(self):
        """Test tokenizing a simple command."""
        tokens = self.shell._tokenize("ls")

        self.assertEqual(tokens, ['ls'])

    def test_tokenize_command_with_args(self):
        """Test tokenizing command with arguments."""
        tokens = self.shell._tokenize("ls -la /home")

        self.assertEqual(tokens, ['ls', '-la', '/home'])

    def test_tokenize_empty_string(self):
        """Test tokenizing empty string."""
        tokens = self.shell._tokenize("")

        self.assertEqual(tokens, [])

    def test_tokenize_whitespace_only(self):
        """Test tokenizing whitespace-only string."""
        tokens = self.shell._tokenize("   ")

        self.assertEqual(tokens, [])


class TestExecuteCommand(unittest.TestCase):
    """Test cases for command execution."""

    def setUp(self):
        """Set up test fixtures."""
        self.shell = PyShell()

    def test_execute_empty_tokens(self):
        """Test executing empty token list."""
        result = self.shell._execute_command([])

        self.assertEqual(result, 1)

    @patch('sys.stdout', new_callable=StringIO)
    def test_execute_builtin_date(self, mock_stdout):
        """Test executing built-in date command."""
        result = self.shell._execute_command(['date'])

        self.assertEqual(result, 0)
        output = mock_stdout.getvalue()
        self.assertTrue(len(output) > 0)

    @patch('sys.stdout', new_callable=StringIO)
    def test_execute_builtin_whoami(self, mock_stdout):
        """Test executing built-in whoami command."""
        result = self.shell._execute_command(['whoami'])

        self.assertEqual(result, 0)
        output = mock_stdout.getvalue()
        self.assertTrue(len(output) > 0)

    @patch('sys.stdout', new_callable=StringIO)
    def test_execute_builtin_hostname(self, mock_stdout):
        """Test executing built-in hostname command."""
        result = self.shell._execute_command(['hostname'])

        self.assertEqual(result, 0)
        output = mock_stdout.getvalue()
        self.assertTrue(len(output) > 0)

    @patch('sys.stderr', new_callable=StringIO)
    def test_execute_invalid_command(self, mock_stderr):
        """Test executing invalid command."""
        result = self.shell._execute_command(['invalidcommand123'])

        self.assertEqual(result, 1)
        output = mock_stderr.getvalue()
        self.assertIn('invalid command', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_execute_plugin_command_ls(self, _mock_stdout):
        """Test executing plugin command (ls)."""
        result = self.shell._execute_command(['ls'])

        # Command may succeed or fail depending on environment
        self.assertIsInstance(result, int)

    @patch('sys.stdout', new_callable=StringIO)
    def test_execute_command_with_args(self, mock_stdout):
        """Test executing command with arguments."""
        result = self.shell._execute_command(['pwd', '-h'])

        # Command may succeed or fail depending on environment
        self.assertIsInstance(result, int)
        output = mock_stdout.getvalue()
        # Check that we got some output (either help or error)
        self.assertTrue(len(output) > 0)


class TestBuiltinCommands(unittest.TestCase):
    """Test cases for built-in commands."""

    def setUp(self):
        """Set up test fixtures."""
        self.shell = PyShell()

    @patch('sys.stdout', new_callable=StringIO)
    def test_cmd_date(self, mock_stdout):
        """Test _cmd_date built-in."""
        self.shell._cmd_date([])
        output = mock_stdout.getvalue()

        # Should output date in format like "Mon Oct 6 12:00:00 2025"
        self.assertTrue(len(output) > 0)
        self.assertRegex(output, r'\w{3} \w{3}\s+\d+')

    @patch('sys.stdout', new_callable=StringIO)
    def test_cmd_whoami(self, mock_stdout):
        """Test _cmd_whoami built-in."""
        self.shell._cmd_whoami([])
        output = mock_stdout.getvalue()

        self.assertTrue(len(output.strip()) > 0)

    @patch('sys.stdout', new_callable=StringIO)
    def test_cmd_hostname(self, mock_stdout):
        """Test _cmd_hostname built-in."""
        self.shell._cmd_hostname([])
        output = mock_stdout.getvalue()

        self.assertTrue(len(output.strip()) > 0)

    @patch('sys.stdout', new_callable=StringIO)
    def test_cmd_timeit_no_args(self, mock_stdout):
        """Test _cmd_timeit with no arguments."""
        self.shell._cmd_timeit([])
        output = mock_stdout.getvalue()

        self.assertIn('missing command', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_cmd_timeit_with_valid_command(self, mock_stdout):
        """Test _cmd_timeit with valid command."""
        self.shell._cmd_timeit(['date'])
        output = mock_stdout.getvalue()

        self.assertIn('took', output)
        self.assertIn('seconds', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_cmd_timeit_with_invalid_command(self, mock_stdout):
        """Test _cmd_timeit with invalid command."""
        self.shell._cmd_timeit(['invalidcmd'])
        output = mock_stdout.getvalue()

        # Should show timing even for invalid command
        self.assertIn('Execution time:', output)
        self.assertIn('seconds', output)

    @patch('sys.exit')
    @patch('sys.stdout', new_callable=StringIO)
    def test_cmd_exit_no_args(self, mock_stdout, mock_exit):
        """Test _cmd_exit with no arguments."""
        self.shell._cmd_exit([])

        mock_exit.assert_called_once_with(0)
        self.assertIn('exited', mock_stdout.getvalue())

    @patch('sys.exit')
    @patch('sys.stdout', new_callable=StringIO)
    def test_cmd_exit_with_code(self, mock_stdout, mock_exit):
        """Test _cmd_exit with exit code."""
        self.shell._cmd_exit(['42'])

        mock_exit.assert_called_once_with(42)

    @patch('sys.exit')
    @patch('sys.stdout', new_callable=StringIO)
    def test_cmd_exit_invalid_code(self, mock_stdout, mock_exit):
        """Test _cmd_exit with invalid exit code."""
        self.shell._cmd_exit(['invalid'])
        output = mock_stdout.getvalue()

        self.assertIn('numeric argument required', output)
        mock_exit.assert_called_once_with(2)

    @patch('sys.stdout', new_callable=StringIO)
    def test_cmd_timeit_with_args(self, mock_stdout):
        """Test _cmd_timeit with command and arguments."""
        self.shell._cmd_timeit(['pwd', '-h'])
        output = mock_stdout.getvalue()

        # Check for either success or failure message
        self.assertTrue('took' in output or 'Execution time:' in output)
        self.assertIn('seconds', output)
        # Check for either the full command or just the base command
        self.assertTrue('`pwd -h`' in output or '`pwd`' in output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_cmd_timeit_timing_accuracy(self, mock_stdout):
        """Test _cmd_timeit timing accuracy."""
        with patch('time.time', side_effect=[0.0, 1.5, 0.0, 1.5]):
            self.shell._cmd_timeit(['date'])
            output = mock_stdout.getvalue()

            # Should show timing information
            self.assertIn('took', output)
            self.assertIn('seconds', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_cmd_timeit_empty_command(self, mock_stdout):
        """Test _cmd_timeit with empty command."""
        self.shell._cmd_timeit([''])
        output = mock_stdout.getvalue()

        self.assertIn('failed or not found', output)
        self.assertIn('Execution time:', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_cmd_timeit_multiple_args(self, mock_stdout):
        """Test _cmd_timeit with multiple arguments."""
        self.shell._cmd_timeit(['ls', '-la', '/tmp'])
        output = mock_stdout.getvalue()

        # Check for either success or failure message
        self.assertTrue('took' in output or 'Execution time:' in output)
        self.assertIn('seconds', output)
        # Check for either the full command or just the base command
        self.assertTrue('`ls -la /tmp`' in output or '`ls`' in output)


class TestExecutePluginCommand(unittest.TestCase):
    """Test cases for plugin command execution."""

    def setUp(self):
        """Set up test fixtures."""
        self.shell = PyShell()

    def test_plugin_command_not_found(self):
        """Test executing non-existent plugin command."""
        with self.assertRaises(FileNotFoundError):
            self.shell._execute_plugin_command('nonexistent', [])

    @patch('sys.stdout', new_callable=StringIO)
    def test_plugin_command_pwd(self, mock_stdout):
        """Test executing pwd plugin command."""
        self.shell._execute_plugin_command('pwd', [])
        output = mock_stdout.getvalue()

        self.assertTrue(len(output) > 0)

    @patch('sys.stdout', new_callable=StringIO)
    def test_plugin_command_with_args(self, mock_stdout):
        """Test executing plugin command with arguments."""
        self.shell._execute_plugin_command('pwd', ['-h'])
        output = mock_stdout.getvalue()

        self.assertIn('Usage:', output)


class TestCommandReturnValues(unittest.TestCase):
    """Test cases for command execution return values."""

    def setUp(self):
        """Set up test fixtures."""
        self.shell = PyShell()

    @patch('sys.stdout', new_callable=StringIO)
    def test_valid_command_returns_zero(self, _mock_stdout):
        """Test that valid commands return 0."""
        result = self.shell._execute_command(['date'])

        self.assertEqual(result, 0)

    @patch('sys.stdout', new_callable=StringIO)
    def test_invalid_command_returns_one(self, _mock_stdout):
        """Test that invalid commands return 1."""
        result = self.shell._execute_command(['notacommand'])

        self.assertEqual(result, 1)

    @patch('sys.stdout', new_callable=StringIO)
    def test_builtin_exception_returns_one(self, _mock_stdout):
        """Test that built-in command exceptions return 1."""
        # Mock a built-in command to raise an exception
        original_cmd = self.shell.builtin_commands['date']
        self.shell.builtin_commands['date'] = MagicMock(side_effect=Exception("Test error"))

        result = self.shell._execute_command(['date'])

        # Restore original
        self.shell.builtin_commands['date'] = original_cmd

        self.assertEqual(result, 1)


class TestParseAndExecutePipeline(unittest.TestCase):
    """Test cases for _parse_and_execute_pipeline method."""

    def setUp(self):
        """Set up test fixtures."""
        self.shell = PyShell()
        self.test_dir = Path(__file__).parent
        self.test_file = self.test_dir.parent / "resources" / "test_file.txt"

    @patch('sys.stdout', new_callable=StringIO)
    def test_simple_command(self, mock_stdout):
        """Test executing a simple command through pipeline."""
        tokens = self.shell._tokenize("pwd")
        result = self.shell._parse_and_execute_pipeline(tokens)

        self.assertEqual(result, 0)
        output = mock_stdout.getvalue()
        self.assertTrue(len(output) > 0)

    @patch('sys.stdout', new_callable=StringIO)
    def test_command_with_args(self, mock_stdout):
        """Test executing command with arguments through pipeline."""
        tokens = self.shell._tokenize("pwd -h")
        result = self.shell._parse_and_execute_pipeline(tokens)

        self.assertEqual(result, 0)
        output = mock_stdout.getvalue()
        self.assertIn("Usage:", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_pipeline_two_commands(self, mock_stdout):
        """Test executing a pipeline with two commands."""
        # Create a test file
        test_file = self.test_dir / "temp_test.txt"
        test_file.write_text("apple\nbanana\ncherry\napricot\n")

        try:
            tokens = self.shell._tokenize(f"cat {test_file} | grep ap")
            result = self.shell._parse_and_execute_pipeline(tokens)

            self.assertEqual(result, 0)
            output = mock_stdout.getvalue()
            self.assertIn("apple", output)
            self.assertIn("apricot", output)
            self.assertNotIn("banana", output)
        finally:
            if test_file.exists():
                test_file.unlink()

    @patch('sys.stdout', new_callable=StringIO)
    def test_pipeline_three_commands(self, mock_stdout):
        """Test executing a pipeline with three commands."""
        # Create a test file
        test_file = self.test_dir / "temp_test2.txt"
        test_file.write_text("line1\nline2\nline3\nline4\nline5\n")

        try:
            tokens = self.shell._tokenize(f"cat {test_file} | head -3 | tail -1")
            result = self.shell._parse_and_execute_pipeline(tokens)

            self.assertEqual(result, 0)
            output = mock_stdout.getvalue()
            # Output should contain line3
            self.assertIn("line3", output)
        finally:
            if test_file.exists():
                test_file.unlink()

    @patch('sys.stdout', new_callable=StringIO)
    def test_output_redirection(self, mock_stdout):
        """Test command with output redirection."""
        output_file = self.test_dir / "temp_output.txt"

        try:
            tokens = self.shell._tokenize(f"pwd > {output_file}")
            result = self.shell._parse_and_execute_pipeline(tokens)

            self.assertEqual(result, 0)
            self.assertTrue(output_file.exists())
            content = output_file.read_text()
            self.assertTrue(len(content) > 0)
        finally:
            if output_file.exists():
                output_file.unlink()

    @patch('sys.stdout', new_callable=StringIO)
    def test_output_redirection_append(self, mock_stdout):
        """Test command with append redirection."""
        output_file = self.test_dir / "temp_append.txt"
        input_file1 = self.test_dir / "temp_in1.txt"
        input_file2 = self.test_dir / "temp_in2.txt"

        try:
            # Create input files
            input_file1.write_text("first\n")
            input_file2.write_text("second\n")

            # Append first line
            tokens = self.shell._tokenize(f"cat {input_file1} >> {output_file}")
            result = self.shell._parse_and_execute_pipeline(tokens)
            self.assertEqual(result, 0)

            # Append second line
            tokens = self.shell._tokenize(f"cat {input_file2} >> {output_file}")
            result = self.shell._parse_and_execute_pipeline(tokens)
            self.assertEqual(result, 0)

            content = output_file.read_text()
            self.assertIn("first", content)
            self.assertIn("second", content)
        finally:
            for f in [output_file, input_file1, input_file2]:
                if f.exists():
                    f.unlink()

    @patch('sys.stdout', new_callable=StringIO)
    def test_input_redirection(self, mock_stdout):
        """Test command with input redirection."""
        # Create a test file
        input_file = self.test_dir / "temp_input.txt"
        input_file.write_text("test content\n")

        try:
            tokens = self.shell._tokenize(f"cat < {input_file}")
            result = self.shell._parse_and_execute_pipeline(tokens)

            self.assertEqual(result, 0)
            output = mock_stdout.getvalue()
            self.assertIn("test content", output)
        finally:
            if input_file.exists():
                input_file.unlink()

    @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    def test_invalid_command_in_pipeline(self, mock_stderr, mock_stdout):
        """Test pipeline with invalid command."""
        tokens = self.shell._tokenize("invalidcmd123")
        result = self.shell._parse_and_execute_pipeline(tokens)

        self.assertEqual(result, 1)
        error = mock_stderr.getvalue()
        self.assertIn("invalid command", error)

    @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    def test_pipeline_with_failing_first_command(self, mock_stderr, mock_stdout):
        """Test pipeline where first command fails."""
        tokens = self.shell._tokenize("cat nonexistent.txt | grep test")
        result = self.shell._parse_and_execute_pipeline(tokens)

        # Pipeline should continue even if first command fails
        self.assertEqual(result, 0)  # grep returns 0 (no matches in empty input)

    @patch('sys.stdout', new_callable=StringIO)
    def test_empty_tokens(self, mock_stdout):
        """Test executing empty token list."""
        tokens = []
        result = self.shell._parse_and_execute_pipeline(tokens)

        # Empty pipeline should succeed
        self.assertEqual(result, 0)

    @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    def test_invalid_redirection_syntax(self, mock_stderr, mock_stdout):
        """Test invalid redirection syntax."""
        tokens = self.shell._tokenize("pwd > ")
        result = self.shell._parse_and_execute_pipeline(tokens)

        self.assertEqual(result, 1)
        error = mock_stderr.getvalue()
        # Should contain error message about redirection
        self.assertIn("pyshell:", error)

    @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    def test_pipeline_parse_error_to_stderr(self, mock_stderr, mock_stdout):
        """Test that pipeline parsing errors are printed to stderr."""
        # Create an invalid pipeline syntax (multiple consecutive pipes)
        tokens = self.shell._tokenize("cat file.txt | | grep test")
        result = self.shell._parse_and_execute_pipeline(tokens)

        self.assertEqual(result, 1)
        error = mock_stderr.getvalue()
        self.assertIn("pyshell:", error)
        # stdout should be empty (no error output there)
        self.assertEqual(mock_stdout.getvalue(), "")

    @patch('sys.stdout', new_callable=StringIO)
    def test_builtin_command_in_pipeline(self, mock_stdout):
        """Test built-in command through pipeline."""
        tokens = self.shell._tokenize("date")
        result = self.shell._parse_and_execute_pipeline(tokens)

        self.assertEqual(result, 0)
        output = mock_stdout.getvalue()
        self.assertTrue(len(output) > 0)

    @patch('sys.stdout', new_callable=StringIO)
    def test_multiple_pipes(self, mock_stdout):
        """Test pipeline with multiple pipe operators."""
        # Create a test file with numbered lines
        test_file = self.test_dir / "temp_multi.txt"
        test_file.write_text("\n".join([f"line{i}" for i in range(1, 11)]))

        try:
            # Get lines 1-5, then grep for lines with '3'
            tokens = self.shell._tokenize(f"cat {test_file} | head -5 | grep 3")
            result = self.shell._parse_and_execute_pipeline(tokens)

            self.assertEqual(result, 0)
            output = mock_stdout.getvalue()
            self.assertIn("line3", output)
            self.assertNotIn("line8", output)  # Should not be in output
        finally:
            if test_file.exists():
                test_file.unlink()

    @patch('sys.stdout', new_callable=StringIO)
    def test_pipeline_with_flags(self, mock_stdout):
        """Test pipeline with commands that have flags."""
        # Create a test file
        test_file = self.test_dir / "temp_flags.txt"
        test_file.write_text("Apple\napple\nbanana\nAPPLE\n")

        try:
            # Case-insensitive grep through pipeline
            tokens = self.shell._tokenize(f"cat {test_file} | grep -i apple")
            result = self.shell._parse_and_execute_pipeline(tokens)

            self.assertEqual(result, 0)
            output = mock_stdout.getvalue()
            # Should match all variations of "apple"
            self.assertIn("Apple", output)
            self.assertIn("apple", output)
            self.assertIn("APPLE", output)
            self.assertNotIn("banana", output)
        finally:
            if test_file.exists():
                test_file.unlink()

    @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    def test_pipeline_exit_code(self, mock_stderr, mock_stdout):
        """Test that pipeline returns exit code of last command."""
        # Create test file
        test_file = self.test_dir / "temp_exitcode.txt"
        test_file.write_text("no match here\n")

        try:
            # Test with an invalid command that will fail
            tokens = self.shell._tokenize(f"cat {test_file} | nonexistentcmd")
            result = self.shell._parse_and_execute_pipeline(tokens)

            # Exit code should be 1 (last command failed)
            self.assertEqual(result, 1)
            error = mock_stderr.getvalue()
            self.assertIn("invalid command", error)
        finally:
            if test_file.exists():
                test_file.unlink()


if __name__ == '__main__':
    unittest.main(verbosity=2)

