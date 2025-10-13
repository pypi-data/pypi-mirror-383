# PyShell

A modular UNIX-like shell implementation in Python with a plugin architecture for custom commands.

## About

PyShell is an educational project that implements a fully functional command-line shell using pure Python. It mimics the behavior of UNIX shells while maintaining a clean, extensible architecture. The project demonstrates key concepts in operating systems, including command parsing, process management, file operations, and interactive user interfaces.

Built with a plugin-based architecture, PyShell separates core shell functionality from individual commands. Each command is a standalone Python module, making it easy to add, modify, or remove commands without touching the core shell engine. The shell maintains its own internal state, including current directory tracking and command history, providing a seamless user experience similar to bash or zsh.

## Features

- **Modular Design**: Plugin-based command system for easy extensibility
- **Command History**: Up/Down arrow navigation with persistent history across sessions
- **Pipelines & Redirections**: Full POSIX-like pipeline and I/O redirection support
- **UNIX-Compatible**: Familiar commands with UNIX-like behavior and options
- **Pure Python**: No external dependencies required - uses only standard library
- **Cross-Platform**: Works on Windows, Linux, and macOS
- **Comprehensive Testing**: Full test suite with unit tests for all commands

## Project Structure

```
PythonProjT5/
├── pyshell/
│   ├── commands/          # Plugin commands (ls, cat, grep, etc.)
│   ├── core/              # Shell engine and history management
│   │   ├── shell.py       # Main shell class with event loop
│   │   ├── history.py     # Command history with readline
│   │   └── pipeline.py    # Pipeline and redirection handler
│   ├── utils/             # Shared utilities
│   │   ├── file_ops.py    # File traversal and operations
│   │   ├── helpers.py     # Path resolution utilities
│   │   └── parsers.py     # Argument parsing
│   ├── resources/         # Demo and test files
│   ├── tests/             # Unit tests for all commands
│   └── main.py            # Entry point
├── setup.py               # Package installation
└── README.md              # This file
```


## Usage

```bash
# Run the shell
python -m pyshell.main

# Or if installed
pyshell
```

## Built-in Commands

| Command      | Description                              |
|--------------|------------------------------------------|
| `date`       | Display current date and time            |
| `whoami`     | Print current username                   |
| `hostname`   | Display system hostname                  |
| `timeit`     | Measure execution time of commands       |
| `exit`       | Exit the shell                           |

## Plugin Commands

All plugin commands are dynamically loaded from the `commands/` directory. Each command supports a `-h` or `--help` flag for detailed usage information.

### File Operations

| Command      | Description                        | Key Options                |
|--------------|------------------------------------|----------------------------|
| `cat`        | Concatenate and display files      | `-n`, `-b`, `-s`           |
| `cp`         | Copy files and directories         | `-r`, `-i`, `-v`, `-u`     |
| `mv`         | Move or rename files               | `-i`, `-v`, `-f`           |
| `rm`         | Remove files and directories       | `-r`, `-i`, `-f`, `-v`     |
| `sizeof`     | Display file size in bytes         | -                          |
| `grep`       | Search text patterns in files      | `-i`, `-n`, `-r`, `-v`     |
| `head`       | Display first lines of files       | `-n`                       |
| `tail`       | Display last lines of files        | `-n`                       |
| `find`       | Search for files by name           | `-i`, `-maxdepth`          |

### Directory Operations

| Command      | Description                        | Key Options                |
|--------------|------------------------------------|----------------------------|
| `cd`         | Change directory                   | Supports `.`, `..`, `~`, `-` |
| `ls`         | List directory contents            | `-R`, `-f`                 |
| `mkdir`      | Create directories                 | `-p`, `-v`                 |
| `pwd`        | Print working directory            | `-L`, `-P`                 |
| `rmdir`      | Remove empty directories           | `-p`, `-v`                 |

### Utility

| Command      | Description                        | Key Options                |
|--------------|------------------------------------|----------------------------|
| `clear`      | Clear terminal screen              | -                          |

## Pipelines and Redirections

PyShell supports POSIX-like command pipelines and I/O redirections, allowing you to chain commands and redirect input/output just like in UNIX shells.

### Pipeline Operator (`|`)

Chain commands together, passing output from one command as input to the next:

```bash
PyShell> cat file.txt | grep "pattern" | head -5
PyShell> ls | grep ".py"
PyShell> cat data.txt | grep "error" | tail -10
```

### Output Redirection

**Overwrite** (`>`): Redirect output to a file, overwriting existing content
```bash
PyShell> cat file.txt > output.txt
PyShell> ls -la > directory_listing.txt
```

**Append** (`>>`): Redirect output to a file, appending to existing content
```bash
PyShell> cat file1.txt >> combined.txt
PyShell> cat file2.txt >> combined.txt
```

### Input Redirection

**Input from file** (`<`): Read input from a file instead of stdin
```bash
PyShell> cat < input.txt
PyShell> grep "pattern" < data.txt
```

### Complex Pipeline Examples

```bash
# Find all Python files and count them
PyShell> ls | grep ".py" | tail -5

# Search for pattern and save with line numbers
PyShell> cat large_file.txt | grep -n "ERROR" > errors_found.txt

# Process data through multiple filters
PyShell> cat data.txt | grep "2024" | grep "ERROR" | head -20 > recent_errors.txt
```

## Examples

```bash
# Basic file operations
PyShell> cat file.txt
PyShell> cp file.txt backup.txt
PyShell> mkdir -p new/nested/dir

# Text processing
PyShell> grep -i "pattern" file.txt
PyShell> head -n 20 file.txt
PyShell> find . -name "*.py"

# Pipelines and redirection
PyShell> cat file.txt | grep "error" | tail -10
PyShell> ls | grep ".py" > python_files.txt
PyShell> cat data.txt | head -100 | grep "pattern"

# Measure command execution time
PyShell> timeit ls -R /large/directory

# Navigation
PyShell> cd ~/projects
PyShell> pwd
PyShell> cd -
```

## Architecture

PyShell follows a clean separation of concerns:

- **Core Engine** (`core/shell.py`): Implements the main event loop, command dispatcher, and built-in commands. Handles tokenization, command lookup, and execution flow.
- **Pipeline Handler** (`core/pipeline.py`): Parses and executes command pipelines with I/O redirection. Manages stdin/stdout/stderr streams between commands in a pipeline.
- **Command Plugins** (`commands/`): Each command is a self-contained module with a `run(args, shell)` function. Commands have access to the shell instance for state management and support stdin/stdout for piping.
- **Utilities** (`utils/`): Shared functionality including argument parsing, file traversal, and path resolution used across multiple commands.
- **History Management** (`core/history.py`): Uses Python's `readline` module for persistent command history and line editing capabilities.

## Adding Custom Commands

Create a new Python file in `pyshell/commands/` with a `run(args, shell)` function:

```python
def run(args, shell):
    """
    Your command implementation
    Args:
        args: List of command arguments
        shell: Shell instance (access shell.current_dir)
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    print("Hello from custom command!")
    return 0
```

The command will be automatically available in the shell with the filename as the command name.

## Testing

```bash
# Run all tests
python -m pytest pyshell/tests/

# Run specific test file
python -m pytest pyshell/tests/test_ls_command.py
```

## Requirements

- Python 3.6+
- Standard library only (no external dependencies)
