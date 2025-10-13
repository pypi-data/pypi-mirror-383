"""
mkdir command implementation - Create directories
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import ArgumentParser, resolve_path


def is_valid_directory_name(dir_name):
    """
    Validate directory name for invalid characters and patterns
    """
    # Check for empty string
    if not dir_name or dir_name.strip() == '':
        return False, "Directory name cannot be empty"

    # Check for invalid patterns
    if dir_name in ['.', '..']:
        return False, "Cannot create directory '.' or '..'"

    # Check for null bytes (not allowed in filenames)
    if '\0' in dir_name:
        return False, "Directory name cannot contain null bytes"

    # Check for path separators only
    if dir_name.replace('/', '').replace('\\', '').strip() == '':
        return False, "Directory name cannot consist only of separators"

    return True, None


def run(args, shell):
    """
    Create directories
    Usage: mkdir [directory...]
    """
    parser = ArgumentParser(args)
    current_dir = shell.current_dir

    # Check for help flags
    if parser.has_flag('h') or parser.has_flag('help'):
        print_help()
        return 0

    if not parser.positional:
        print("mkdir: missing operand", file=sys.stderr)
        print("Try 'mkdir --help' for more information.", file=sys.stderr)
        return 1

    # Track exit code - start with 0 (success), set to 1 if any errors occur
    exit_code = 0

    for dir_name in parser.positional:
        try:
            # Validate directory name
            is_valid, error_msg = is_valid_directory_name(dir_name)
            if not is_valid:
                print(f"mkdir: cannot create directory '{dir_name}': {error_msg}", file=sys.stderr)
                exit_code = 1
                continue

            # Check path length early (before resolve which might fail on long paths)
            # Combine current_dir and dir_name to estimate final path length
            estimated_path = str(current_dir / dir_name)
            if len(estimated_path) > 4096:
                print(f"mkdir: cannot create directory '{dir_name}': Path too long", file=sys.stderr)
                exit_code = 1
                continue

            # Resolve path
            try:
                target = resolve_path(dir_name, current_dir, resolve_symlinks=True)
            except (OSError, RuntimeError) as e:
                # Check if error is due to path length
                error_str = str(e).lower()
                if 'too long' in error_str or 'name too long' in error_str:
                    print(f"mkdir: cannot create directory '{dir_name}': Path too long", file=sys.stderr)
                else:
                    print(f"mkdir: cannot create directory '{dir_name}': Invalid path", file=sys.stderr)
                exit_code = 1
                continue

            # Check if already exists
            if target.exists():
                print(f"mkdir: cannot create directory '{dir_name}': Directory already exists", file=sys.stderr)
                exit_code = 1
                continue

            # Create directory
            target.mkdir(parents=True, exist_ok=False)

        except PermissionError:
            print(f"mkdir: cannot create directory '{dir_name}': Permission denied", file=sys.stderr)
            exit_code = 1
        except OSError as e:
            # Handle specific OS errors
            if e.errno == 36 or e.errno == 63:  # File name too long (36 on Linux, 63 on macOS)
                print(f"mkdir: cannot create directory '{dir_name}': Path too long", file=sys.stderr)
            elif e.errno == 28:  # No space left on device
                print(f"mkdir: cannot create directory '{dir_name}': No space left on device", file=sys.stderr)
            else:
                print(f"mkdir: cannot create directory '{dir_name}': {e}", file=sys.stderr)
            exit_code = 1
        except Exception as e:
            print(f"mkdir: cannot create directory '{dir_name}': {e}", file=sys.stderr)
            exit_code = 1

    return exit_code


def print_help():
    """Print detailed help message for mkdir command"""
    help_text = """mkdir - make directories

Usage: mkdir [OPTION]... DIRECTORY...

Create the DIRECTORY(ies), if they do not already exist.

Options:
  -h, --help     display this help and exit

Examples:
  mkdir newdir                    Create a single directory
  mkdir dir1 dir2 dir3            Create multiple directories
  mkdir -p path/to/nested/dir     Create nested directories (if -p supported)

Exit Status:
  Returns 0 unless an error occurs or invalid option is given.
"""
    print(help_text)
