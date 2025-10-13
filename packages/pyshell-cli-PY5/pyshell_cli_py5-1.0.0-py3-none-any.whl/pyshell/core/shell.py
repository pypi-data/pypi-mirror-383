#!/usr/bin/env python3
"""
PyShell - A modular UNIX-like shell implementation in Python
Main shell class with core event loop and command dispatcher
"""

import sys
import importlib.util
from pathlib import Path
from typing import List
from .history import CommandHistory
from .pipeline_executor import PipelineExecutor
from utils.parsers import PipelineParser

# Add parent directory to path for utils imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import ArgumentParser


class PyShell:
    """Main shell class implementing the core event loop and command dispatcher"""

    def __init__(self):
        self.current_dir = Path.cwd()
        self.previous_dir = None  # Track previous directory for cd -
        self.commands_dir = Path(__file__).parent.parent / "commands"
        self.builtin_commands = {
            'date': self._cmd_date,
            'whoami': self._cmd_whoami,
            'hostname': self._cmd_hostname,
            'timeit': self._cmd_timeit,
            'exit': self._cmd_exit,
        }

        # Initialize command history (enables up/down arrow navigation)
        self.history = CommandHistory()

        # Ensure commands directory exists
        self.commands_dir.mkdir(exist_ok=True)

    def run(self):
        """Main event loop - accepts user input, tokenizes and evaluates commands"""
        print("PyShell - A modular UNIX-like shell")
        print("Type 'exit' to quit")
        print("(Use Up/Down arrows to navigate command history)")

        while True:
            try:
                # Display prompt using shell's tracked current directory
                current_dir = str(self.current_dir.absolute())
                prompt = f"PyShell {current_dir}> "

                user_input = input(prompt).strip()

                if not user_input:
                    continue

                # Add to history
                self.history.add_command(user_input)

                # Tokenize input
                tokens = self._tokenize(user_input)
                if not tokens:
                    continue

                # Check if input contains pipes or redirections
                # Parse and execute as pipeline
                self._parse_and_execute_pipeline(tokens)

            except KeyboardInterrupt:
                print("\nUse 'exit' to quit PyShell")
            except EOFError:
                print("\nPyShell exited.")
                break

    def _tokenize(self, input_str: str) -> List[str]:
        """Tokenize user input into command and arguments
        Handles quoted strings (both single and double quotes) as single tokens"""
        tokens = []
        current_token = []
        in_quote = None  # Track if we're inside quotes (' or ")
        i = 0

        while i < len(input_str):
            char = input_str[i]

            # Handle quotes
            if char in ('"', "'") and in_quote is None:
                # Start of quoted string
                in_quote = char
                current_token.append(char)
            elif char == in_quote:
                # End of quoted string
                current_token.append(char)
                in_quote = None
            elif char.isspace() and in_quote is None:
                # Space outside quotes - token boundary
                if current_token:
                    tokens.append(''.join(current_token))
                    current_token = []
            else:
                # Regular character or space inside quotes
                current_token.append(char)

            i += 1

        # Add final token if any
        if current_token:
            tokens.append(''.join(current_token))

        return tokens

    def _parse_and_execute_pipeline(self, tokens: List[str]) -> int:
        """
        Parse tokens into pipeline and execute

        Args:
            tokens: List of command tokens

        Returns:
            Exit code
        """
        try:
            # Parse pipeline
            parser = PipelineParser(tokens)
            segments = parser.parse()

            # Execute pipeline
            executor = PipelineExecutor(self)
            return executor.execute(segments)

        except ValueError as e:
            print(f"pyshell: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"pyshell: Unhandled exception: {e}", file=sys.stderr)
            return 1

    def _execute_command(self, tokens: List[str]):
        """Execute a command with given tokens

        Returns:
            bool: True if command was valid and executed, False if command was invalid
        """
        if not tokens:
            return 1

        command = tokens.pop(0)
        args = tokens

        # Check if it's a built-in command (case-sensitive first)
        if command in self.builtin_commands:
            try:
                exit_code = self.builtin_commands[command](args)
                return exit_code
            except Exception as e:
                print(f"*** Unhandled `{type(e).__name__}` exception: {e}", file=sys.stderr)
                return 1
        
        # Check for case-insensitive match with builtin commands
        command_lower = command.lower()
        builtin_matches = [cmd for cmd in self.builtin_commands if cmd.lower() == command_lower]
        if builtin_matches:
            print(f"`{command}` is an invalid command")
            print(f"Did you mean '{builtin_matches[0]}'?")
            return 1

        # Try to load as plugin command
        try:
            exit_code = self._execute_plugin_command(command, args)
            return exit_code
        except FileNotFoundError:
            print(f"`{command}` is an invalid command", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"*** Unhandled `{type(e).__name__}` exception: {e}", file=sys.stderr)
            return 1

    def _execute_plugin_command(self, command: str, args: List[str]):
        """Load and execute a plugin command"""
        plugin_path = self.commands_dir / f"{command}.py"

        if not plugin_path.exists():
            raise FileNotFoundError(f"Command '{command}' not found")

        # Load the module dynamically
        spec = importlib.util.spec_from_file_location(command, plugin_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Failed to load command module '{command}'")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Execute the run function
        if hasattr(module, 'run'):
            exit_code = module.run(args, self)
            return exit_code
        raise AttributeError(f"Command module '{command}' missing run() function")

    # Built-in commands implementation
    def _cmd_date(self, args: List[str]):
        """Built-in date command
        
        Usage: date [-h|--help]
        
        Displays the current date and time.
        """
        parser = ArgumentParser(args)
        
        # Check for help flags
        if parser.has_flag('h') or parser.has_flag('help'):
            self._print_date_help()
            return 0
        
        # Validate flags - date accepts no other flags
        try:
            boolean_flags: set = set()
            parser.validate_flags(boolean_flags)
        except ValueError as e:
            print(f"date: {e}")
            print("Try 'date --help' for more information.")
            return 1
        
        # Check for extra positional arguments
        if parser.positional:
            print(f"date: invalid argument -- '{parser.positional[0]}'")
            print("Try 'date --help' for more information.")
            return 1
        
        import time
        # Get current time in seconds
        current_time = time.time()

        # Convert to local time structure
        local_time = time.localtime(current_time)

        # Format the date string manually (UNIX date format)
        # Format: "Day Mon DD HH:MM:SS YYYY"

        # Day names
        day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        # Month names
        month_names = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        # Get components
        day_name = day_names[local_time.tm_wday]
        month_name = month_names[local_time.tm_mon]
        day = local_time.tm_mday
        hour = local_time.tm_hour
        minute = local_time.tm_min
        second = local_time.tm_sec
        year = local_time.tm_year

        # Format the output string
        date_string = f"{day_name} {month_name} {day:2d} {hour:02d}:{minute:02d}:{second:02d} {year}"

        print(date_string)
        return 0
    
    def _print_date_help(self):
        """Print help for date command"""
        print("""date - display current date and time

Usage: date
       date --help

Displays the current date and time in the format:
  Day Mon DD HH:MM:SS YYYY

Options:
  -h, --help     Display this help and exit

Examples:
  date           Show current date and time""")

    def _cmd_whoami(self, args: List[str]):
        """Built-in whoami command
        
        Usage: whoami [-h|--help]
        
        Displays the current username.
        """
        parser = ArgumentParser(args)
        
        # Check for help flags
        if parser.has_flag('h') or parser.has_flag('help'):
            self._print_whoami_help()
            return 0
        
        # Validate flags - whoami accepts no other flags
        try:
            boolean_flags: set = set()
            parser.validate_flags(boolean_flags)
        except ValueError as e:
            print(f"whoami: {e}")
            print("Try 'whoami --help' for more information.")
            return 1
        
        # Check for extra positional arguments
        if parser.positional:
            print(f"whoami: {parser.positional[0]}: no such user")
            return 1
        
        import getpass
        print(getpass.getuser())
        return 0
    
    def _print_whoami_help(self):
        """Print help for whoami command"""
        print("""whoami - display current username

Usage: whoami
       whoami --help

Displays the username of the current user.

Options:
  -h, --help     Display this help and exit

Examples:
  whoami         Show current username""")

    def _cmd_hostname(self, args: List[str]):
        """Built-in hostname command
        
        Usage: hostname [-h|--help]
        
        Displays the system's hostname.
        """
        parser = ArgumentParser(args)
        
        # Check for help flags
        if parser.has_flag('h') or parser.has_flag('help'):
            self._print_hostname_help()
            return 0
        
        # Validate flags - hostname accepts no other flags
        try:
            boolean_flags: set = set()
            parser.validate_flags(boolean_flags)
        except ValueError as e:
            print(f"hostname: {e}")
            print("Try 'hostname --help' for more information.")
            return 1
        
        # Check for extra positional arguments
        if parser.positional:
            print(f"hostname: invalid argument -- '{parser.positional[0]}'")
            print("Try 'hostname --help' for more information.")
            return 1
        
        import socket
        print(socket.gethostname())
        return 0
    
    def _print_hostname_help(self):
        """Print help for hostname command"""
        print("""hostname - display system hostname

Usage: hostname
       hostname --help

Displays the system's hostname (network name).

Options:
  -h, --help     Display this help and exit

Examples:
  hostname       Show system hostname""")

    def _cmd_timeit(self, args: List[str]):
        """
        Built-in timeit command - measures execution time of other commands
        Usage: timeit <command> [arguments...]

        Examples:
            timeit ls -la
            timeit head -5 file.txt
            timeit pwd
        """
        if not args:
            print("timeit: missing command to time")
            print("Usage: timeit <command> [arguments...]")
            return 1

        import time

        # Get the command to time
        command_to_time = args[0]

        # Start timing
        start_time = time.time()

        command_str = ' '.join(args)

        # Execute the command
        exit_code = self._execute_command(args)

        # Calculate execution time
        end_time = time.time()
        execution_time = end_time - start_time

        # Print results
        if not exit_code:
            print(f"`{command_str}` took {execution_time:.5f} seconds.")
        else:
            print(f"timeit: command `{command_to_time}` failed or not found")
            print(f"Execution time: {execution_time:.5f} seconds.")

        return 0

    def _cmd_exit(self, args: List[str]):
        """
        Built-in exit command
        Usage: exit [exit_code]
        """
        exit_code = 0
        if args:
            try:
                exit_code = int(args[0])
            except ValueError:
                print(f"exit: {args[0]}: numeric argument required")
                exit_code = 2

        print("PyShell exited.")
        sys.exit(exit_code)

    def change_directory(self, new_path: Path):
        """Change the current directory and update tracking"""
        # Store current directory as previous
        self.previous_dir = self.current_dir
        # Update current directory
        self.current_dir = new_path




def main():
    """Entry point for PyShell"""
    shell = PyShell()
    shell.run()


if __name__ == "__main__":
    main()
