"""
rmdir command implementation - Remove empty directories
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import ArgumentParser, safe_remove_directory, resolve_path


def is_safe_to_remove(target, current_dir):
    """
    Check if directory is safe to remove
    Returns: (is_safe: bool, error_message: str or None)
    """
    try:
        # Resolve to absolute paths for comparison
        target_resolved = target.resolve()
        current_resolved = current_dir.resolve()

        # Prevent removing current working directory
        if target_resolved == current_resolved:
            return False, "Cannot remove current working directory"

        # Prevent removing if current directory is inside target
        try:
            current_resolved.relative_to(target_resolved)
            return False, "Cannot remove directory: current directory is inside it"
        except ValueError:
            # Not a subdirectory, this is fine
            pass

        # Check for special directories
        dir_name = target.name
        if dir_name in ['.', '..']:
            return False, f"Cannot remove '{dir_name}'"

        # Prevent removing root directory
        if target_resolved == target_resolved.parent:
            return False, "Cannot remove root directory"

        # Check if it's a system critical directory (basic check)
        critical_dirs = ['/bin', '/sbin', '/usr', '/etc', '/var', '/sys', '/proc', '/dev']
        for critical in critical_dirs:
            try:
                if target_resolved == Path(critical).resolve():
                    return False, "Cannot remove system directory"
            except (OSError, ValueError):
                pass

        return True, None

    except Exception as e:
        return False, str(e)


def run(args, shell):
    """
    Remove empty directories
    Usage: rmdir [options] [directory...]
    Options:
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
        boolean_flags = {'f', 'force'}
        parser.validate_flags(boolean_flags)
    except ValueError as e:
        print(f"rmdir: {e}", file=sys.stderr)
        return 1

    if not parser.positional:
        print("rmdir: missing operand", file=sys.stderr)
        return 1

    # Track exit code - start with 0 (success), set to 1 if any errors occur
    exit_code = 0

    for dir_name in parser.positional:
        try:
            # Check for invalid arguments
            if dir_name.strip() in ['', '.', '..']:
                if not force:
                    print(f"rmdir: failed to remove '{dir_name}': Invalid argument", file=sys.stderr)
                exit_code = 1
                continue

            # Resolve path
            try:
                target = resolve_path(dir_name, current_dir, resolve_symlinks=True)
            except (OSError, RuntimeError):
                if not force:
                    print(f"rmdir: failed to remove '{dir_name}': Invalid path", file=sys.stderr)
                exit_code = 1
                continue

            # Check if path exists
            if not target.exists():
                if not force:
                    print(f"rmdir: failed to remove '{dir_name}': No such file or directory", file=sys.stderr)
                exit_code = 1
                continue

            # Check if it's a directory (not a symlink to a directory)
            if not target.is_dir():
                if not force:
                    print(f"rmdir: failed to remove '{dir_name}': Not a directory", file=sys.stderr)
                exit_code = 1
                continue

            # Check if it's a symbolic link
            if target.is_symlink():
                if not force:
                    print(f"rmdir: failed to remove '{dir_name}': Is a symbolic link", file=sys.stderr)
                exit_code = 1
                continue

            # Safety checks
            is_safe, error_msg = is_safe_to_remove(target, current_dir)
            if not is_safe:
                if not force:
                    print(f"rmdir: failed to remove '{dir_name}': {error_msg}", file=sys.stderr)
                exit_code = 1
                continue

            # Try to remove directory (only if empty)
            success = safe_remove_directory(target, recursive=False)

            if not success:
                if not force:
                    print(f"rmdir: failed to remove '{dir_name}': Directory not empty", file=sys.stderr)
                exit_code = 1

        except PermissionError:
            if not force:
                print(f"rmdir: failed to remove '{dir_name}': Permission denied", file=sys.stderr)
            exit_code = 1
        except OSError as e:
            if not force:
                if e.errno == 16:  # Device or resource busy
                    print(f"rmdir: failed to remove '{dir_name}': Device or resource busy", file=sys.stderr)
                else:
                    print(f"rmdir: failed to remove '{dir_name}': {e}", file=sys.stderr)
            exit_code = 1
        except Exception as e:
            if not force:
                print(f"rmdir: failed to remove '{dir_name}': {e}", file=sys.stderr)
            exit_code = 1

    return exit_code


def print_help():
    """Print help information for rmdir command"""
    print("""Usage: rmdir [options] [directory...]

Remove empty directories.

Options:
    -f, --force        Ignore errors and continue
    -h, --help         Show this help message

Examples:
    rmdir empty_dir     Remove empty directory 'empty_dir'
    rmdir dir1 dir2     Remove multiple empty directories
    rmdir -f nonexistent Ignore errors when removing nonexistent directories
    rmdir -h            Show this help message

Note: rmdir only removes empty directories. Use other tools to remove
directories with contents.

Exit Status:
    Returns 0 if all directories were removed successfully, non-zero otherwise.""")
