"""
Command history management for PyShell using readline module.

This provides:
- Up/Down arrow to navigate history
- History persistence across sessions
- Tab completion (bonus feature)

Uses pathlib for cross-platform file operations.
"""

from pathlib import Path

# readline module for command history and line editing
try:
    import readline
    READLINE_AVAILABLE = True
except ImportError:
    # readline not available on Windows by default
    READLINE_AVAILABLE = False
    print("Warning: readline not available. History features disabled.")


class CommandHistory:
    """
    Manages command history with up/down arrow navigation.

    Uses readline module for:
    - Arrow key navigation (up/down through history)
    - History persistence (saves to file)
    - Line editing (left/right arrows, backspace, etc.)
    """

    def __init__(self, history_file=None):
        """
        Initialize command history.

        Args:
            history_file: Path to save history (default: ~/.pyshell_history)
        """

        if history_file is None:
            home = str(Path.home())
            self.history_file = home.rstrip('/') + '/.pyshell_history'
        else:
            if history_file.startswith('~'):
                home = str(Path.home())
                self.history_file = history_file.replace('~', home, 1)
            else:
                self.history_file = history_file

        if READLINE_AVAILABLE:
            self._setup_readline()

    def _setup_readline(self):
        """Configure readline for history and editing."""
        # Set history file length
        readline.set_history_length(1000)

        try:
            Path(self.history_file).stat()
            file_exists = True
        except FileNotFoundError:
            file_exists = False
        except Exception:
            file_exists = False

        # Load existing history if file exists
        if file_exists:
            try:
                readline.read_history_file(self.history_file)
            except Exception as e:
                print(f"Warning: Could not load history: {e}")

        # Enable tab completion (optional bonus)
        # readline.parse_and_bind("tab: complete")

    def add_command(self, command):
        """
        Add a command to history.

        Args:
            command: Command string to add
        """
        if READLINE_AVAILABLE and command.strip():
            readline.add_history(command)

    def save_history(self):
        """Save history to file."""
        if READLINE_AVAILABLE:
            try:
                readline.write_history_file(self.history_file)
            except Exception as e:
                print(f"Warning: Could not save history: {e}")

    def clear_history(self):
        """Clear all history."""
        if READLINE_AVAILABLE:
            readline.clear_history()

    def get_history(self):
        """
        Get all history as a list.

        Returns:
            List of command strings
        """
        if not READLINE_AVAILABLE:
            return []

        history = []
        for i in range(readline.get_current_history_length()):
            history.append(readline.get_history_item(i + 1))
        return history


# Simple usage example
if __name__ == "__main__":
    history = CommandHistory()

    print("Command History Demo")
    print("Type commands and use Up/Down arrows to navigate")
    print("Type 'exit' to quit\n")

    while True:
        try:
            cmd = input("PyShell> ")
            if cmd == "exit":
                break

            history.add_command(cmd)
            print(f"Executed: {cmd}")

        except (KeyboardInterrupt, EOFError):
            break

    # Save history on exit
    history.save_history()
    print("\nHistory saved!")
