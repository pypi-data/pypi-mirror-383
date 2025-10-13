#!/usr/bin/env python3
"""
Unit tests for parsers.py utility classes
"""

import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# pylint: disable=wrong-import-position
from utils.parsers import ArgumentParser, PipelineParser, CommandSegment, Redirection


class TestArgumentParser(unittest.TestCase):
    """Test ArgumentParser class"""

    def test_parse_positional_args(self):
        """Test parsing positional arguments"""
        parser = ArgumentParser(['file1.txt', 'file2.txt'])
        self.assertEqual(parser.positional, ['file1.txt', 'file2.txt'])
        self.assertEqual(parser.get_positional(0), 'file1.txt')
        self.assertEqual(parser.get_positional(1), 'file2.txt')

    def test_parse_short_flags(self):
        """Test parsing short flags"""
        parser = ArgumentParser(['-r', 'file.txt'])
        self.assertTrue(parser.has_flag('r'))
        # Note: ArgumentParser treats next non-flag as value for the flag
        # So 'file.txt' is treated as value for '-r', not a positional arg

    def test_parse_long_flags(self):
        """Test parsing long flags"""
        parser = ArgumentParser(['--recursive', '--verbose', 'file.txt'])
        self.assertTrue(parser.has_flag('recursive'))
        self.assertTrue(parser.has_flag('verbose'))

    def test_parse_flag_with_value(self):
        """Test parsing flags with values"""
        parser = ArgumentParser(['-n', '10', 'file.txt'])
        self.assertEqual(parser.get_flag_value('n'), '10')
        self.assertEqual(parser.positional, ['file.txt'])

    def test_parse_long_flag_with_equals(self):
        """Test parsing long flag with = syntax"""
        parser = ArgumentParser(['--lines=20', 'file.txt'])
        self.assertEqual(parser.get_flag_value('lines'), '20')

    def test_get_positional_with_default(self):
        """Test getting positional argument with default"""
        parser = ArgumentParser(['file.txt'])
        self.assertEqual(parser.get_positional(0), 'file.txt')
        self.assertEqual(parser.get_positional(1, 'default'), 'default')
        self.assertIsNone(parser.get_positional(2))

    def test_get_flag_value_with_default(self):
        """Test getting flag value with default"""
        parser = ArgumentParser(['-r'])
        self.assertTrue(parser.get_flag_value('r'))
        self.assertEqual(parser.get_flag_value('n', 10), 10)

    def test_validate_boolean_flags(self):
        """Test validating boolean flags"""
        parser = ArgumentParser(['-r', '-v', 'file.txt'])
        parser.validate_flags(boolean_flags=['r', 'v'])
        self.assertTrue(parser.has_flag('r'))
        self.assertTrue(parser.has_flag('v'))

    def test_validate_flags_with_value(self):
        """Test validating flags that require values"""
        parser = ArgumentParser(['-n', '10', 'file.txt'])
        parser.validate_flags(boolean_flags=[], flags_with_value=['n'])
        self.assertEqual(parser.get_flag_value('n'), '10')

    def test_validate_invalid_flag(self):
        """Test validation fails on invalid flag"""
        parser = ArgumentParser(['-x', 'file.txt'])
        with self.assertRaises(ValueError) as context:
            parser.validate_flags(boolean_flags=['r', 'v'], flags_with_value=['n'])
        self.assertIn("Invalid option", str(context.exception))

    def test_empty_args(self):
        """Test parsing empty arguments"""
        parser = ArgumentParser([])
        self.assertEqual(parser.positional, [])
        self.assertEqual(parser.flags, {})

    def test_mixed_args(self):
        """Test parsing mixed arguments"""
        parser = ArgumentParser(['file1.txt', '-r', '--verbose', 'file2.txt'])
        self.assertTrue(parser.has_flag('r'))
        self.assertTrue(parser.has_flag('verbose'))
        # Positional args before flags are preserved
        self.assertIn('file1.txt', parser.positional)

    def test_quoted_string_double_quotes(self):
        """Test parsing double-quoted strings"""
        parser = ArgumentParser(['"hello world"', 'file.txt'])
        self.assertEqual(parser.positional, ['hello world', 'file.txt'])

    def test_quoted_string_single_quotes(self):
        """Test parsing single-quoted strings"""
        parser = ArgumentParser(["'hello world'", 'file.txt'])
        self.assertEqual(parser.positional, ['hello world', 'file.txt'])

    def test_quoted_string_not_treated_as_flag_value(self):
        """Test that quoted strings are positional args, not flag values"""
        parser = ArgumentParser(['-n', '"10"', 'file.txt'])
        # The quoted "10" should be a positional arg, not the value for -n
        self.assertEqual(parser.get_flag_value('n'), True)
        self.assertIn('10', parser.positional)

    def test_combined_short_flags(self):
        """Test parsing combined short flags like -ni"""
        parser = ArgumentParser(['-ni', 'file.txt'])
        self.assertTrue(parser.has_flag('n'))
        self.assertTrue(parser.has_flag('i'))
        self.assertEqual(parser.positional, ['file.txt'])

    def test_numeric_shortcut_flag(self):
        """Test parsing numeric shortcuts like -10"""
        parser = ArgumentParser(['-10', 'file.txt'])
        self.assertTrue(parser.has_flag('10'))
        self.assertEqual(parser.positional, ['file.txt'])

    def test_empty_quoted_string(self):
        """Test parsing empty quoted strings"""
        parser = ArgumentParser(['""', 'file.txt'])
        self.assertEqual(parser.positional, ['', 'file.txt'])

    def test_merge_quoted_args_method(self):
        """Test _merge_quoted_args internal method"""
        parser = ArgumentParser([])
        merged = parser._merge_quoted_args(['"hello"', "'world'", 'test'])
        self.assertEqual(merged, ['hello', 'world', 'test'])
        self.assertIn(0, parser._quoted_indices)
        self.assertIn(1, parser._quoted_indices)
        self.assertNotIn(2, parser._quoted_indices)

    def test_is_from_quoted_string_method(self):
        """Test _is_from_quoted_string internal method"""
        parser = ArgumentParser(['"quoted"', 'notquoted'])
        self.assertTrue(parser._is_from_quoted_string(0))
        self.assertFalse(parser._is_from_quoted_string(1))


