"""
cp command implementation - Copy files and directories
Pure Python implementation with -r, -i, -u, -v, -h options
"""

import sys
import shutil
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import ArgumentParser, resolve_path


def run(args, shell):
    """
    Copy files and directories
    Usage: cp [-r] [-i] [-u] [-v] [-h | --help] source... destination

    Options:
        -r, --recursive       Copy directories recursively
        -i, --interactive     Prompt before overwrite
        -u, --update          Copy only when source is newer than destination
        -v, --verbose         Explain what is being done
        -h, --help            Display this help message and exit

    Copy SOURCE to DEST, or multiple SOURCE(s) to DIRECTORY.
    """
    parser = ArgumentParser(args)
    current_dir = shell.current_dir

    # Check for help flag
    if parser.has_flag('h') or parser.has_flag('help'):
        print_help()
        return 0

    # Check for recursive flag (-r or --recursive)
    recursive = parser.has_flag('r') or parser.has_flag('recursive')

    # Check for interactive flag (-i or --interactive)
    interactive = parser.has_flag('i') or parser.has_flag('interactive')

    # Check for update flag (-u or --update)
    update = parser.has_flag('u') or parser.has_flag('update')

    # Check for verbose flag (-v or --verbose)
    verbose = parser.has_flag('v') or parser.has_flag('verbose')

    try:
        # Validate flags - check if any switch is present but has an invalid option value
        boolean_flags = {'r', 'recursive', 'i', 'interactive', 'u', 'update', 'v', 'verbose'}
        parser.validate_flags(boolean_flags)
    except ValueError as e:
        print(f"cp: {e}", file=sys.stderr)
        return 1

    # Get source files and destination
    if len(parser.positional) < 2:
        print("cp: missing file operand", file=sys.stderr)
        print("Try 'cp --help' for more information.", file=sys.stderr)
        return 1

    sources = parser.positional[:-1]
    destination = parser.positional[-1]

    # Process the copy operation
    exit_code = copy_files(sources, destination, current_dir, recursive, interactive, update, verbose)

    return exit_code


def copy_files(sources, destination, current_dir, recursive=False, interactive=False, update=False, verbose=False):
    """
    Copy files and directories

    Args:
        sources: List of source paths
        destination: Destination path
        current_dir: Current working directory
        recursive: Whether to copy directories recursively
        interactive: Whether to prompt before overwrite
        update: Whether to copy only when source is newer
        verbose: Whether to print verbose output

    Returns:
        Exit code (0 for success, 1 for any errors)
    """
    dest_path = resolve_path(destination, current_dir)

    # Track exit code - start with 0 (success), set to 1 if any errors occur
    exit_code = 0

    # Handle multiple sources - destination must be a directory
    if len(sources) > 1:
        if not dest_path.exists():
            # Create destination directory if it doesn't exist
            dest_path.mkdir(parents=True, exist_ok=True)
            if verbose:
                print(f"created directory '{dest_path}'")
        elif not dest_path.is_dir():
            print(f"cp: target '{destination}' is not a directory", file=sys.stderr)
            return 1

    # Copy each source
    for source in sources:
        source_path = resolve_path(source, current_dir)

        try:
            copy_item(source_path, dest_path, current_dir, recursive, interactive, update, verbose)
        except Exception as e:
            print(f"cp: cannot copy '{source}': {e}", file=sys.stderr)
            exit_code = 1

    return exit_code


