"""
find command - Search for files and directories by name.

Implementation Details:
- Uses FileTraversal utility from utils.file_ops for directory traversal
- Leverages pathlib for all file system operations
- Pure Python implementation with cross-platform compatibility
- Uses regex pattern matching for flexible file searching
"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.parsers import ArgumentParser
from utils.file_ops import find_files
from utils.helpers import resolve_path


def run(args, shell):
    """
    Find files/directories by name starting from a given path.

    Usage:
        find <start_path> <name>
        find / passwd        (searches from root for 'passwd')
        find . test.txt      (searches from current dir for 'test.txt')

    How it works using find_files utility:
    - Uses find_files() for recursive directory traversal
    - Leverages pathlib for cross-platform compatibility
    - Uses regex pattern matching for flexible file searching
    - Handles permission errors gracefully

    Args:
        args: [start_path, search_name]
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
    # Check for maxdepth option (default is unlimited depth)
    maxdepth = None
    if parser.has_flag('maxdepth'):
        try:
            maxdepth = int(parser.get_flag_value('maxdepth'))
            if maxdepth < 0:
                print("find: -maxdepth: must be non-negative", file=sys.stderr)
                return 1
        except (ValueError, TypeError):
            print("find: -maxdepth: not a valid number", file=sys.stderr)
            return 1

    # Get all arguments (including flags)
    all_args = args

    # Check arguments - need at least 2 arguments after flags
    if len(all_args) < 2:
        print("find: missing arguments", file=sys.stderr)
        print("Usage: find [OPTION]... <path> <name>", file=sys.stderr)
        print("Try 'find --help' for more information.", file=sys.stderr)
        return 1

    # Get the last two arguments as path and name
    start_path = all_args[-2]
    search_name = all_args[-1]

    # Strip quotes from search name if present
    if search_name.startswith('"') and search_name.endswith('"'):
        search_name = search_name[1:-1]
    elif search_name.startswith("'") and search_name.endswith("'"):
        search_name = search_name[1:-1]

    # Resolve path (handles ~, relative paths, etc.)
    start_path = str(resolve_path(start_path, Path(current_dir)))

    # Check if start path exists
    try:
        Path(start_path).stat()
    except FileNotFoundError:
        print(f"find: {start_path}: No such file or directory", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"find: {start_path}: {e}", file=sys.stderr)
        return 1
    # Convert shell glob pattern to regex pattern
    import re
    # Escape special regex characters except * and ?
    pattern = re.escape(search_name)
    # Convert shell glob patterns to regex
    pattern = pattern.replace(r'\*', '.*').replace(r'\?', '.')
    # Add end anchor to ensure exact match (e.g., *.py should not match *.pyc)
    pattern = pattern + '$'
    # Use FileTraversal utility for search
    try:
        start_path_obj = Path(start_path)
        found_any = False

        for item in find_files(start_path_obj, pattern, case_sensitive=True, maxdepth=maxdepth):
            print(str(item))
            found_any = True

        # If no files/directories were found, show a helpful message
        if not found_any:
            print(f"find: no matches for '{search_name}' found in '{start_path}'", file=sys.stderr)

    except PermissionError as e:
        # Handle permission errors gracefully
        if found_any:
            # If we found some files before hitting permission error, show them and continue
            print(f"find: {e}", file=sys.stderr)
            return 0  # Return success since we found files
        # If no files found due to permission error
        print(f"find: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"find: {e}", file=sys.stderr)
        return 1

    return 0


def print_help():
    """Print detailed help message for find command"""
    help_text = """find - search for files in a directory hierarchy

Usage: find [OPTION]... PATH NAME

Search for files and directories by name starting from PATH.

Options:
  -maxdepth N        descend at most N levels of directories
  -h, --help         display this help and exit

Examples:
  find . "*.py"                     Search for Python files recursively
  find -maxdepth 1 . "*.txt"        Search for text files in current directory only
  find / passwd                     Search for 'passwd' starting from root
  find . test.txt                   Search for 'test.txt' in current directory
  find ~/Documents "*.txt"          Search for .txt files in Documents
  find /usr/bin python              Search for 'python' in /usr/bin
  find -maxdepth 2 . "*.py"         Search for Python files up to 2 levels deep

Exit Status:
  Returns 0 if successful, 1 if an error occurs.
"""
    print(help_text)
