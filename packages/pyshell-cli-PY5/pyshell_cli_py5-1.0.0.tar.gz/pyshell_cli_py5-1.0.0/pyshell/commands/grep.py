"""
grep command implementation - Search text patterns in files
Supports -n flag for line numbers and -i flag for case insensitive search
"""

import sys
import re
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils import ArgumentParser, resolve_path


def is_binary_file(file_path, chunk_size=8192):
    """
    Check if file is binary by reading a chunk and looking for null bytes
    """
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(chunk_size)
            # Check for null bytes (common in binary files)
            if b'\x00' in chunk:
                return True
            # Check for high proportion of non-text characters
            text_characters = bytes(range(32, 127)) + b'\n\r\t\b'
            non_text = sum(1 for byte in chunk if byte not in text_characters)
            # If more than 30% non-text characters, consider it binary
            if chunk and (non_text / len(chunk)) > 0.3:
                return True
        return False
    except Exception:
        return True  # If we can't read it, treat as binary


def is_valid_pattern(pattern):
    """
    Validate regex pattern for potential issues
    Returns: (is_valid: bool, error_message: str or None)
    """
    if not pattern or pattern.strip() == '':
        return False, "Empty pattern"

    # Check pattern length (very long patterns can cause performance issues)
    if len(pattern) > 10000:
        return False, "Pattern too long"

    # Try to compile to catch regex errors
    try:
        re.compile(pattern)
        return True, None
    except re.error as e:
        # Provide more user-friendly error messages
        error_str = str(e)
        if 'unbalanced' in error_str or 'unterminated' in error_str:
            return False, "unbalanced bracket"
        return False, error_str