def copy_item(source_path, dest_path, current_dir, recursive=False, interactive=False, update=False, verbose=False):
    """
    Copy a single file or directory

    Args:
        source_path: Source path
        dest_path: Destination path
        current_dir: Current working directory
        recursive: Whether to copy directories recursively
        interactive: Whether to prompt before overwrite
        update: Whether to copy only when source is newer
        verbose: Whether to print verbose output
    """
    if not source_path.exists():
        raise FileNotFoundError("No such file or directory")

    # Determine the actual destination path
    if dest_path.exists() and dest_path.is_dir():
        # If destination exists and is a directory, copy into it
        actual_dest = dest_path / source_path.name
    else:
        # If destination is a file or doesn't exist, copy to that exact path
        actual_dest = dest_path

    # Handle interactive mode
    if interactive and actual_dest.exists():
        response = input(f"cp: overwrite '{actual_dest}'? ")
        if response.lower() not in ['y', 'yes']:
            if verbose:
                print(f"'{source_path}' -> '{actual_dest}' (skipped)")
            return

    # Handle update mode
    if update and actual_dest.exists():
        if source_path.is_file() and actual_dest.is_file():
            # Only copy if source is newer than destination
            source_mtime = source_path.stat().st_mtime
            dest_mtime = actual_dest.stat().st_mtime
            if source_mtime <= dest_mtime:
                if verbose:
                    print(f"'{source_path}' -> '{actual_dest}' (not newer, skipped)")
                return

    if source_path.is_file():
        # Copy file
        copy_file(source_path, actual_dest, verbose)
    elif source_path.is_dir():
        if not recursive:
            raise IsADirectoryError(f"omitting directory '{source_path}' (use -r to copy directories)")

        # Copy directory recursively
        copy_directory(source_path, actual_dest, current_dir, recursive, interactive, update, verbose)
    else:
        raise ValueError(f"'{source_path}' is not a regular file or directory")


def copy_file(source_path, dest_path, verbose=False):
    """
    Copy a single file

    Args:
        source_path: Source file path
        dest_path: Destination file path
        verbose: Whether to print verbose output
    """
    try:
        # Create parent directories if they don't exist
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy the file
        shutil.copy2(source_path, dest_path)

        if verbose:
            print(f"'{source_path}' -> '{dest_path}'")

    except PermissionError:
        raise PermissionError(f"Permission denied")
    except Exception as e:
        raise Exception(f"Cannot copy file: {e}")


def copy_directory(source_path, dest_path, current_dir, recursive=False, interactive=False, update=False, verbose=False):
    """
    Copy a directory recursively

    Args:
        source_path: Source directory path
        dest_path: Destination directory path
        current_dir: Current working directory
        recursive: Whether to copy directories recursively
        interactive: Whether to prompt before overwrite
        update: Whether to copy only when source is newer
        verbose: Whether to print verbose output
    """
    try:
        # Create destination directory
        dest_path.mkdir(parents=True, exist_ok=True)

        if verbose:
            print(f"'{source_path}' -> '{dest_path}'")

        # Copy all items in the directory
        for item in source_path.iterdir():
            item_dest = dest_path / item.name

            if item.is_file():
                copy_file(item, item_dest, verbose)
            elif item.is_dir():
                if recursive:
                    copy_directory(item, item_dest, current_dir, recursive, interactive, update, verbose)
                else:
                    if verbose:
                        print(f"omitting directory '{item}' (use -r to copy directories)")
            else:
                if verbose:
                    print(f"skipping special file '{item}'")

    except PermissionError:
        raise PermissionError(f"Permission denied")
    except Exception as e:
        raise Exception(f"Cannot copy directory: {e}")


def print_help():
    """Print detailed help message for cp command"""
    help_text = """cp - copy files and directories

Usage: cp [OPTION]... SOURCE... DEST
   or: cp [OPTION]... SOURCE... DIRECTORY

Copy SOURCE to DEST, or multiple SOURCE(s) to DIRECTORY.

Options:
  -r, --recursive    copy directories recursively
  -i, --interactive  prompt before overwrite
  -u, --update       copy only when SOURCE file is newer than destination file
  -v, --verbose      explain what is being done
  -h, --help         display this help and exit

By default, sparse SOURCE files are detected by a crude heuristic and the
corresponding DEST file is made sparse as well. That is the behavior
selected by --sparse=auto. Specify --sparse=always to create a sparse DEST
file whenever the SOURCE file contains a long enough sequence of zero bytes.
Use --sparse=never to inhibit creation of sparse files.

When --force is specified, cp will attempt to copy files even if they
cannot be read or written.

Examples:
  cp file.txt backup.txt              Copy file to backup
  cp file1.txt file2.txt /backup/     Copy multiple files to directory
  cp -r source_dir dest_dir           Copy directory recursively
  cp -i file.txt existing.txt         Interactive copy (prompt before overwrite)
  cp -u source.txt dest.txt           Update copy (only if source is newer)
  cp -v file.txt backup.txt           Verbose copy (show what's being done)
  cp -r -v source_dir dest_dir        Recursive verbose copy

Exit Status:
  Returns 0 if all files were copied successfully, non-zero otherwise.
"""
    print(help_text)
