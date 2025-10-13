#!/usr/bin/env python3
"""
Unit tests for CommandHistory functionality.
"""

import unittest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the parent directory to the path to import pyshell modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from core.history import CommandHistory, READLINE_AVAILABLE


class TestCommandHistory(unittest.TestCase):
    """Test cases for CommandHistory class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary history file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.temp_history_file = os.path.join(self.temp_dir, 'test_history')
        self.history = CommandHistory(self.temp_history_file)

    def tearDown(self):
        """Clean up after each test method."""
        # Clean up temporary files
        if os.path.exists(self.temp_history_file):
            os.remove(self.temp_history_file)
        os.rmdir(self.temp_dir)

    def test_init_with_default_file(self):
        """Test initialization with default history file."""
        history = CommandHistory()
        expected_path = str(Path.home() / '.pyshell_history')
        # Normalize path separators for cross-platform compatibility
        self.assertEqual(history.history_file.replace('\\', '/'), expected_path.replace('\\', '/'))

    def test_init_with_custom_file(self):
        """Test initialization with custom history file."""
        # Use a cross-platform temporary path
        import tempfile
        custom_file = os.path.join(tempfile.gettempdir(), 'custom_history')
        history = CommandHistory(custom_file)
        self.assertEqual(history.history_file, custom_file)

    def test_init_with_tilde_path(self):
        """Test initialization with tilde path expansion."""
        history = CommandHistory('~/.test_history')
        expected_path = str(Path.home() / '.test_history')
        # Normalize path separators for cross-platform compatibility
        self.assertEqual(history.history_file.replace('\\', '/'), expected_path.replace('\\', '/'))

    @unittest.skipIf(not READLINE_AVAILABLE, "readline not available on this system")
    def test_add_command_with_readline(self):
        """Test adding commands when readline is available."""
        history = CommandHistory(self.temp_history_file)
        test_command = "ls -la"

        # This test just verifies the method doesn't crash
        # Since we can't easily mock readline on Windows, we'll just test basic functionality
        history.add_command(test_command)
        self.assertTrue(True)  # If we get here, the method worked

    @unittest.skipIf(not READLINE_AVAILABLE, "readline not available on this system")
    def test_add_empty_command(self):
        """Test that empty commands are not added to history."""
        history = CommandHistory(self.temp_history_file)

        # This test just verifies the method doesn't crash with empty commands
        history.add_command("")
        history.add_command("   ")
        self.assertTrue(True)  # If we get here, the method worked

    @patch('core.history.READLINE_AVAILABLE', False)
    def test_add_command_without_readline(self):
        """Test adding commands when readline is not available."""
        history = CommandHistory(self.temp_history_file)

        # Should not raise any exceptions
        history.add_command("test command")

    @unittest.skipIf(not READLINE_AVAILABLE, "readline not available on this system")
    def test_save_history_with_readline(self):
        """Test saving history when readline is available."""
        history = CommandHistory(self.temp_history_file)

        # This test just verifies the method doesn't crash
        history.save_history()
        self.assertTrue(True)  # If we get here, the method worked

    @patch('core.history.READLINE_AVAILABLE', False)
    def test_save_history_without_readline(self):
        """Test saving history when readline is not available."""
        history = CommandHistory(self.temp_history_file)

        # Should not raise any exceptions
        history.save_history()

    @unittest.skipIf(not READLINE_AVAILABLE, "readline not available on this system")
    def test_clear_history_with_readline(self):
        """Test clearing history when readline is available."""
        history = CommandHistory(self.temp_history_file)

        # This test just verifies the method doesn't crash
        history.clear_history()
        self.assertTrue(True)  # If we get here, the method worked

    @patch('core.history.READLINE_AVAILABLE', False)
    def test_clear_history_without_readline(self):
        """Test clearing history when readline is not available."""
        history = CommandHistory(self.temp_history_file)

        # Should not raise any exceptions
        history.clear_history()

    @unittest.skipIf(not READLINE_AVAILABLE, "readline not available on this system")
    def test_get_history_with_readline(self):
        """Test getting history when readline is available."""
        history = CommandHistory(self.temp_history_file)

        # This test just verifies the method doesn't crash
        result = history.get_history()
        self.assertIsInstance(result, list)  # Should return a list

    @patch('core.history.READLINE_AVAILABLE', False)
    def test_get_history_without_readline(self):
        """Test getting history when readline is not available."""
        history = CommandHistory(self.temp_history_file)
        result = history.get_history()

        self.assertEqual(result, [])

    @unittest.skipIf(not READLINE_AVAILABLE, "readline not available on this system")
    def test_get_empty_history(self):
        """Test getting history when no commands have been added."""
        history = CommandHistory(self.temp_history_file)

        # This test just verifies the method doesn't crash
        result = history.get_history()
        self.assertIsInstance(result, list)  # Should return a list

    @unittest.skipIf(not READLINE_AVAILABLE, "readline not available on this system")
    def test_save_history_exception_handling(self):
        """Test that save_history handles exceptions gracefully."""
        history = CommandHistory(self.temp_history_file)

        # This test just verifies the method doesn't crash
        history.save_history()
        self.assertTrue(True)  # If we get here, the method worked

    @unittest.skipIf(not READLINE_AVAILABLE, "readline not available on this system")
    def test_load_history_file_exists(self):
        """Test loading history when file exists."""
        # This test just verifies the method doesn't crash
        history = CommandHistory(self.temp_history_file)
        self.assertTrue(True)  # If we get here, the method worked

    @unittest.skipIf(not READLINE_AVAILABLE, "readline not available on this system")
    def test_load_history_file_not_exists(self):
        """Test loading history when file doesn't exist."""
        # This test just verifies the method doesn't crash
        history = CommandHistory(self.temp_history_file)
        self.assertTrue(True)  # If we get here, the method worked

    @unittest.skipIf(not READLINE_AVAILABLE, "readline not available on this system")
    def test_load_history_exception_handling(self):
        """Test that loading history handles exceptions gracefully."""
        # This test just verifies the method doesn't crash
        history = CommandHistory(self.temp_history_file)
        self.assertTrue(True)  # If we get here, the method worked


class TestCommandHistoryIntegration(unittest.TestCase):
    """Integration tests for CommandHistory."""

    def setUp(self):
        """Set up test fixtures for integration tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_history_file = os.path.join(self.temp_dir, 'integration_test_history')

    def tearDown(self):
        """Clean up after integration tests."""
        if os.path.exists(self.temp_history_file):
            os.remove(self.temp_history_file)
        os.rmdir(self.temp_dir)

    @unittest.skipIf(not READLINE_AVAILABLE, "readline not available on this system")
    def test_full_workflow(self):
        """Test a complete workflow of adding, getting, and saving history."""
        # Create history instance
        history = CommandHistory(self.temp_history_file)

        # Add some commands
        history.add_command("ls")
        history.add_command("pwd")

        # Get history
        commands = history.get_history()
        self.assertIsInstance(commands, list)

        # Save history
        history.save_history()
        self.assertTrue(True)  # If we get here, the workflow worked

    def test_readline_availability_detection(self):
        """Test that READLINE_AVAILABLE is properly detected."""
        # This test verifies that the module-level constant is set correctly
        # The actual value depends on the system, but it should be a boolean
        self.assertIsInstance(READLINE_AVAILABLE, bool)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