def run(args, shell):
    """
    Search for patterns in files
    Usage: grep [options] pattern [file...]
    Options:
        -n    Show line numbers
        -i    Case insensitive search
        -F    Fixed string (literal) search (treat pattern as literal text, not regex)
        -f, --force    Ignore errors and continue
        -h, --help    Show this help message
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
        boolean_flags = {'n', 'i', 'F', 'f', 'force'}
        parser.validate_flags(boolean_flags)
    except ValueError as e:
        print(f"grep: {e}", file=sys.stderr)
        return 1

    if not parser.positional:
        print("grep: missing pattern", file=sys.stderr)
        return 1

    # The ArgumentParser already handles quoted strings, so we don't need to strip quotes
    # Just use the pattern as-is from the parser
    pattern = parser.positional[0]
    files = parser.positional[1:] if len(parser.positional) > 1 else []

    # Get options first to check for -F flag
    show_line_numbers = parser.has_flag('n')
    case_insensitive = parser.has_flag('i')
    fixed_string = parser.has_flag('F')

    # If no files specified, read from stdin
    if not files:
        files = ['-']

    # Handle pattern based on search type
    if fixed_string:
        # For fixed string search, escape all regex special characters
        pattern = re.escape(pattern)

    # Validate pattern (only for regex mode)
    if not fixed_string:
        is_valid, error_msg = is_valid_pattern(pattern)
        if not is_valid:
            if not force:
                print(f"grep: invalid pattern: {error_msg}", file=sys.stderr)
            return 1

    try:
        # Compile pattern with proper flags
        flags = re.IGNORECASE if case_insensitive else 0
        compiled_pattern = re.compile(pattern, flags)
    except re.error as e:
        if not force:
            print(f"grep: invalid pattern: {e}", file=sys.stderr)
        return 1

    # Track exit code - start with 0 (success), set to 1 if any errors occur
    exit_code = 0
    total_matches = 0
    multiple_files = len(files) > 1

    for file_arg in files:
        # Check if reading from stdin
        if file_arg == '-':
            try:
                matches = search_stdin(compiled_pattern, show_line_numbers)
                total_matches += matches
            except KeyboardInterrupt:
                print()  # Print newline on Ctrl+C
                return 130
            except Exception as e:
                if not force:
                    print(f"grep: stdin: {e}", file=sys.stderr)
                exit_code = 1
            continue

        # Validate file argument
        if not file_arg or file_arg.strip() == '':
            if not force:
                print("grep: invalid file operand", file=sys.stderr)
            exit_code = 1
            continue

        try:
            file_path = resolve_path(file_arg, current_dir, resolve_symlinks=True)
        except (OSError, RuntimeError):
            if not force:
                print(f"grep: {file_arg}: Invalid path", file=sys.stderr)
            exit_code = 1
            continue

        try:

            if file_path.is_dir():
                # Search in all files in directory (non-recursive)
                try:
                    dir_files = list(file_path.iterdir())
                    if not dir_files:
                        continue  # Empty directory

                    for item in dir_files:
                        if item.is_file() and not item.is_symlink():
                            matches = search_in_file(item, compiled_pattern,
                                                    show_line_numbers, multiple_files, force)
                            total_matches += matches
                except PermissionError:
                    if not force:
                        print(f"grep: {file_arg}: Permission denied", file=sys.stderr)
                    exit_code = 1

            elif file_path.is_file():
                matches = search_in_file(file_path, compiled_pattern,
                                        show_line_numbers, multiple_files, force)
                total_matches += matches
            else:
                if not force:
                    print(f"grep: {file_arg}: No such file or directory", file=sys.stderr)
                exit_code = 1

        except PermissionError:
            if not force:
                print(f"grep: {file_arg}: Permission denied", file=sys.stderr)
            exit_code = 1
        except Exception as e:
            if not force:
                print(f"grep: {file_arg}: {e}", file=sys.stderr)
            exit_code = 1

    return exit_code


def search_in_file(file_path, pattern, show_line_numbers, show_filename, force=False):
    """Search for pattern in a single file"""
    matches = 0

    try:
        # Skip if not a regular file
        if not file_path.is_file():
            return matches

        # Skip symbolic links to avoid potential issues
        if file_path.is_symlink():
            return matches

        # Check file size (skip very large files > 100MB)
        file_size = file_path.stat().st_size
        if file_size > 100 * 1024 * 1024:  # 100MB
            if not force:
                print(f"grep: {file_path.name}: File too large, skipping", file=sys.stderr)
            return matches

        # Check if file is empty
        if file_size == 0:
            return matches  # Empty file, no matches

        # Check if file is binary
        if is_binary_file(file_path):
            return matches  # Skip binary files silently

        # Read and search file
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
                    # Handle very long lines (potential memory issue)
                    if len(line) > 100000:  # Skip lines longer than 100K chars
                        continue

                    line = line.rstrip('\n\r')

                    try:
                        if pattern.search(line):
                            matches += 1

                            # Format output
                            output_parts = []

                            if show_filename:
                                output_parts.append(str(file_path.name))

                            if show_line_numbers:
                                output_parts.append(str(line_num))

                            output_parts.append(line)

                            # Join with appropriate separator
                            if show_filename or show_line_numbers:
                                print(':'.join(output_parts))
                            else:
                                print(line)
                    except Exception:
                        # Pattern matching error on this line, skip it
                        continue

        except UnicodeDecodeError:
            # File contains invalid unicode, skip it
            return matches
        except MemoryError:
            if not force:
                print(f"grep: {file_path.name}: File too large to process", file=sys.stderr)
            return matches

    except PermissionError:
        if not force:
            print(f"grep: {file_path.name}: Permission denied", file=sys.stderr)
    except OSError as e:
        if not force:
            if e.errno == 5:  # I/O error
                print(f"grep: {file_path.name}: I/O error", file=sys.stderr)
            else:
                print(f"grep: {file_path.name}: {e}", file=sys.stderr)
    except Exception as e:
        if not force:
            print(f"grep: {file_path.name}: {e}", file=sys.stderr)

    return matches


def search_stdin(pattern, show_line_numbers):
    """Search for pattern in stdin"""
    matches = 0

    for line_num, line in enumerate(sys.stdin, 1):
        # Handle very long lines (potential memory issue)
        if len(line) > 100000:  # Skip lines longer than 100K chars
            continue

        line = line.rstrip('\n\r')

        try:
            if pattern.search(line):
                matches += 1

                # Format output
                if show_line_numbers:
                    print(f"{line_num}:{line}")
                else:
                    print(line)
        except Exception:
            # Pattern matching error on this line, skip it
            continue

    return matches


def print_help():
    """Print help information for grep command"""
    print("""Usage: grep [options] pattern [file...]

Search for patterns in files using regular expressions or fixed strings.
With no FILE, or when FILE is -, read standard input.

Options:
    -n                  Show line numbers
    -i                  Case insensitive search
    -F                  Fixed string search (treat pattern as literal text, not regex)
    -f, --force         Ignore errors and continue
    -h, --help          Show this help message

Examples:
    grep "hello" file.txt                    Search for "hello" in file.txt
    grep -n "error" *.log                    Search for "error" in all .log files with line numbers
    grep -i "WARNING" /var/log/*             Case insensitive search for "WARNING"
    grep -F "this is test" file.txt          Search for literal text "this is test"
    grep -F -i "multi word pattern" *.txt    Case insensitive literal search for multiword patterns
    cat file.txt | grep "pattern"            Search pattern in piped input
    grep -f "pattern" nonexistent            Ignore errors when searching nonexistent files

Exit Status:
    Returns 0 unless an error occurs or invalid option is given.

Note:
    - By default, grep uses Python regular expressions.
      Special characters like . * + ? ^ $ | ( ) [ ] { } \\ need escaping.
    - Use -F flag for literal string matching, ideal for multiword patterns
      and avoids regex complexity.""")
