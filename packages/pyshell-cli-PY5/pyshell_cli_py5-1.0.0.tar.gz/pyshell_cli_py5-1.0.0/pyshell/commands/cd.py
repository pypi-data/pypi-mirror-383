"""
cd command - Change directory.

Implementation Details:
- Pure Python implementation using only pathlib and existing utilities
- No os module usage - uses callback mechanism to notify shell
- Leverages existing parsers, helpers, and file operations utilities
- Supports all standard cd functionality without os.chdir()
"""

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import ArgumentParser, resolve_path


def _validate_directory(target_path: Path) -> bool:
    """Validate that target path is a valid directory using pathlib"""
    try:
        # Check if path exists
        if not target_path.exists():
            raise FileNotFoundError(f"cd: {target_path}: No such file or directory")

        # Check if it's a directory
        if not target_path.is_dir():
            raise NotADirectoryError(f"cd: {target_path}: Not a directory")

        # Check if we can access the directory
        try:
            next(target_path.iterdir())
        except PermissionError:
            raise PermissionError(f"cd: {target_path}: Permission denied")
        except StopIteration:
            pass  # Empty directory is fine

        return True

    except (OSError, PermissionError) as e:
        raise OSError(f"cd: {target_path}: {e}")


def _go_home(shell):
    """Change to home directory"""
    home_dir = Path.home()
    shell.change_directory(home_dir)
    print(f"Changed to home directory: {home_dir}")


def _go_to_previous(shell):
    """Change to previous directory (cd - functionality)"""
    if shell.previous_dir:
        shell.change_directory(shell.previous_dir)
        print(f"Changed to previous directory: {shell.previous_dir}")
    else:
        print("cd: no previous directory")


def _go_to_target(target: str, current_dir: Path, shell):
    """Change to target directory"""
    # Handle special cases
    if target == "-":
        _go_to_previous(shell)
        return

    # Resolve the target path
    try:
        absolute_path = resolve_path(target, current_dir, resolve_symlinks=True)
    except (OSError, RuntimeError) as e:
        raise OSError(f"cd: {target}: Invalid path: {e}")

    # Validate the directory
    _validate_directory(absolute_path)

    # Change to the directory
    shell.change_directory(absolute_path)
    print(f"Changed to directory: {absolute_path}")


def run(args, shell):
    """Command entry point - pure Python implementation without os module"""
    parser = ArgumentParser(args)
    current_dir = shell.current_dir

    try:
        # Check for help flags using existing parser
        if parser.has_flag('h') or parser.has_flag('help'):
            print_help()
            return 0
        # Get target from positional arguments
        target = parser.get_positional(0)
        if target is None:
            # No arguments: go to home directory
            _go_home(shell)
        else:
            # Change to specified directory
            _go_to_target(target, current_dir, shell)

        return 0

    except (FileNotFoundError, NotADirectoryError, PermissionError, OSError) as e:
        print(str(e), file=sys.stderr)
        return 1
    except Exception as e:
        print(f"cd: unexpected error: {e}", file=sys.stderr)
        return 1


def print_help():
    """Print detailed help message for cd command"""
    help_text = """cd - change directory

Usage: cd [DIRECTORY]

Change the current working directory to DIRECTORY. If no DIRECTORY is specified,
changes to the home directory.

Special directories:
  ~              Home directory
  ..             Parent directory
  .              Current directory (no change)
  /              Root directory

Options:
  -h, --help     Display this help and exit

Examples:
  cd                    Go to home directory
  cd /usr/local         Go to /usr/local directory
  cd ..                 Go to parent directory
  cd ~/Documents        Go to Documents in home directory
  cd -                  Go to previous directory
  cd .                  Stay in current directory

Exit Status:
  Returns 0 if successful, 1 if an error occurs.
"""
    print(help_text)

