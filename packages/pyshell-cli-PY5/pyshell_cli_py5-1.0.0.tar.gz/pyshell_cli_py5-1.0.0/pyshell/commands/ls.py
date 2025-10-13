"""
ls command implementation - List directory contents
Supports -R/--recursive flag for recursive listing
"""

import sys
from pathlib import Path
from typing import Dict, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import ArgumentParser, list_directory, format_file_listing, resolve_path


def run(args, shell):
    """
    List directory contents
    Usage: ls [options] [directory]
    Options:
        -R, --recursive    List subdirectories recursively
        -f, --force        Ignore errors and continue
        -h, --help         Show this help message
    """
    parser = ArgumentParser(args)
    current_dir = shell.current_dir

    # Check for help flags
    if parser.has_flag('h') or parser.has_flag('help'):
        print_help()
        return 0

    # Check for force flag (-f or --force)
    force = parser.has_flag('f') or parser.has_flag('force')

    try:
        # Validate flags - check if any switch is present but has an invalid option value
        boolean_flags = {'R', 'recursive', 'f', 'force'}
        parser.validate_flags(boolean_flags)
    except ValueError as e:
        print(f"ls: {e}", file=sys.stderr)
        return 1

    # Get target directory
    target_path = parser.get_positional(0, '.')
    if target_path == '.':
        target = current_dir
    else:
        target = resolve_path(target_path, current_dir)

    # Check for recursive flag
    recursive = parser.has_flag('R') or parser.has_flag('recursive')

    # Track exit code - start with 0 (success), set to 1 if any errors occur
    exit_code = 0

    try:
        if target.is_file():
            # If target is a file, just print its name
            print(target.name)
            return 0

        # List directory contents
        items = list(list_directory(target, recursive=recursive))

        if not items:
            return 0  # Empty directory

        if recursive:
            # Group items by directory for recursive listing
            dirs: Dict[Path, List[Path]] = {}
            for item in items:
                parent = item.parent
                if parent not in dirs:
                    dirs[parent] = []
                dirs[parent].append(item)

            # Sort directories
            sorted_dirs = sorted(dirs.keys(), key=str)

            for i, dir_path in enumerate(sorted_dirs):
                if i > 0:
                    print()  # Empty line between directories

                # Print directory header (except for current directory)
                if dir_path != target:
                    print(f"{dir_path}:")

                # Sort items in this directory
                dir_items = sorted(dirs[dir_path], key=lambda x: (x.is_file(), x.name.lower()))

                # Print items
                names = [format_file_listing(item) for item in dir_items if item.parent == dir_path]
                if names:
                    print(' '.join(names))
        else:
            # Non-recursive listing
            # Sort items: directories first, then files, both alphabetically
            sorted_items = sorted(items, key=lambda x: (x.is_file(), x.name.lower()))

            # Format and print
            names = [format_file_listing(item) for item in sorted_items]
            if names:
                print(' '.join(names))

        return 0

    except FileNotFoundError:
        if not force:
            print(f"ls: cannot access '{target_path}': No such file or directory", file=sys.stderr)
        exit_code = 1
    except PermissionError:
        if not force:
            print(f"ls: cannot open directory '{target_path}': Permission denied", file=sys.stderr)
        exit_code = 1
    except Exception as e:
        if not force:
            print(f"ls: cannot access '{target_path}': {e}", file=sys.stderr)
        exit_code = 1

    return exit_code


def print_help():
    """Print help information for ls command"""
    print("""Usage: ls [options] [directory]

List directory contents.

Options:
    -R, --recursive    List subdirectories recursively
    -f, --force        Ignore errors and continue
    -h, --help         Show this help message

Examples:
    ls                  List current directory contents
    ls /home            List contents of /home directory
    ls -R               List current directory recursively
    ls --recursive /tmp List /tmp directory recursively
    ls -f /nonexistent  Ignore errors when accessing /nonexistent

Exit Status:
    Returns 0 if all operations were successful, non-zero otherwise.""")
