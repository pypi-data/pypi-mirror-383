"""
cat command implementation - Concatenate and display file contents
Pure Python implementation with -n, -b, -s, -h, --help options
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import ArgumentParser, resolve_path


def run(args, shell):
    """
    Concatenate and display file contents
    Usage: cat [-n] [-b] [-s] [-h | --help] [file]...

    Options:
        -n, --number          Number all output lines
        -b, --number-nonblank Number nonempty output lines, overrides -n
        -s, --squeeze-blank   Suppress repeated empty output lines
        -h, --help            Display this help message and exit

    Read FILE(s) and output them to standard output.
    If no FILE is specified, or if FILE is -, read from standard input.

    Note: Use shell redirection operators (>, >>) for output redirection:
        cat file.txt > output.txt
        cat file.txt >> output.txt
    """
    parser = ArgumentParser(args)
    current_dir = shell.current_dir

    # Check for help flag
    if parser.has_flag('h') or parser.has_flag('help'):
        print_help()
        return 0

    # Check for number lines flag (-n or --number)
    number_lines = parser.has_flag('n') or parser.has_flag('number')

    # Check for number non-blank lines flag (-b or --number-nonblank)
    number_nonblank = parser.has_flag('b') or parser.has_flag('number-nonblank')

    # Check for squeeze blank lines flag (-s or --squeeze-blank)
    squeeze_blank = parser.has_flag('s') or parser.has_flag('squeeze-blank')

    try:
        # Validate flags - check if any switch is present but has an invalid option value
        boolean_flags = {'n', 'number', 'b', 'number-nonblank', 's', 'squeeze-blank'}
        parser.validate_flags(boolean_flags)
    except ValueError as e:
        print(f"cat: {e}", file=sys.stderr)
        return 1

    # Get files from positional arguments
    files = parser.positional

    # Default to stdin if no files specified
    if not files:
        files = ['-']

    # Process each file
    all_lines = []
    for file_path in files:
        try:
            if file_path == '-':
                # Read from stdin
                lines = read_stdin()
            else:
                # Read from file
                target_path = resolve_path(file_path, current_dir)
                lines = read_file_lines(target_path)

            all_lines.extend(lines)
        except Exception as e:
            print(f"cat: {file_path}: {e}", file=sys.stderr)
            return 1

    # Display output (redirection is handled by shell pipeline)
    try:
        display_lines(all_lines, number_lines, number_nonblank, squeeze_blank)
    except Exception as e:
        print(f"cat: {e}", file=sys.stderr)
        return 1

    return 0


def read_file_lines(file_path):
    """
    Read lines from a file

    Args:
        file_path: Path object to the file

    Returns:
        List of lines from the file
    """
    if not file_path.exists():
        raise FileNotFoundError(f"No such file or directory")

    if not file_path.is_file():
        raise IsADirectoryError(f"Is a directory")

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.readlines()
    except PermissionError:
        raise PermissionError(f"Permission denied")


def read_stdin():
    """
    Read lines from stdin

    Returns:
        List of lines from stdin
    """
    try:
        return sys.stdin.readlines()
    except KeyboardInterrupt:
        print()  # Print newline on Ctrl+C
        return []


def display_lines(lines, number_lines=False, number_nonblank=False, squeeze_blank=False):
    """
    Display lines with appropriate formatting

    Args:
        lines: List of lines to display
        number_lines: Whether to number all lines
        number_nonblank: Whether to number non-blank lines only
        squeeze_blank: Whether to squeeze multiple blank lines
    """
    line_number = 1
    last_was_blank = False

    for line in lines:
        # Remove trailing newline for processing
        original_line = line.rstrip('\n\r')
        is_blank = not original_line.strip()

        # Handle squeeze blank lines
        if squeeze_blank and is_blank and last_was_blank:
            continue

        # Determine if we should number this line
        should_number = False
        if number_nonblank and not is_blank:
            should_number = True
        elif number_lines and not number_nonblank:
            should_number = True

        # Display the line
        if should_number:
            print(f"{line_number:6d}\t{original_line}")
            if not is_blank or not number_nonblank:
                line_number += 1
        else:
            print(original_line)
            if not is_blank or not number_nonblank:
                line_number += 1

        last_was_blank = is_blank


def print_help():
    """Print detailed help message for cat command"""
    help_text = """cat - concatenate and display file contents

Usage: cat [OPTION]... [FILE]...

Concatenate FILE(s) to standard output.

Options:
  -n, --number          number all output lines
  -b, --number-nonblank number nonempty output lines, overrides -n
  -s, --squeeze-blank   suppress repeated empty output lines
  -h, --help            display this help and exit

With no FILE, or when FILE is -, read standard input.

Examples:
  cat file.txt                    Display contents of file.txt
  cat file1.txt file2.txt         Display contents of multiple files
  cat -n file.txt                 Display with line numbers
  cat -b file.txt                 Display with line numbers (non-blank only)
  cat -s file.txt                 Display with squeezed blank lines
  cat -                           Read from standard input
  cat file.txt | grep pattern     Pipe output to another command
  cat file.txt > output.txt       Redirect output to file (shell redirection)
  cat file.txt >> output.txt      Append output to file (shell redirection)

Pipelines and Redirection:
  Use shell operators for I/O:
    |     Pipe output to another command
    >     Redirect output to file (overwrite)
    >>    Redirect output to file (append)
    <     Redirect input from file

Exit Status:
  Returns 0 if all files were displayed successfully, non-zero otherwise.
"""
    print(help_text)

