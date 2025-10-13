"""
head command - Display the first N lines of a file.

Implementation Details:
- Uses Python's built-in file operations (open, readline)
- Reads file line by line to avoid loading entire file into memory
- Default: shows first 10 lines if -n not specified
- Handles multiple files (shows header for each file)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.parsers import ArgumentParser


def run(args, shell):
    """
    Display the first N lines of one or more files.

    Usage:
        head filename
        head -n 5 filename
        head -3 filename  (shorthand for -n 3)

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
            print("head: option requires an argument -- n", file=sys.stderr)
            return 1
        try:
            num_lines = int(flag_value)
        except ValueError:
            print(f"head: invalid number of lines: '{flag_value}'", file=sys.stderr)
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
                lines_read = 0
                for line in sys.stdin:
                    if lines_read >= num_lines:
                        break
                    print(line, end='')
                    lines_read += 1
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
                # Open file and read first N lines
                # We use 'with' to ensure file is properly closed
                with open(file_path, 'r') as f:
                    lines_read = 0

                    # Read line by line (memory efficient)
                    for line in f:
                        if lines_read >= num_lines:
                            break
                        # Print without adding extra newline (line already has one)
                        print(line, end='')
                        lines_read += 1

            except FileNotFoundError:
                print(f"head: {filepath}: No such file or directory", file=sys.stderr)
                exit_code = 1
            except PermissionError:
                print(f"head: {filepath}: Permission denied", file=sys.stderr)
                exit_code = 1
            except IsADirectoryError:
                print(f"head: {filepath}: Is a directory", file=sys.stderr)
                exit_code = 1
            except Exception as e:
                print(f"head: {filepath}: {e}", file=sys.stderr)
                exit_code = 1

    return exit_code


def print_help():
    """Print help information for head command"""
    print("""Usage: head [options] [file...]

Print the first 10 lines of each FILE to standard output.
With more than one FILE, precede each with a header giving the file name.
With no FILE, or when FILE is -, read standard input.

Options:
    -n, --lines=NUMBER    print first NUMBER lines instead of first 10
    -h, --help            display this help and exit

Examples:
    head file.txt         Print first 10 lines of file.txt
    head -n 5 file.txt    Print first 5 lines of file.txt
    head -3 file.txt      Print first 3 lines of file.txt (shorthand)
    head file1 file2      Print first 10 lines of both files
    cat file.txt | head -5    Print first 5 lines from piped input""")
