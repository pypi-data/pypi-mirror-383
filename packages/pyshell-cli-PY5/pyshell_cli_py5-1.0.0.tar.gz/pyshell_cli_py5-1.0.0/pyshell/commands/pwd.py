"""
pwd command implementation - Print working directory
Pure Python implementation with -L and -P options
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import ArgumentParser


def run(args, shell):
    """
    Print the current working directory
    Usage: pwd [-L | -P] [-h | --help]

    Options:
        -L, --logical   Print the logical current working directory (default)
                        Displays the path with symbolic links preserved
        -P, --physical  Print the physical current working directory
                        Resolves all symbolic links to show actual path
        -h, --help      Display this help message and exit

    The pwd command prints the absolute pathname of the current working directory.
    By default, it prints the logical path (with symbolic links intact).
    """
    parser = ArgumentParser(args)
    current_dir = shell.current_dir

    # Check for help flag
    if parser.has_flag('h') or parser.has_flag('help'):
        print_help()
        return 0

    # Check for physical flag (-P)
    physical = parser.has_flag('P') or parser.has_flag('physical')

    # Check for logical flag (-L)
    logical = parser.has_flag('L') or parser.has_flag('logical')

    try:
        # Validate flags - check if any switch is present but has an invalid option value
        boolean_flags = {'P', 'physical', 'L', 'logical'}
        parser.validate_flags(boolean_flags)
    except ValueError as e:
        print(f"pwd: {e}", file=sys.stderr)
        return 1

    # Check if there are any positional arguments
    if parser.positional:
        print("pwd: invalid operand(s) provided", file=sys.stderr)
        print("Try 'pwd--help' for more information.", file=sys.stderr)
        return 1

    # Both -P and -L specified - error
    if physical and logical:
        print("pwd: cannot specify both -P and -L", file=sys.stderr)
        return 1

    # Get the current directory path
    if physical:
        # Physical path - resolve all symbolic links
        try:
            # Use resolve() to get the real path with symlinks resolved
            real_path = current_dir.resolve()
            print(str(real_path))
        except Exception as e:
            print(f"pwd: error resolving physical path: {e}", file=sys.stderr)
            return 1
    else:
        # Logical path (default) - preserve symbolic links
        # Just use the absolute path without resolving symlinks
        print(str(current_dir.absolute()))

    return 0


def print_help():
    """Print detailed help message for pwd command"""
    help_text = """pwd - print working directory

Usage: pwd [OPTION]...

Print the full filename of the current working directory.

Options:
  -L, --logical   print the value of $PWD if it names the current working
                  directory (this is the default behavior)
  -P, --physical  print the physical directory, without any symbolic links
  -h, --help      display this help and exit

By default, pwd behaves as if -L was specified.

Examples:
  pwd           Print the current working directory (logical path)
  pwd -L        Print the logical current working directory
  pwd -P        Print the physical current working directory (resolve symlinks)

Exit Status:
  Returns 0 unless an invalid option is given or the current directory
  cannot be read.
"""
    print(help_text)
