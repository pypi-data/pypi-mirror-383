"""
Pipeline Execution Engine for PyShell

This module handles the execution of command pipelines with I/O redirections.
"""

import sys
import io
from pathlib import Path
from typing import List, Tuple, Optional

# Import from utils
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.parsers import CommandSegment
from utils.helpers import resolve_path


class PipelineExecutor:
    """Executes command pipelines with proper I/O redirection"""

    def __init__(self, shell):
        """
        Args:
            shell: Reference to PyShell instance for command execution
        """
        self.shell = shell

    def execute(self, segments: List[CommandSegment]) -> int:
        """
        Execute a pipeline of commands

        Args:
            segments: List of CommandSegment objects

        Returns:
            Exit code of the last command in pipeline
        """
        if not segments:
            return 0

        # Single command - execute with redirections
        if len(segments) == 1:
            exit_code, _ = self._execute_single_command(segments[0], None, False)
            return exit_code

        # Multiple commands - set up pipeline
        return self._execute_pipeline(segments)

    def _execute_single_command(
        self,
        segment: CommandSegment,
        stdin_data: Optional[str],
        pipe_stdout: bool = False
    ) -> Tuple[int, Optional[str]]:
        """
        Execute a single command with redirections

        Args:
            segment: CommandSegment to execute
            stdin_data: Data to provide as stdin (from previous pipe or file)
            pipe_stdout: If True, capture and return stdout for piping

        Returns:
            Tuple of (exit_code, stdout_data)
        """
        # Save original stdin/stdout
        original_stdin = sys.stdin
        original_stdout = sys.stdout

        exit_code = 0
        stdout_data = None

        # Prepare file handles to clean up
        stdin_file = None
        stdout_file = None
        
        # Track if WE created the StringIO for piping
        we_created_stringio = False

        try:
            # Handle input redirection
            if stdin_data is not None:
                # Input from previous pipe or string
                sys.stdin = io.StringIO(stdin_data)
            elif segment.stdin_redirect:
                # Input redirection from file (<)
                input_path = resolve_path(
                    segment.stdin_redirect.target,
                    self.shell.current_dir
                )
                if not input_path.exists():
                    print(f"pyshell: {segment.stdin_redirect.target}: No such file or directory")
                    return 1, None
                stdin_file = open(input_path, 'r', encoding='utf-8', errors='ignore')
                sys.stdin = stdin_file

            # Handle output redirection
            if pipe_stdout:
                # Capture stdout for piping
                sys.stdout = io.StringIO()
                we_created_stringio = True
            elif segment.stdout_redirect:
                # Output redirection to file (> or >>)
                output_path = resolve_path(
                    segment.stdout_redirect.target,
                    self.shell.current_dir
                )
                mode = 'a' if segment.stdout_redirect.type == '>>' else 'w'

                # Create parent directories if needed
                output_path.parent.mkdir(parents=True, exist_ok=True)
                stdout_file = open(output_path, mode, encoding='utf-8')
                sys.stdout = stdout_file

            # Execute the command
            command = segment.tokens[0]
            args = segment.tokens[1:]

            # Check if builtin
            if command in self.shell.builtin_commands:
                try:
                    exit_code = self.shell.builtin_commands[command](args)
                except Exception as e:
                    print(f"*** Unhandled `{type(e).__name__}` exception: {e}", file=sys.stderr)
                    exit_code = 1
            else:
                # Try to load as plugin command
                try:
                    exit_code = self.shell._execute_plugin_command(command, args)
                except FileNotFoundError:
                    print(f"`{command}` is an invalid command", file=sys.stderr)
                    exit_code = 1
                except Exception as e:
                    print(f"*** Unhandled `{type(e).__name__}` exception: {e}", file=sys.stderr)
                    exit_code = 1

            # Capture stdout only if WE created the StringIO for piping
            if we_created_stringio and isinstance(sys.stdout, io.StringIO):
                stdout_data = sys.stdout.getvalue()

        finally:
            # Restore original streams
            sys.stdin = original_stdin
            sys.stdout = original_stdout

            # Close opened files
            if stdin_file:
                stdin_file.close()
            if stdout_file:
                stdout_file.close()

        return exit_code, stdout_data

    def _execute_pipeline(self, segments: List[CommandSegment]) -> int:
        """
        Execute a pipeline of multiple commands

        Args:
            segments: List of CommandSegment objects

        Returns:
            Exit code of last command
        """
        stdin_data = None
        exit_code = 0

        for i, segment in enumerate(segments):
            is_last = i == len(segments) - 1

            # Execute command
            exit_code, stdout_data = self._execute_single_command(
                segment,
                stdin_data,
                pipe_stdout=not is_last
            )

            # For last command, print captured output if any
            if is_last and stdout_data:
                print(stdout_data, end='')

            # Pass stdout to next command as stdin
            stdin_data = stdout_data

            # In Unix/Linux, pipelines continue even if a command fails
            # The exit code of the pipeline is typically that of the last command
            # (unless pipefail is set in bash, which we don't implement here)

        return exit_code
