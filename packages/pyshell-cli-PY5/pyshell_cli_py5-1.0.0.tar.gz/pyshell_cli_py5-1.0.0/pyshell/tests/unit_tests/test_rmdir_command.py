#!/usr/bin/env python3
"""
Unit tests for rmdir command
"""

import unittest
import sys
import os
import tempfile
from io import StringIO
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from commands import rmdir
import shutil


class TestRmdirCommand(unittest.TestCase):
    """Test cases for rmdir command plugin."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.empty_dir = self.test_dir / 'empty_dir'
        self.non_empty_dir = self.test_dir / 'non_empty_dir'

        # Create a mock shell object with current_dir attribute
        self.mock_shell = MagicMock()
        self.mock_shell.current_dir = self.test_dir

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up test directories
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)
    @patch('sys.stdout', new_callable=StringIO)
    def test_rmdir_help_flag(self, mock_stdout):
        """Test rmdir with -h flag."""
        rmdir.run(['-h'], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertIn('Usage: rmdir [options] [directory...]', output)
        self.assertIn('Remove empty directories', output)
        self.assertIn('Options:', output)
        self.assertIn('-h, --help', output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_rmdir_help_long_flag(self, mock_stdout):
        """Test rmdir with --help flag."""
        rmdir.run(['--help'], self.mock_shell)
        output = mock_stdout.getvalue()

        self.assertIn('Usage: rmdir [options] [directory...]', output)
        self.assertIn('Examples:', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_rmdir_missing_operand(self, mock_stderr):
        """Test rmdir with no arguments."""
        rmdir.run([], self.mock_shell)
        output = mock_stderr.getvalue()

        self.assertIn('rmdir: missing operand', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_rmdir_invalid_argument_dot(self, mock_stderr):
        """Test rmdir with '.' as argument."""
        rmdir.run(['.'], self.mock_shell)
        output = mock_stderr.getvalue()

        self.assertIn("rmdir: failed to remove '.': Invalid argument", output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_rmdir_invalid_argument_dotdot(self, mock_stderr):
        """Test rmdir with '..' as argument."""
        rmdir.run(['..'], self.mock_shell)
        output = mock_stderr.getvalue()

        self.assertIn("rmdir: failed to remove '..': Invalid argument", output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_rmdir_invalid_argument_empty(self, mock_stderr):
        """Test rmdir with empty string as argument."""
        rmdir.run([''], self.mock_shell)
        output = mock_stderr.getvalue()

        self.assertIn("rmdir: failed to remove '': Invalid argument", output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_rmdir_file_not_found(self, mock_stderr):
        """Test rmdir with non-existent directory."""
        with patch.object(Path, 'exists', return_value=False):
            rmdir.run(['nonexistent'], self.mock_shell)
            output = mock_stderr.getvalue()

            self.assertIn("rmdir: failed to remove 'nonexistent': No such file or directory", output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_rmdir_not_a_directory(self, mock_stderr):
        """Test rmdir with file instead of directory."""
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'is_dir', return_value=False):
                rmdir.run(['file.txt'], self.mock_shell)
                output = mock_stderr.getvalue()

                self.assertIn("rmdir: failed to remove 'file.txt': Not a directory", output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_rmdir_symlink(self, mock_stderr):
        """Test rmdir with symbolic link."""
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'is_dir', return_value=True):
                with patch.object(Path, 'is_symlink', return_value=True):
                    rmdir.run(['symlink_dir'], self.mock_shell)
                    output = mock_stderr.getvalue()

                    self.assertIn("rmdir: failed to remove 'symlink_dir': Is a symbolic link", output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_rmdir_current_directory_safety_check(self, mock_stderr):
        """Test rmdir trying to remove a directory with safety check."""
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'is_dir', return_value=True):
                with patch.object(Path, 'is_symlink', return_value=False):
                    with patch('commands.rmdir.is_safe_to_remove', return_value=(False, "Cannot remove current working directory")):
                        rmdir.run(['some_dir'], self.mock_shell)
                        output = mock_stderr.getvalue()

                        self.assertIn("rmdir: failed to remove 'some_dir': Cannot remove current working directory", output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_rmdir_directory_not_empty(self, mock_stderr):
        """Test rmdir with non-empty directory."""
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'is_dir', return_value=True):
                with patch.object(Path, 'is_symlink', return_value=False):
                    with patch('commands.rmdir.is_safe_to_remove', return_value=(True, None)):
                        with patch('commands.rmdir.safe_remove_directory', return_value=False):
                            rmdir.run(['non_empty_dir'], self.mock_shell)
                            output = mock_stderr.getvalue()

                            self.assertIn("rmdir: failed to remove 'non_empty_dir': Directory not empty", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_rmdir_success(self, mock_stdout):
        """Test successful rmdir operation."""
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'is_dir', return_value=True):
                with patch.object(Path, 'is_symlink', return_value=False):
                    with patch('commands.rmdir.is_safe_to_remove', return_value=(True, None)):
                        with patch('commands.rmdir.safe_remove_directory', return_value=True):
                            rmdir.run(['empty_dir'], self.mock_shell)
                            output = mock_stdout.getvalue()

                            # Should not have any error messages
                            self.assertNotIn('failed to remove', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_rmdir_permission_denied(self, mock_stderr):
        """Test rmdir with permission denied."""
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'is_dir', return_value=True):
                with patch.object(Path, 'is_symlink', return_value=False):
                    with patch('commands.rmdir.is_safe_to_remove', return_value=(True, None)):
                        with patch('commands.rmdir.safe_remove_directory', side_effect=PermissionError()):
                            rmdir.run(['restricted_dir'], self.mock_shell)
                            output = mock_stderr.getvalue()

                            self.assertIn("rmdir: failed to remove 'restricted_dir': Permission denied", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_rmdir_multiple_directories(self, mock_stdout):
        """Test rmdir with multiple directory arguments."""
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'is_dir', return_value=True):
                with patch.object(Path, 'is_symlink', return_value=False):
                    with patch('commands.rmdir.is_safe_to_remove', return_value=(True, None)):
                        with patch('commands.rmdir.safe_remove_directory', return_value=True):
                            rmdir.run(['dir1', 'dir2', 'dir3'], self.mock_shell)
                            output = mock_stdout.getvalue()

                            # Should not have any error messages
                            self.assertNotIn('failed to remove', output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_rmdir_invalid_path(self, mock_stderr):
        """Test rmdir with invalid path."""
        with patch.object(Path, 'resolve', side_effect=OSError()):
            rmdir.run(['invalid_path'], self.mock_shell)
            output = mock_stderr.getvalue()

            self.assertIn("rmdir: failed to remove 'invalid_path': Invalid path", output)

    @patch('sys.stderr', new_callable=StringIO)
    def test_rmdir_device_busy(self, mock_stderr):
        """Test rmdir with device busy error."""
        error = OSError()
        error.errno = 16  # Device or resource busy

        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'is_dir', return_value=True):
                with patch.object(Path, 'is_symlink', return_value=False):
                    with patch('commands.rmdir.is_safe_to_remove', return_value=(True, None)):
                        with patch('commands.rmdir.safe_remove_directory', side_effect=error):
                            rmdir.run(['busy_dir'], self.mock_shell)
                            output = mock_stderr.getvalue()

                            self.assertIn("rmdir: failed to remove 'busy_dir': Device or resource busy", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_rmdir_force_flag(self, mock_stdout):
        """Test rmdir with -f flag (force - ignore errors)."""
        with patch.object(Path, 'exists', return_value=False):
            result = rmdir.run(['-f', 'nonexistent'], self.mock_shell)
            output = mock_stdout.getvalue()

            # With force flag, should return 1 but not print error message
            self.assertEqual(result, 1)
            self.assertEqual(output.strip(), '')

    @patch('sys.stdout', new_callable=StringIO)
    def test_rmdir_force_long_flag(self, mock_stdout):
        """Test rmdir with --force flag (ignore errors)."""
        with patch.object(Path, 'exists', return_value=False):
            result = rmdir.run(['--force', 'nonexistent'], self.mock_shell)
            output = mock_stdout.getvalue()

            # With force flag, should return 1 but not print error message
            self.assertEqual(result, 1)
            self.assertEqual(output.strip(), '')

    @patch('sys.stdout', new_callable=StringIO)
    def test_rmdir_force_flag_with_invalid_argument(self, mock_stdout):
        """Test rmdir with -f flag handles invalid arguments silently."""
        result = rmdir.run(['-f', '.'], self.mock_shell)
        output = mock_stdout.getvalue()

        # Should suppress error message with force flag
        self.assertNotIn('Invalid argument', output)
        self.assertEqual(result, 1)

    @patch('sys.stdout', new_callable=StringIO)
    def test_rmdir_force_flag_with_permission_error(self, mock_stdout):
        """Test rmdir with -f flag handles permission errors silently."""
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'is_dir', return_value=True):
                with patch.object(Path, 'is_symlink', return_value=False):
                    with patch('commands.rmdir.is_safe_to_remove', return_value=(True, None)):
                        with patch('commands.rmdir.safe_remove_directory', side_effect=PermissionError()):
                            result = rmdir.run(['-f', 'restricted_dir'], self.mock_shell)
                            output = mock_stdout.getvalue()

                            # Should suppress error message with force flag
                            self.assertNotIn('Permission denied', output)
                            self.assertEqual(result, 1)

    @patch('sys.stdout', new_callable=StringIO)
    def test_rmdir_force_flag_with_not_directory(self, mock_stdout):
        """Test rmdir with -f flag handles not a directory error silently."""
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'is_dir', return_value=False):
                result = rmdir.run(['-f', 'file.txt'], self.mock_shell)
                output = mock_stdout.getvalue()

                # Should suppress error message with force flag
                self.assertNotIn('Not a directory', output)
                self.assertEqual(result, 1)

    @patch('sys.stdout', new_callable=StringIO)
    def test_rmdir_force_flag_with_symlink(self, mock_stdout):
        """Test rmdir with -f flag handles symlink error silently."""
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'is_dir', return_value=True):
                with patch.object(Path, 'is_symlink', return_value=True):
                    result = rmdir.run(['-f', 'symlink_dir'], self.mock_shell)
                    output = mock_stdout.getvalue()

                    # Should suppress error message with force flag
                    self.assertNotIn('Is a symbolic link', output)
                    self.assertEqual(result, 1)

    @patch('sys.stdout', new_callable=StringIO)
    def test_rmdir_force_flag_with_directory_not_empty(self, mock_stdout):
        """Test rmdir with -f flag handles directory not empty error silently."""
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'is_dir', return_value=True):
                with patch.object(Path, 'is_symlink', return_value=False):
                    with patch('commands.rmdir.is_safe_to_remove', return_value=(True, None)):
                        with patch('commands.rmdir.safe_remove_directory', return_value=False):
                            result = rmdir.run(['-f', 'non_empty_dir'], self.mock_shell)
                            output = mock_stdout.getvalue()

                            # Should suppress error message with force flag
                            self.assertNotIn('Directory not empty', output)
                            self.assertEqual(result, 1)

    @patch('sys.stderr', new_callable=StringIO)
    def test_rmdir_without_force_flag_shows_errors(self, mock_stderr):
        """Test rmdir without force flag shows error messages."""
        with patch.object(Path, 'exists', return_value=False):
            result = rmdir.run(['nonexistent'], self.mock_shell)
            output = mock_stderr.getvalue()

            # Without force flag, should show error message
            self.assertEqual(result, 1)
            self.assertIn('No such file or directory', output)


class TestRmdirIsSafeToRemove(unittest.TestCase):
    """Test cases for is_safe_to_remove function."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.target_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up test directories
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir, ignore_errors=True)
        if self.target_dir.exists():
            shutil.rmtree(self.target_dir, ignore_errors=True)
    def test_is_safe_to_remove_current_directory(self):
        """Test is_safe_to_remove with current directory."""
        is_safe, error_msg = rmdir.is_safe_to_remove(self.test_dir, self.test_dir)

        self.assertFalse(is_safe)
        self.assertIn('Cannot remove current working directory', error_msg)

    def test_is_safe_to_remove_current_inside_target(self):
        """Test is_safe_to_remove when current directory is inside target."""
        # Create a scenario where current is inside target
        # Make test_dir a subdirectory of target_dir
        parent_dir = self.target_dir
        child_dir = self.target_dir / 'subdir'

        is_safe, error_msg = rmdir.is_safe_to_remove(parent_dir, child_dir)

        self.assertFalse(is_safe)
        self.assertIn('Cannot remove directory: current directory is inside it', error_msg)

    def test_is_safe_to_remove_dot_directory(self):
        """Test is_safe_to_remove with '.' directory."""
        dot_dir = Path('.')
        with patch.object(Path, 'resolve') as mock_resolve:
            # Mock resolve to return different paths so they're not equal
            def resolve_side_effect():
                if mock_resolve.call_count == 1:
                    return Path(tempfile.mkdtemp())  # target.resolve()
                else:
                    return self.test_dir  # current_dir.resolve()

            mock_resolve.side_effect = resolve_side_effect
            with patch.object(Path, 'name', '.'):
                is_safe, error_msg = rmdir.is_safe_to_remove(dot_dir, self.test_dir)

                self.assertFalse(is_safe)
                self.assertIn("Cannot remove '.'", error_msg)

    def test_is_safe_to_remove_dotdot_directory(self):
        """Test is_safe_to_remove with '..' directory."""
        dotdot_dir = Path('..')
        with patch.object(Path, 'resolve') as mock_resolve:
            # Mock resolve to return different paths so they're not equal
            def resolve_side_effect():
                if mock_resolve.call_count == 1:
                    return Path(tempfile.mkdtemp())  # target.resolve()
                return self.test_dir  # current_dir.resolve()

            mock_resolve.side_effect = resolve_side_effect
            with patch.object(Path, 'name', '..'):
                is_safe, error_msg = rmdir.is_safe_to_remove(dotdot_dir, self.test_dir)

                self.assertFalse(is_safe)
                self.assertIn("Cannot remove '..'", error_msg)

    def test_is_safe_to_remove_root_directory(self):
        """Test is_safe_to_remove with root directory."""
        root_dir = Path('/')
        with patch.object(Path, 'resolve') as mock_resolve:
            # Mock resolve to return root for target, different for current_dir
            def resolve_side_effect():
                if mock_resolve.call_count == 1:
                    return Path('/')  # target.resolve()
                return self.test_dir  # current_dir.resolve()

            mock_resolve.side_effect = resolve_side_effect
            # Mock relative_to to raise ValueError so it doesn't trigger "inside" check
            with patch.object(Path, 'relative_to', side_effect=ValueError()):
                with patch.object(Path, 'parent', Path('/')):
                    is_safe, error_msg = rmdir.is_safe_to_remove(root_dir, self.test_dir)

                    self.assertFalse(is_safe)
                    self.assertIn('Cannot remove root directory', error_msg)

    def test_is_safe_to_remove_system_directory(self):
        """Test is_safe_to_remove with system directory."""
        system_dir = Path('/bin')
        is_safe, error_msg = rmdir.is_safe_to_remove(system_dir, self.test_dir)

        self.assertFalse(is_safe)
        self.assertIn('Cannot remove system directory', error_msg)

    def test_is_safe_to_remove_safe_directory(self):
        """Test is_safe_to_remove with safe directory."""
        safe_dir = Path(tempfile.mkdtemp())
        is_safe, error_msg = rmdir.is_safe_to_remove(safe_dir, self.test_dir)

        self.assertTrue(is_safe)
        self.assertIsNone(error_msg)


class TestRmdirPrintHelp(unittest.TestCase):
    """Test cases for rmdir help function."""

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_help_function(self, mock_stdout):
        """Test the print_help function directly."""
        rmdir.print_help()
        output = mock_stdout.getvalue()

        self.assertIn('Usage: rmdir [options] [directory...]', output)
        self.assertIn('Remove empty directories', output)
        self.assertIn('-h, --help', output)
        self.assertIn('Examples:', output)
        self.assertIn('Note:', output)


if __name__ == '__main__':
    unittest.main(verbosity=2)
