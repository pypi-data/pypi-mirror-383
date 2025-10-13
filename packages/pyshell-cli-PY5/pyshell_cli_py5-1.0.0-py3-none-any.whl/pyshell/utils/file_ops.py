"""
File and directory operation utilities for PyShell
"""

import re
from pathlib import Path
from typing import Generator, Optional


def list_directory(path: Path, recursive: bool = False, show_hidden: bool = False) -> Generator[Path, None, None]:
    """
    List directory contents, optionally recursive.

    Args:
        path: Path to the directory to list
        recursive: If True, recursively list all subdirectories
        show_hidden: If True, include hidden files (starting with '.')

    Yields:
        Path objects for each item in the directory

    Raises:
        FileNotFoundError: If the path doesn't exist
        NotADirectoryError: If the path is not a directory
        PermissionError: If access to the directory is denied
    """
    try:
        if not path.exists():
            raise FileNotFoundError(f"No such file or directory: '{path}'")

        if not path.is_dir():
            raise NotADirectoryError(f"Not a directory: '{path}'")

        if recursive:
            for item in path.rglob('*'):
                if show_hidden or not item.name.startswith('.'):
                    yield item
        else:
            for item in path.iterdir():
                if show_hidden or not item.name.startswith('.'):
                    yield item
    except PermissionError:
        raise PermissionError(f"Permission denied: '{path}'")


def find_files(start_path: Path, pattern: str, case_sensitive: bool = True, maxdepth: Optional[int] = None) -> Generator[Path, None, None]:
    """
    Find files and directories matching a pattern with optional depth limit.

    Args:
        start_path: Starting directory for the search
        pattern: Regular expression pattern to match filenames
        case_sensitive: If True, perform case-sensitive matching
        maxdepth: Maximum directory depth to search (None for unlimited)

    Yields:
        Path objects for matching files and directories

    Raises:
        ValueError: If the pattern is invalid regex
        PermissionError: If access to directories is denied
    """
    try:
        flags = 0 if case_sensitive else re.IGNORECASE
        regex = re.compile(pattern, flags)

        if maxdepth is None:
            # Unlimited depth - use rglob but with permission error handling
            try:
                for item in start_path.rglob('*'):
                    try:
                        # Match both files and directories
                        if regex.search(item.name):
                            yield item
                    except (PermissionError, OSError):
                        # Skip items we can't access
                        pass
            except PermissionError:
                # If we can't access the start directory, raise the error
                raise
        else:
            # Limited depth - use custom traversal
            for item in _traverse_with_depth(start_path, maxdepth):
                try:
                    # Match both files and directories
                    if regex.search(item.name):
                        yield item
                except (PermissionError, OSError):
                    # Skip items we can't access
                    pass
    except re.error as e:
        raise ValueError(f"Invalid pattern: {e}")


def _traverse_with_depth(start_path: Path, maxdepth: int, current_depth: int = 0) -> Generator[Path, None, None]:
    """
    Helper function to traverse directory with depth limit.

    Args:
        start_path: Directory to start traversal from
        maxdepth: Maximum depth to traverse
        current_depth: Current depth level (used in recursion)

    Yields:
        Path objects for each item found within the depth limit
    """
    if current_depth > maxdepth:
        return

    try:
        for item in start_path.iterdir():
            yield item
            if item.is_dir() and current_depth < maxdepth:
                yield from _traverse_with_depth(item, maxdepth, current_depth + 1)
    except PermissionError:
        # Skip directories we can't access
        pass


def format_file_listing(path: Path, show_details: bool = False) -> str:
    """Format file/directory for listing"""
    if show_details:
        stat = path.stat()
        size = stat.st_size if path.is_file() else 0
        permissions = oct(stat.st_mode)[-3:]
        return f"{permissions} {size:>8} {path.name}"
    return path.name


def safe_remove_directory(path: Path, recursive: bool = False) -> bool:
    """Safely remove directory, checking if empty unless recursive"""
    if not path.exists():
        raise FileNotFoundError(f"No such file or directory: '{path}'")

    if not path.is_dir():
        raise NotADirectoryError(f"Not a directory: '{path}'")

    if not recursive:
        # Check if directory is empty
        try:
            next(path.iterdir())
            return False  # Directory not empty
        except StopIteration:
            pass  # Directory is empty

    try:
        if recursive:
            # Remove all contents recursively
            for item in path.rglob('*'):
                if item.is_file():
                    item.unlink()
            # Remove empty directories in reverse order
            for item in sorted(path.rglob('*'), key=lambda x: str(x), reverse=True):
                if item.is_dir():
                    item.rmdir()

        path.rmdir()
        return True
    except PermissionError:
        raise PermissionError(f"Permission denied: '{path}'")
    except OSError as e:
        raise OSError(f"Cannot remove '{path}': {e}")