class TestRedirection(unittest.TestCase):
    """Test Redirection class"""

    def test_redirection_creation(self):
        """Test creating a Redirection object"""
        redir = Redirection('>', 'output.txt')
        self.assertEqual(redir.type, '>')
        self.assertEqual(redir.target, 'output.txt')

    def test_redirection_append(self):
        """Test append redirection"""
        redir = Redirection('>>', 'output.txt')
        self.assertEqual(redir.type, '>>')
        self.assertEqual(redir.target, 'output.txt')

    def test_redirection_input(self):
        """Test input redirection"""
        redir = Redirection('<', 'input.txt')
        self.assertEqual(redir.type, '<')
        self.assertEqual(redir.target, 'input.txt')


class TestCommandSegment(unittest.TestCase):
    """Test CommandSegment class"""

    def test_command_segment_creation(self):
        """Test creating a CommandSegment"""
        segment = CommandSegment(['cat', 'file.txt'])
        self.assertEqual(segment.tokens, ['cat', 'file.txt'])
        self.assertEqual(segment.redirections, [])
        self.assertIsNone(segment.stdin_redirect)
        self.assertIsNone(segment.stdout_redirect)

    def test_command_segment_with_redirections(self):
        """Test CommandSegment with redirections"""
        segment = CommandSegment(['cat'])
        redir_in = Redirection('<', 'input.txt')
        redir_out = Redirection('>', 'output.txt')

        segment.stdin_redirect = redir_in
        segment.stdout_redirect = redir_out
        segment.redirections = [redir_in, redir_out]

        self.assertEqual(segment.stdin_redirect.target, 'input.txt')
        self.assertEqual(segment.stdout_redirect.target, 'output.txt')
        self.assertEqual(len(segment.redirections), 2)


