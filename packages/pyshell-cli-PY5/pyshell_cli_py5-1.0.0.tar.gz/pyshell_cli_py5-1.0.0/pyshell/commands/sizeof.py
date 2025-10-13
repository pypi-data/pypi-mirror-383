"""
sizeof command - Print size of a file in bytes.

Implementation Details:
- Uses pathlib.Path for modern object-oriented path handling
- Path.stat().st_size gets file size from filesystem metadata
- Doesn't read file content, just metadata (efficient)
- pathlib is part of Python standard library
"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.parsers import ArgumentParser


def run(args, shell):
    """
    Print the size of a file in bytes.

    Usage:
        sizeof filename

    How pathlib.Path works:
    - Path(filepath) creates a path object
    - .stat() returns file metadata (like size, timestamps)
    - .st_size is the size in bytes
    - Doesn't read file content, just filesystem metadata

    Args:
        args: Command arguments (filename)
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

    # Check if filename was provided
    if not parser.positional:
        print("sizeof: missing file operand", file=sys.stderr)
        print("Try 'sizeof --help' for more information.", file=sys.stderr)
        return 1

    filepath = parser.positional[0]

    try:
        # Create Path object and resolve relative paths
        path = Path(filepath)
        if not path.is_absolute():
            path = Path(current_dir) / filepath

        # Get file size using .stat().st_size
        # stat() returns file metadata, st_size is size in bytes
        size = path.stat().st_size

        # Print size in bytes (as per requirement)
        print(f"{size} bytes")
        return 0

    except FileNotFoundError:
        print(f"sizeof: {filepath}: No such file or directory", file=sys.stderr)
        return 1
    except PermissionError:
        print(f"sizeof: {filepath}: Permission denied", file=sys.stderr)
        return 1
    except IsADirectoryError:
        print(f"sizeof: {filepath}: Is a directory", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"sizeof: {filepath}: {e}", file=sys.stderr)
        return 1


def print_help():
    """Print detailed help message for sizeof command"""
    help_text = """sizeof - print file size in bytes

Usage: sizeof [OPTION]... FILE...

Print the size of each FILE in bytes.

Options:
  -h, --help     display this help and exit

Examples:
  sizeof file.txt                    Print size of file.txt
  sizeof file1.txt file2.txt         Print size of multiple files

Exit Status:
  Returns 0 if successful, 1 if an error occurs.
"""
    print(help_text)
