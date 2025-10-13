"""
mv command implementation - Move/rename files and directories
"""

import sys
import shutil
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import ArgumentParser, resolve_path


def is_subdirectory(child, parent):
    """
    Check if child is a subdirectory of parent
    """
    try:
        child_resolved = child.resolve()
        parent_resolved = parent.resolve()

        # Check if child is same as parent
        if child_resolved == parent_resolved:
            return True

        # Check if child is inside parent
        try:
            child_resolved.relative_to(parent_resolved)
            return True
        except ValueError:
            return False
    except Exception:
        return False


def is_valid_move(src_path, dest_path, source_name):
    """
    Validate if the move operation is safe and valid
    Returns: (is_valid: bool, error_message: str or None)
    """
    try:
        # Resolve paths
        src_resolved = src_path.resolve()
        dest_resolved = dest_path.resolve() if dest_path.exists() else dest_path

        # Check for special names
        if source_name in ['.', '..']:
            return False, f"Cannot move '{source_name}'"

        # Check if source and destination are the same
        if src_resolved == dest_resolved:
            return False, "Source and destination are the same"

        # Check if trying to move directory into itself
        if src_path.is_dir():
            # If destination is inside source, it's invalid
            if is_subdirectory(dest_resolved, src_resolved):
                return False, "Cannot move directory into itself"

        return True, None

    except Exception as e:
        return False, str(e)


def run(args, shell):
    """
    Move/rename files and directories
    Usage: mv [options] source destination
           mv [options] source... directory
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
        print(f"mv: {e}", file=sys.stderr)
        return 1

    if len(parser.positional) < 2:
        print("mv: missing file operand", file=sys.stderr)
        return 1

    # Track exit code - start with 0 (success), set to 1 if any errors occur
    exit_code = 0

    sources = parser.positional[:-1]
    destination = parser.positional[-1]

    # Resolve destination path
    try:
        dest_path = resolve_path(destination, current_dir, resolve_symlinks=True)
    except (OSError, RuntimeError):
        # If resolve fails, just use the path as-is
        dest_path = Path(destination)
        if not dest_path.is_absolute():
            dest_path = current_dir / dest_path

    # Remove trailing slashes for consistency
    dest_str = str(dest_path).rstrip('/')
    dest_path = Path(dest_str)

    try:
        # If multiple sources, destination must be a directory
        if len(sources) > 1:
            if not dest_path.exists():
                if not force:
                    print(f"mv: target '{destination}': No such file or directory", file=sys.stderr)
                return 1
            if not dest_path.is_dir():
                if not force:
                    print(f"mv: target '{destination}' is not a directory", file=sys.stderr)
                return 1

        for source in sources:
            # Resolve source path
            src_path = resolve_path(source, current_dir)

            # Check if source exists
            if not src_path.exists():
                if not force:
                    print(f"mv: cannot stat '{source}': No such file or directory", file=sys.stderr)
                exit_code = 1
                continue

            # Validate the move operation
            is_valid, error_msg = is_valid_move(src_path, dest_path, source)
            if not is_valid:
                if not force:
                    print(f"mv: cannot move '{source}': {error_msg}", file=sys.stderr)
                exit_code = 1
                continue

            # Determine final destination
            try:
                if dest_path.is_dir():
                    final_dest = dest_path / src_path.name
                else:
                    final_dest = dest_path
            except Exception:
                final_dest = dest_path

            # Additional check: if destination directory doesn't exist for rename
            if not dest_path.exists() and len(sources) == 1:
                # This is a rename operation - check parent directory exists
                try:
                    if not final_dest.parent.exists():
                        if not force:
                            print(f"mv: cannot move '{source}' to '{destination}': No such file or directory", file=sys.stderr)
                        exit_code = 1
                        continue
                except Exception:
                    if not force:
                        print(f"mv: cannot move '{source}' to '{destination}': No such file or directory", file=sys.stderr)
                    exit_code = 1
                    continue

            # Check if destination already exists
            try:
                if final_dest.exists():
                    # Additional validation for existing destination
                    try:
                        final_dest_resolved = final_dest.resolve()
                        src_resolved = src_path.resolve()

                        # If they're the same (after resolution), skip
                        if src_resolved == final_dest_resolved:
                            continue

                    except Exception:
                        pass

                    try:
                        if final_dest.is_dir() and src_path.is_file():
                            if not force:
                                print(f"mv: cannot overwrite directory '{destination}' with non-directory", file=sys.stderr)
                            exit_code = 1
                            continue
                        elif final_dest.is_file() and src_path.is_dir():
                            if not force:
                                print(f"mv: cannot overwrite non-directory '{destination}' with directory", file=sys.stderr)
                            exit_code = 1
                            continue
                    except Exception:
                        pass
            except Exception:
                pass

            # For directories, additional check
            try:
                if src_path.is_dir() and final_dest.exists() and final_dest.is_dir():
                    # Check if trying to move into existing directory with same name
                    nested_dest = final_dest / src_path.name
                    if nested_dest.exists():
                        if not force:
                            print(f"mv: cannot move '{source}': Destination already exists", file=sys.stderr)
                        exit_code = 1
                        continue
            except Exception:
                pass

            # Perform the move operation
            try:
                if src_path.is_file():
                    # Move file
                    try:
                        if final_dest.exists() and final_dest.is_file():
                            final_dest.unlink()  # Remove existing file
                    except Exception:
                        pass
                    shutil.move(str(src_path), str(final_dest))
                elif src_path.is_dir():
                    # Move directory
                    try:
                        if final_dest.exists():
                            if final_dest.is_dir():
                                # Move into existing directory
                                final_dest = final_dest / src_path.name
                            else:
                                if not force:
                                    print(f"mv: cannot overwrite non-directory '{destination}' with directory", file=sys.stderr)
                                exit_code = 1
                                continue
                    except Exception:
                        pass
                    shutil.move(str(src_path), str(final_dest))

            except PermissionError:
                if not force:
                    print(f"mv: cannot move '{source}': Permission denied", file=sys.stderr)
                exit_code = 1
            except OSError as e:
                if not force:
                    errno_val = getattr(e, 'errno', None)
                    if errno_val == 18:  # Invalid cross-device link
                        print(f"mv: cannot move '{source}': Cross-device move requires copy", file=sys.stderr)
                    else:
                        print(f"mv: cannot move '{source}': {e}", file=sys.stderr)
                exit_code = 1
            except Exception as e:
                if not force:
                    print(f"mv: cannot move '{source}': {e}", file=sys.stderr)
                exit_code = 1

    except Exception as e:
        if not force:
            print(f"mv: {e}", file=sys.stderr)
        return 1

    return exit_code


def print_help():
    """Print help information for mv command"""
    print("""Usage: mv [options] source destination
       mv [options] source... directory

Move or rename files and directories.

Options:
    -f, --force        Ignore errors and continue
    -h, --help         Show this help message

Examples:
    mv file.txt newname.txt     Rename file.txt to newname.txt
    mv file.txt /tmp/           Move file.txt to /tmp/ directory
    mv dir1 dir2                Move directory dir1 to dir2
    mv file1 file2 /tmp/        Move multiple files to /tmp/ directory
    mv -f nonexistent.txt /tmp/ Ignore errors when moving nonexistent files
    mv -h                      Show this help message

Note: mv can both move and rename files/directories. When moving multiple
sources, the destination must be a directory.

Exit Status:
    Returns 0 if all operations were successful, non-zero otherwise.""")
