"""
Helper functions for PyShell.
"""

from pathlib import Path
from typing import Union


def resolve_path(
    path: Union[str, Path],
    current_dir: Path,
    expand_user: bool = True,
    resolve_symlinks: bool = False
) -> Path:
    """
    Resolve a path relative to the current directory.

    This utility function standardizes path resolution across all PyShell commands,
    handling relative paths, absolute paths, tilde expansion, and symbolic links.

    Args:
        path: Path string or Path object to resolve
        current_dir: Current working directory
        expand_user: Whether to expand ~ to home directory (default: True)
        resolve_symlinks: Whether to resolve symbolic links and normalize path (default: False)

    Returns:
        Resolved absolute Path object

    Examples:
        >>> resolve_path("file.txt", Path("/home/user"))
        Path('/home/user/file.txt')

        >>> resolve_path("~/docs", Path("/tmp"))
        Path('/home/user/docs')

        >>> resolve_path("/etc/hosts", Path("/tmp"))
        Path('/etc/hosts')

        >>> resolve_path("../test", Path("/home/user/dir"))
        Path('/home/user/test')
    """
    target = Path(path)

    # Expand ~ to home directory
    if expand_user and str(target).startswith('~'):
        target = target.expanduser()

    # Convert relative paths to absolute
    if not target.is_absolute():
        target = current_dir / target

    # Resolve symlinks and normalize path
    if resolve_symlinks:
        target = target.resolve()

    return target