class TestPipelineParser(unittest.TestCase):
    """Test PipelineParser class"""

    def test_simple_command(self):
        """Test parsing a simple command"""
        parser = PipelineParser(['cat', 'file.txt'])
        segments = parser.parse()

        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0].tokens, ['cat', 'file.txt'])

    def test_pipeline_two_commands(self):
        """Test parsing pipeline with two commands"""
        parser = PipelineParser(['cat', 'file.txt', '|', 'grep', 'pattern'])
        segments = parser.parse()

        self.assertEqual(len(segments), 2)
        self.assertEqual(segments[0].tokens, ['cat', 'file.txt'])
        self.assertEqual(segments[1].tokens, ['grep', 'pattern'])

    def test_pipeline_three_commands(self):
        """Test parsing pipeline with three commands"""
        parser = PipelineParser(['cat', 'file.txt', '|', 'head', '-10', '|', 'tail', '-5'])
        segments = parser.parse()

        self.assertEqual(len(segments), 3)
        self.assertEqual(segments[0].tokens, ['cat', 'file.txt'])
        self.assertEqual(segments[1].tokens, ['head', '-10'])
        self.assertEqual(segments[2].tokens, ['tail', '-5'])

    def test_output_redirection(self):
        """Test parsing output redirection"""
        parser = PipelineParser(['cat', 'file.txt', '>', 'output.txt'])
        segments = parser.parse()

        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0].tokens, ['cat', 'file.txt'])
        self.assertIsNotNone(segments[0].stdout_redirect)
        self.assertEqual(segments[0].stdout_redirect.type, '>')
        self.assertEqual(segments[0].stdout_redirect.target, 'output.txt')

    def test_append_redirection(self):
        """Test parsing append redirection"""
        parser = PipelineParser(['cat', 'file.txt', '>>', 'output.txt'])
        segments = parser.parse()

        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0].tokens, ['cat', 'file.txt'])
        self.assertIsNotNone(segments[0].stdout_redirect)
        self.assertEqual(segments[0].stdout_redirect.type, '>>')
        self.assertEqual(segments[0].stdout_redirect.target, 'output.txt')

    def test_input_redirection(self):
        """Test parsing input redirection"""
        parser = PipelineParser(['cat', '<', 'input.txt'])
        segments = parser.parse()

        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0].tokens, ['cat'])
        self.assertIsNotNone(segments[0].stdin_redirect)
        self.assertEqual(segments[0].stdin_redirect.type, '<')
        self.assertEqual(segments[0].stdin_redirect.target, 'input.txt')

    def test_multiple_redirections(self):
        """Test parsing command with both input and output redirection"""
        parser = PipelineParser(['cat', '<', 'input.txt', '>', 'output.txt'])
        segments = parser.parse()

        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0].tokens, ['cat'])
        self.assertIsNotNone(segments[0].stdin_redirect)
        self.assertIsNotNone(segments[0].stdout_redirect)
        self.assertEqual(segments[0].stdin_redirect.target, 'input.txt')
        self.assertEqual(segments[0].stdout_redirect.target, 'output.txt')

    def test_pipeline_with_redirection(self):
        """Test parsing pipeline with redirection on last command"""
        parser = PipelineParser(['cat', 'file.txt', '|', 'grep', 'pattern', '>', 'output.txt'])
        segments = parser.parse()

        self.assertEqual(len(segments), 2)
        self.assertEqual(segments[0].tokens, ['cat', 'file.txt'])
        self.assertEqual(segments[1].tokens, ['grep', 'pattern'])
        self.assertIsNotNone(segments[1].stdout_redirect)
        self.assertEqual(segments[1].stdout_redirect.target, 'output.txt')

    def test_empty_command_error(self):
        """Test that empty command raises error"""
        parser = PipelineParser([])
        segments = parser.parse()
        # Empty input should result in empty segments list
        self.assertEqual(len(segments), 0)

    def test_pipe_at_start_error(self):
        """Test that pipe at start raises error"""
        parser = PipelineParser(['|', 'cat', 'file.txt'])
        with self.assertRaises(ValueError) as context:
            parser.parse()
        self.assertIn('syntax error', str(context.exception).lower())

    def test_consecutive_pipes_error(self):
        """Test that consecutive pipes raise error"""
        parser = PipelineParser(['cat', 'file.txt', '|', '|', 'grep', 'pattern'])
        with self.assertRaises(ValueError) as context:
            parser.parse()
        self.assertIn('syntax error', str(context.exception).lower())

    def test_redirection_without_target_error(self):
        """Test that redirection without target raises error"""
        parser = PipelineParser(['cat', 'file.txt', '>'])
        with self.assertRaises(ValueError) as context:
            parser.parse()
        self.assertIn('syntax error', str(context.exception).lower())

    def test_ambiguous_input_redirect_error(self):
        """Test that multiple input redirections raise error"""
        parser = PipelineParser(['cat', '<', 'input1.txt', '<', 'input2.txt'])
        with self.assertRaises(ValueError) as context:
            parser.parse()
        self.assertIn('ambiguous redirect', str(context.exception).lower())

    def test_ambiguous_output_redirect_error(self):
        """Test that multiple output redirections raise error"""
        parser = PipelineParser(['cat', 'file.txt', '>', 'out1.txt', '>', 'out2.txt'])
        with self.assertRaises(ValueError) as context:
            parser.parse()
        self.assertIn('ambiguous redirect', str(context.exception).lower())

    def test_complex_pipeline(self):
        """Test parsing complex pipeline with multiple commands and redirections"""
        parser = PipelineParser([
            'cat', '<', 'input.txt', '|',
            'grep', 'pattern', '|',
            'head', '-10', '|',
            'tail', '-5', '>', 'output.txt'
        ])
        segments = parser.parse()

        self.assertEqual(len(segments), 4)
        self.assertEqual(segments[0].tokens, ['cat'])
        self.assertEqual(segments[0].stdin_redirect.target, 'input.txt')
        self.assertEqual(segments[1].tokens, ['grep', 'pattern'])
        self.assertEqual(segments[2].tokens, ['head', '-10'])
        self.assertEqual(segments[3].tokens, ['tail', '-5'])
        self.assertEqual(segments[3].stdout_redirect.target, 'output.txt')


if __name__ == '__main__':
    unittest.main()
