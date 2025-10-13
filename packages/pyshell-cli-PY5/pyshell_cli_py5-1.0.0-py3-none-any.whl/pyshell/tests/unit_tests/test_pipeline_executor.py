#!/usr/bin/env python3
"""
Unit tests for PipelineExecutor
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

from core.pipeline_executor import PipelineExecutor
from utils.parsers import CommandSegment, Redirection
import shutil


class TestPipelineExecutor(unittest.TestCase):
    """Test cases for PipelineExecutor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())

        # Create a mock shell object
        self.mock_shell = MagicMock()
        self.mock_shell.current_dir = self.test_dir
        self.mock_shell.builtin_commands = {}
        self.mock_shell._execute_plugin_command = MagicMock(return_value=0)

        self.executor = PipelineExecutor(self.mock_shell)

    def tearDown(self):
        """Clean up test fixtures."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_execute_empty_segments(self):
        """Test executing empty segment list."""
        result = self.executor.execute([])
        self.assertEqual(result, 0)

    def test_execute_single_command(self):
        """Test executing a single command."""
        segment = CommandSegment(tokens=['test_cmd', 'arg1'])
        segment.stdin_redirect = None
        segment.stdout_redirect = None

        result = self.executor.execute([segment])

        # Should call _execute_plugin_command
        self.mock_shell._execute_plugin_command.assert_called_once_with('test_cmd', ['arg1'])

    @patch('sys.stdout', new_callable=StringIO)
    def test_execute_builtin_command(self, mock_stdout):
        """Test executing a builtin command."""
        def mock_date(args):
            print("Test Date")
            return 0

        self.mock_shell.builtin_commands['date'] = mock_date

        segment = CommandSegment(tokens=['date'])
        segment.stdin_redirect = None
        segment.stdout_redirect = None

        result = self.executor.execute([segment])

        self.assertEqual(result, 0)
        self.assertIn("Test Date", mock_stdout.getvalue())

    @patch('sys.stderr', new_callable=StringIO)
    def test_execute_invalid_command(self, mock_stderr):
        """Test executing an invalid command."""
        self.mock_shell._execute_plugin_command.side_effect = FileNotFoundError()

        segment = CommandSegment(tokens=['invalidcmd'])
        segment.stdin_redirect = None
        segment.stdout_redirect = None

        result = self.executor.execute([segment])

        self.assertEqual(result, 1)
        self.assertIn("invalid command", mock_stderr.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_pipeline_two_commands(self, mock_stdout):
        """Test executing a pipeline with two commands."""
        # Mock commands that read from stdin and write to stdout
        def mock_cmd1(args):
            print("Line 1\nLine 2\nLine 3")
            return 0

        def mock_cmd2(args):
            for line in sys.stdin:
                if 'Line 2' in line:
                    print(line.strip())
            return 0

        self.mock_shell._execute_plugin_command.side_effect = [0, 0]

        # Create a more sophisticated mock that executes actual logic
        original_execute = self.mock_shell._execute_plugin_command

        def execute_side_effect(cmd, args):
            if cmd == 'cmd1':
                return mock_cmd1(args)
            elif cmd == 'cmd2':
                return mock_cmd2(args)
            return 0

        self.mock_shell._execute_plugin_command = execute_side_effect

        segment1 = CommandSegment(tokens=['cmd1'])
        segment1.stdin_redirect = None
        segment1.stdout_redirect = None
        segment2 = CommandSegment(tokens=['cmd2'])
        segment2.stdin_redirect = None
        segment2.stdout_redirect = None

        result = self.executor.execute([segment1, segment2])

        self.assertEqual(result, 0)

    def test_pipeline_continues_after_failure(self):
        """Test that pipeline continues even if a command fails (Unix behavior)."""
        # First command fails, second command should still execute
        self.mock_shell._execute_plugin_command.side_effect = [1, 0]

        segment1 = CommandSegment(tokens=['failing_cmd'])
        segment1.stdin_redirect = None
        segment1.stdout_redirect = None
        segment2 = CommandSegment(tokens=['working_cmd'])
        segment2.stdin_redirect = None
        segment2.stdout_redirect = None

        result = self.executor.execute([segment1, segment2])

        # Exit code should be from the last command (0)
        self.assertEqual(result, 0)
        # Both commands should have been called
        self.assertEqual(self.mock_shell._execute_plugin_command.call_count, 2)

    def test_output_redirection_overwrite(self):
        """Test output redirection with > operator."""
        def mock_cmd(cmd, args):
            print("Test output")
            return 0

        self.mock_shell._execute_plugin_command = mock_cmd

        output_file = self.test_dir / "output.txt"
        segment = CommandSegment(tokens=['test_cmd'])
        segment.stdin_redirect = None
        segment.stdout_redirect = Redirection('>', 'output.txt')

        result = self.executor.execute([segment])

        self.assertEqual(result, 0)
        self.assertTrue(output_file.exists())
        content = output_file.read_text()
        self.assertIn("Test output", content)

    def test_output_redirection_append(self):
        """Test output redirection with >> operator."""
        output_file = self.test_dir / "output.txt"
        output_file.write_text("Existing content\n")

        def mock_cmd(cmd, args):
            print("New content")
            return 0

        self.mock_shell._execute_plugin_command = mock_cmd

        segment = CommandSegment(tokens=['test_cmd'])
        segment.stdin_redirect = None
        segment.stdout_redirect = Redirection('>>', 'output.txt')

        result = self.executor.execute([segment])

        self.assertEqual(result, 0)
        content = output_file.read_text()
        self.assertIn("Existing content", content)
        self.assertIn("New content", content)

    def test_input_redirection(self):
        """Test input redirection with < operator."""
        input_file = self.test_dir / "input.txt"
        input_file.write_text("Test input line")

        def mock_cmd(cmd, args):
            line = sys.stdin.readline()
            print(f"Read: {line.strip()}")
            return 0

        self.mock_shell._execute_plugin_command = mock_cmd

        segment = CommandSegment(tokens=['test_cmd'])
        segment.stdin_redirect = Redirection('<', 'input.txt')
        segment.stdout_redirect = None

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            result = self.executor.execute([segment])

            self.assertEqual(result, 0)
            self.assertIn("Read: Test input line", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_input_redirection_file_not_found(self, mock_stdout):
        """Test input redirection with non-existent file."""
        segment = CommandSegment(tokens=['test_cmd'])
        segment.stdin_redirect = Redirection('<', 'nonexistent.txt')
        segment.stdout_redirect = None

        result = self.executor.execute([segment])

        self.assertEqual(result, 1)
        output = mock_stdout.getvalue()
        self.assertIn("No such file or directory", output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_builtin_command_exception(self, mock_stderr):
        """Test builtin command raising an exception."""
        def failing_builtin(args):
            raise ValueError("Test error")

        self.mock_shell.builtin_commands['failing'] = failing_builtin

        segment = CommandSegment(tokens=['failing'])
        segment.stdin_redirect = None
        segment.stdout_redirect = None

        result = self.executor.execute([segment])

        self.assertEqual(result, 1)
        self.assertIn("ValueError", mock_stderr.getvalue())

    @patch('sys.stderr', new_callable=StringIO)
    def test_plugin_command_exception(self, mock_stderr):
        """Test plugin command raising an exception."""
        self.mock_shell._execute_plugin_command.side_effect = RuntimeError("Test error")

        segment = CommandSegment(tokens=['test_cmd'])
        segment.stdin_redirect = None
        segment.stdout_redirect = None

        result = self.executor.execute([segment])

        self.assertEqual(result, 1)
        self.assertIn("RuntimeError", mock_stderr.getvalue())

    def test_pipeline_with_stdin_data(self):
        """Test executing pipeline with stdin data."""
        def mock_cmd(cmd, args):
            # Read from stdin and count lines
            lines = sys.stdin.readlines()
            print(f"Received {len(lines)} lines")
            return 0

        self.mock_shell._execute_plugin_command = mock_cmd

        segment = CommandSegment(tokens=['test_cmd'])
        segment.stdin_redirect = None
        segment.stdout_redirect = None

        stdin_data = "Line 1\nLine 2\nLine 3\n"

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            exit_code, stdout_data = self.executor._execute_single_command(
                segment, stdin_data, pipe_stdout=False
            )

            self.assertEqual(exit_code, 0)
            self.assertIn("Received 3 lines", mock_stdout.getvalue())

    def test_pipeline_capture_stdout(self):
        """Test capturing stdout for piping."""
        def mock_cmd(cmd, args):
            print("Output line 1")
            print("Output line 2")
            return 0

        self.mock_shell._execute_plugin_command = mock_cmd

        segment = CommandSegment(tokens=['test_cmd'])
        segment.stdin_redirect = None
        segment.stdout_redirect = None

        exit_code, stdout_data = self.executor._execute_single_command(
            segment, None, pipe_stdout=True
        )

        self.assertEqual(exit_code, 0)
        self.assertIn("Output line 1", stdout_data)
        self.assertIn("Output line 2", stdout_data)

    def test_output_redirection_creates_directories(self):
        """Test that output redirection creates parent directories."""
        def mock_cmd(cmd, args):
            print("Test content")
            return 0

        self.mock_shell._execute_plugin_command = mock_cmd

        # Use nested path that doesn't exist
        output_path = "subdir1/subdir2/output.txt"
        segment = CommandSegment(tokens=['test_cmd'])
        segment.stdin_redirect = None
        segment.stdout_redirect = Redirection('>', output_path)

        result = self.executor.execute([segment])

        self.assertEqual(result, 0)
        full_path = self.test_dir / output_path
        self.assertTrue(full_path.exists())
        self.assertIn("Test content", full_path.read_text())

    @patch('sys.stdout', new_callable=StringIO)
    @patch('sys.stderr', new_callable=StringIO)
    def test_error_goes_to_stderr_not_piped(self, mock_stderr, mock_stdout):
        """Test that errors go to stderr and are not piped to next command."""
        # First command fails and writes to stderr
        def failing_cmd(args):
            print("Error message", file=sys.stderr)
            return 1

        # Second command reads from stdin (should be empty)
        def reading_cmd(args):
            lines = sys.stdin.readlines()
            print(f"Received {len(lines)} lines")
            return 0

        call_count = [0]
        def execute_side_effect(cmd, args):
            call_count[0] += 1
            if call_count[0] == 1:
                return failing_cmd(args)
            else:
                return reading_cmd(args)

        self.mock_shell._execute_plugin_command = execute_side_effect

        segment1 = CommandSegment(tokens=['failing'])
        segment1.stdin_redirect = None
        segment1.stdout_redirect = None
        segment2 = CommandSegment(tokens=['reading'])
        segment2.stdin_redirect = None
        segment2.stdout_redirect = None

        result = self.executor.execute([segment1, segment2])

        # Error should be in stderr
        self.assertIn("Error message", mock_stderr.getvalue())
        # Second command should receive 0 lines (error not piped)
        self.assertIn("Received 0 lines", mock_stdout.getvalue())


class TestPipelineExecutorIntegration(unittest.TestCase):
    """Integration tests for PipelineExecutor with real shell."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())

        # Import actual PyShell for integration testing
        from core.shell import PyShell
        self.shell = PyShell()
        self.shell.current_dir = self.test_dir

        self.executor = PipelineExecutor(self.shell)

    def tearDown(self):
        """Clean up test fixtures."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch('sys.stdout', new_callable=StringIO)
    def test_real_builtin_command(self, mock_stdout):
        """Test executing real builtin command."""
        segment = CommandSegment(tokens=['date'])
        segment.stdin_redirect = None
        segment.stdout_redirect = None

        result = self.executor.execute([segment])

        self.assertEqual(result, 0)
        # Date command should output something
        self.assertTrue(len(mock_stdout.getvalue()) > 0)

    def test_real_file_operations(self):
        """Test real file I/O operations."""
        # Create input file
        input_file = self.test_dir / "input.txt"
        input_file.write_text("Test content\n")

        # Create output file through redirection
        segment = CommandSegment(tokens=['cat', 'input.txt'])
        segment.stdin_redirect = None
        segment.stdout_redirect = Redirection('>', 'output.txt')

        result = self.executor.execute([segment])

        self.assertEqual(result, 0)
        output_file = self.test_dir / "output.txt"
        self.assertTrue(output_file.exists())
        self.assertEqual(output_file.read_text().strip(), "Test content")


if __name__ == '__main__':
    unittest.main(verbosity=2)

