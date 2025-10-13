"""
tail command - Display the last N lines of a file.

Implementation Details:
- Uses collections.deque with maxlen for efficient sliding window
- deque automatically maintains only the last N items (memory efficient)
- Default: shows last 10 lines if -n not specified
- For small files: reads all lines, for large files: keeps only last N in memory
"""

from collections import deque
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.parsers import ArgumentParser


def run(args, shell):
    """
    Display the last N lines of one or more files.

    Usage:
        tail filename
        tail -n 5 filename
        tail -1 filename  (shorthand for -n 1)

    How it works:
    - Uses a deque (double-ended queue) with fixed max length
    - As we read lines, deque automatically removes oldest lines
    - This keeps memory usage constant regardless of file size

    Args:
        args: Command arguments (flags and filenames)
        current_dir: Current directory path for relative path resolution

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = ArgumentParser(args)
    current_dir = shell.current_dir

    # Check for help flags
    if parser.has_flag('h') or parser.has_flag('help'):
        print_help()
        return 0

    # Default number of lines to display
    num_lines = 10

    # Get number of lines from -n flag or shorthand -NUM
    if parser.has_flag('n'):
        flag_value = parser.get_flag_value('n')
        if flag_value is True:
            print("tail: option requires an argument -- n", file=sys.stderr)
            return 1
        try:
            num_lines = int(flag_value)
        except ValueError:
            print(f"tail: invalid number of lines: '{flag_value}'", file=sys.stderr)
            return 1
    else:
        # Check for shorthand -NUM in flags (e.g., -3, -10)
        for flag_key in parser.flags:
            if flag_key.isdigit():
                num_lines = int(flag_key)
                break

    # Get files from positional arguments
    files = parser.positional

    # Check if files were provided, if not, read from stdin
    if not files:
        files = ['-']

    # Handle zero lines case
    if num_lines == 0:
        return 0

    # Process each file
    exit_code = 0
    show_headers = len(files) > 1 and files != ['-']

    for idx, filepath in enumerate(files):
        # Show header if multiple files
        if show_headers:
            if idx > 0:
                print()  # Blank line between files
            print(f"==> {filepath} <==")

        # Check if reading from stdin
        if filepath == '-':
            try:
                # deque with maxlen automatically keeps only last N items
                last_lines = deque(maxlen=num_lines)

                # Read all lines from stdin
                for line in sys.stdin:
                    last_lines.append(line)

                # Print the collected lines
                for line in last_lines:
                    print(line, end='')
            except KeyboardInterrupt:
                print()  # Print newline on Ctrl+C
                return 130
        else:
            # Resolve relative paths using current directory
            file_path = Path(filepath)
            if not file_path.is_absolute():
                file_path = Path(current_dir) / filepath
            else:
                file_path = Path(filepath)

            try:
                # Open file and collect last N lines
                with open(file_path, 'r') as f:
                    # deque with maxlen automatically keeps only last N items
                    # This is memory efficient - no matter how big the file is,
                    # we only keep N lines in memory
                    last_lines: deque = deque(maxlen=num_lines)

                    # Read all lines, but deque keeps only the last N
                    for line in f:
                        last_lines.append(line)

                    # Print the collected lines
                    for line in last_lines:
                        print(line, end='')

            except FileNotFoundError:
                print(f"tail: {filepath}: No such file or directory", file=sys.stderr)
                exit_code = 1
            except PermissionError:
                print(f"tail: {filepath}: Permission denied", file=sys.stderr)
                exit_code = 1
            except IsADirectoryError:
                print(f"tail: {filepath}: Is a directory", file=sys.stderr)
                exit_code = 1
            except Exception as e:
                print(f"tail: {filepath}: {e}", file=sys.stderr)
                exit_code = 1

    return exit_code


def print_help():
    """Print detailed help message for tail command"""
    help_text = """tail - output the last part of files

Usage: tail [OPTION]... [FILE]...

Print the last 10 lines of each FILE to standard output.
With more than one FILE, precede each with a header giving the file name.
With no FILE, or when FILE is -, read standard input.

Options:
  -n, --lines=NUMBER    output the last NUMBER lines instead of last 10
  -NUMBER               same as -n NUMBER
  -h, --help            display this help and exit

Examples:
  tail file.txt                    Print last 10 lines of file.txt
  tail -n 5 file.txt               Print last 5 lines of file.txt
  tail -1 file.txt                 Print last 1 line of file.txt
  tail file1.txt file2.txt         Print last 10 lines of each file
  cat file.txt | tail -5           Print last 5 lines from piped input

Exit Status:
  Returns 0 if successful, 1 if an error occurs.
"""
    print(help_text)
