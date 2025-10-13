"""
clear command - Clear the terminal screen.

Implementation Details:
- Pure Python implementation using ANSI escape sequences
- Cross-platform compatible (works on Unix, macOS, and Windows)
- Supports help flag
- Simple and efficient
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import ArgumentParser


def run(args, shell):
    """
    Clear the terminal screen.

    Usage:
        clear
        clear -h
        clear --help

    Args:
        args: Command arguments (flags only)
        shell: Shell object (unused for clear)

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = ArgumentParser(args)

    # Check for help flags
    if parser.has_flag('h') or parser.has_flag('help'):
        print_help()
        return 0

    # Check if there are any positional arguments
    if parser.positional:
        print("clear: invalid operand(s) provided", file=sys.stderr)
        print("Try 'clear --help' for more information.", file=sys.stderr)
        return 1

    # Clear the screen using ANSI escape sequence
    # This works on most modern terminals
    print('\033[2J\033[H', end='')

    # Alternative method for Windows (if ANSI doesn't work)
    # This is a fallback that works on Windows Command Prompt
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # Unix/Linux/macOS
        os.system('clear')

    return 0


def print_help():
    """Print detailed help message for clear command"""
    help_text = """clear - clear the terminal screen

Usage: clear [OPTION]...

Clear the terminal screen.

Options:
  -h, --help     display this help and exit

Examples:
  clear          Clear the terminal screen
  clear -h       Show this help message

Exit Status:
  Returns 0 if successful, 1 if an error occurs.

Note:
  This command clears the terminal screen and positions the cursor
  at the top-left corner. It works on most modern terminals and
  operating systems.
"""
    print(help_text)
