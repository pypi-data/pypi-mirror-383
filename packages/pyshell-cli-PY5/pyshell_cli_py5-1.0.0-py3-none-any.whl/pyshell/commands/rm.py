"""
rm command implementation - Remove files and directories
Pure Python implementation with -r, -V, and --verbose options
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import ArgumentParser, list_directory, resolve_path


def run(args, shell):
    """
    Remove files or directories
    Usage: rm [-r] [-v | --verbose] [-i | --interactive] [-f | --force] [-h | --help] file...

    Options:
        -r                  Remove directories and their contents recursively
        -v, --verbose       Explain what is being done
        -i, --interactive   Prompt before every removal
        -f, --force         Ignore nonexistent files and arguments, never prompt
        -h, --help          Display this help message and exit

    Remove (unlink) the specified files. With -r option, remove directories
    and their contents recursively.
    """
    parser = ArgumentParser(args)
    current_dir = shell.current_dir

    # Check for help flag
    if parser.has_flag('h') or parser.has_flag('help'):
        print_help()
        return 0

    # Check for recursive flag (-r)
    recursive = parser.has_flag('r') or parser.has_flag('recursive')

    # Check for verbose flag (-v or --verbose)
    verbose = parser.has_flag('v') or parser.has_flag('verbose')

    # Check for interactive flag (-i or --interactive)
    interactive = parser.has_flag('i') or parser.has_flag('interactive')

    # Check for force flag (-f or --force)
    force = parser.has_flag('f') or parser.has_flag('force')

    try:
        # Validate flags - check if any switch is present but has an invalid option value
        boolean_flags = {'r', 'recursive', 'v', 'verbose', 'i', 'interactive', 'f', 'force'}
        parser.validate_flags(boolean_flags)
    except ValueError as e:
        print(f"rm: {e}", file=sys.stderr)
        return 1

    # Get positional arguments (files/directories to remove)
    if not parser.positional:
        print("rm: missing operand", file=sys.stderr)
        print("Try 'rm --help' for more information.", file=sys.stderr)
        return 1

    # Track exit code - start with 0 (success), set to 1 if any errors occur
    exit_code = 0

    # Process each file/directory
    for item in parser.positional:
        # Resolve path
        target_path = resolve_path(item, current_dir)

        try:
            # Only proceed if all flags are properly validated (don't have option value or are not present)
            remove_item(target_path, recursive, verbose, interactive, force)

        except Exception as e:
            if not force:  # Don't print errors in force mode
                print(f"rm: cannot remove '{item}': {e}", file=sys.stderr)
            exit_code = 1

    return exit_code


def remove_item(path, recursive=False, verbose=False, interactive=False, force=False):
    """
    Remove a file or directory

    Args:
        path: Path object to remove
        recursive: Whether to remove directories recursively
        verbose: Whether to print verbose output
        interactive: Whether to prompt before removal
        force: Whether to ignore errors and never prompt
    """
    if not path.exists():
        raise FileNotFoundError("No such file or directory")

    # Interactive mode: prompt before removal
    if interactive and not force:
        response = input(f"rm: remove '{path}'? ")
        if response.lower() not in ['y', 'yes']:
            return  # User declined

    if path.is_file() or path.is_symlink():
        # Remove file or symbolic link
        if verbose:
            print(f"removed '{path}'")
        path.unlink()

    elif path.is_dir():
        if not recursive:
            raise IsADirectoryError("Is a directory (use -r to remove directories)")

        # Remove directory recursively
        remove_directory_recursive(path, verbose, interactive, force)


def remove_directory_recursive(directory, verbose=False, interactive=False, force=False):
    """
    Remove a directory and all its contents using FileTraversal

    Args:
        directory: Path object representing the directory
        verbose: Whether to print verbose output
        interactive: Whether to prompt before removal
        force: Whether to ignore errors and never prompt
    """
    try:
        # Use list_directory to get all items recursively
        # We need to collect all items first, then remove them in reverse order
        # (files first, then directories from deepest to shallowest)
        all_items = list(list_directory(directory, recursive=True, show_hidden=True))

        # Separate files and directories
        files = []
        dirs = []

        for item in all_items:
            if item.is_file() or item.is_symlink():
                files.append(item)
            elif item.is_dir():
                dirs.append(item)

        # Remove files first
        for file_path in files:
            # Interactive mode: prompt for each file
            if interactive and not force:
                response = input(f"rm: remove '{file_path}'? ")
                if response.lower() not in ['y', 'yes']:
                    continue  # Skip this file

            if verbose:
                print(f"removed '{file_path}'")
            file_path.unlink()

        # Remove directories in reverse order (deepest first)
        # Sort by path length to ensure deeper directories are removed first
        dirs.sort(key=lambda x: len(x.parts), reverse=True)
        for dir_path in dirs:
            # Interactive mode: prompt for each directory
            if interactive and not force:
                response = input(f"rm: remove directory '{dir_path}'? ")
                if response.lower() not in ['y', 'yes']:
                    continue  # Skip this directory

            if verbose:
                print(f"removed directory '{dir_path}'")
            dir_path.rmdir()

        # Finally remove the target directory itself
        if verbose:
            print(f"removed directory '{directory}'")
        directory.rmdir()

    except PermissionError as e:
        raise PermissionError(f"Permission denied")
    except Exception as e:
        raise Exception(f"Cannot remove directory: {e}")


def print_help():
    """Print detailed help message for rm command"""
    help_text = """rm - remove files or directories

Usage: rm [OPTION]... FILE...

Remove (unlink) the FILE(s).

Options:
  -r                    remove directories and their contents recursively
  -v, --verbose         explain what is being done
  -i, --interactive     prompt before every removal
  -f, --force           ignore nonexistent files and arguments, never prompt
  -h, --help            display this help and exit

By default, rm does not remove directories. Use the -r option to remove
each listed directory and all of its contents.

Examples:
  rm file.txt           Remove file.txt
  rm file1.txt file2.txt    Remove multiple files
  rm -r directory       Remove directory and its contents
  rm -v file.txt        Remove file.txt with verbose output
  rm -i file.txt        Prompt before removing file.txt
  rm -f file.txt        Force remove file.txt (ignore errors)
  rm -r -i mydir        Remove directory with interactive prompts
  rm -r -f mydir        Force remove directory (ignore errors)

CAUTION: rm removes files permanently. There is no undelete or trash.
Be careful when using -r with rm, especially as root/administrator.

Exit Status:
  Returns 0 if all files were removed successfully, non-zero otherwise.
"""
    print(help_text)
