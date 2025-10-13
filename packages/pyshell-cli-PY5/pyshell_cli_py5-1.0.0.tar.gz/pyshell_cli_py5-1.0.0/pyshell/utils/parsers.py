"""
Argument parsing utilities for PyShell commands

This module provides parsers for:
- Command arguments (ArgumentParser)
- Pipeline and redirection operators (PipelineParser)
"""

from typing import List, Dict, Optional, Union


class ArgumentParser:
    """Simple argument parser for shell commands with support for quoted strings"""

    def __init__(self, args: List[str]):
        self.args = args
        self.flags: Dict[str, Union[str, bool]] = {}
        self.positional: List[str] = []
        self._quoted_indices: List[int] = []  # Track which indices came from quoted strings
        self._parse()

    def _parse(self):
        """Parse arguments into flags and positional arguments
        Handles quoted strings as single arguments"""
        # First, merge quoted strings
        merged_args = self._merge_quoted_args(self.args)

        i = 0
        while i < len(merged_args):
            arg = merged_args[i]

            if arg.startswith('--') and len(arg) > 2:
                # Long flag
                if '=' in arg:
                    key, value = arg[2:].split('=', 1)
                    self.flags[key] = value
                else:
                    key = arg[2:]
                    # Check if next arg is a value (not quoted string = positional)
                    if (i + 1 < len(merged_args) and
                        not merged_args[i + 1].startswith('-') and
                        not self._is_from_quoted_string(i + 1)):
                        self.flags[key] = merged_args[i + 1]
                        i += 1
                    else:
                        self.flags[key] = True
            elif arg.startswith('-') and len(arg) > 1 and not arg.startswith('--'):
                # Short flag(s) - can be combined like -ni meaning -n -i
                flags_str = arg[1:]

                # Special case: numeric shortcuts like -10 for head/tail
                if flags_str.isdigit():
                    # This is a numeric shortcut (e.g., -10 for head/tail)
                    # Treat as boolean flag (value is the number itself)
                    self.flags[flags_str] = True
                elif len(flags_str) == 1:
                    # Single short flag - check if next arg is a value
                    if (i + 1 < len(merged_args) and
                        not merged_args[i + 1].startswith('-') and
                        not self._is_from_quoted_string(i + 1)):
                        self.flags[flags_str] = merged_args[i + 1]
                        i += 1
                    else:
                        self.flags[flags_str] = True
                else:
                    # Multiple combined flags (e.g., -ni = -n -i)
                    # All are treated as boolean flags
                    for flag_char in flags_str:
                        self.flags[flag_char] = True
            else:
                # Positional argument
                self.positional.append(arg)

            i += 1

    def _merge_quoted_args(self, args: List[str]) -> List[str]:
        """Merge arguments that are part of a quoted string
        Handles both single and double quotes

        Note: Since the shell tokenizer keeps quoted strings together,
        we only need to handle complete quoted strings (not split across args)"""
        merged: List[str] = []
        self._quoted_indices.clear()  # Clear tracking list

        for arg in args:
            # Check if arg is a complete quoted string
            if arg.startswith('"') and arg.endswith('"') and len(arg) > 1:
                # Double-quoted string - remove quotes and track
                self._quoted_indices.append(len(merged))
                merged.append(arg[1:-1])
            elif arg.startswith("'") and arg.endswith("'") and len(arg) > 1:
                # Single-quoted string - remove quotes and track
                self._quoted_indices.append(len(merged))
                merged.append(arg[1:-1])
            else:
                # Regular argument (no quotes or incomplete quotes)
                merged.append(arg)

        return merged

    def _is_from_quoted_string(self, index: int) -> bool:
        """Check if the argument at this index came from a quoted string"""
        return index in self._quoted_indices

    def has_flag(self, flag: str) -> bool:
        """Check if a flag is present"""
        return flag in self.flags

    def get_flag_value(self, flag: str, default=None):
        """Get the value of a flag"""
        return self.flags.get(flag, default)

    def get_positional(self, index: int, default=None):
        """Get positional argument by index"""
        if index < len(self.positional):
            return self.positional[index]
        return default

    def validate_flags(self, boolean_flags: Union[List[str], set], flags_with_value: Optional[List[str]] = None):
        """Validate flags - check for invalid flags and incorrect option
        values assigned to switches while parsing"""
        if flags_with_value is None:
            flags_with_value = []
        for flag_name, flag_value in self.flags.items():
            if flag_name in boolean_flags:
                if flag_value is not True:
                    # flag_value should be a string if it's not True
                    if isinstance(flag_value, str):
                        self.positional.insert(0, flag_value)
                    self.flags[flag_name] = True
            elif flag_name not in flags_with_value:
                raise ValueError(f"Invalid option -- '{flag_name}'")


class Redirection:
    """Represents a single I/O redirection"""

    def __init__(self, redir_type: str, target: str):
        """
        Args:
            redir_type: Type of redirection ('>', '>>', '<')
            target: File path for redirection
        """
        self.type = redir_type
        self.target = target


class CommandSegment:
    """Represents a single command in a pipeline with its redirections"""

    def __init__(self, tokens: List[str]):
        self.tokens = tokens
        self.redirections: List[Redirection] = []
        self.stdin_redirect: Optional[Redirection] = None
        self.stdout_redirect: Optional[Redirection] = None


class PipelineParser:
    """Parses command line input into pipeline segments with redirections"""

    # Redirection operators
    REDIR_OPERATORS = ['>>', '>', '<']

    def __init__(self, tokens: List[str]):
        self.tokens = tokens
        self.segments: List[CommandSegment] = []

    def parse(self) -> List[CommandSegment]:
        """
        Parse tokens into command segments separated by pipes

        Returns:
            List of CommandSegment objects
        """
        current_segment_tokens = []

        i = 0
        while i < len(self.tokens):
            token = self.tokens[i]

            # Check for pipe operator
            if token == '|':
                if current_segment_tokens:
                    segment = self._parse_segment(current_segment_tokens)
                    self.segments.append(segment)
                    current_segment_tokens = []
                else:
                    raise ValueError("syntax error near unexpected token '|'")
                i += 1
            else:
                current_segment_tokens.append(token)
                i += 1

        # Add final segment
        if current_segment_tokens:
            segment = self._parse_segment(current_segment_tokens)
            self.segments.append(segment)

        return self.segments

    def _parse_segment(self, tokens: List[str]) -> CommandSegment:
        """
        Parse a single command segment, extracting redirections

        Args:
            tokens: List of tokens for this segment

        Returns:
            CommandSegment with command and redirections separated
        """
        segment = CommandSegment([])
        i = 0

        while i < len(tokens):
            token = tokens[i]

            # Check for redirection operators
            if token in self.REDIR_OPERATORS:
                # Regular redirection - next token is the target file
                if i + 1 >= len(tokens):
                    raise ValueError(f"syntax error near unexpected token '{token}'")

                target = tokens[i + 1]
                redir = Redirection(token, target)

                # Categorize redirection
                if token == '<':
                    if segment.stdin_redirect:
                        raise ValueError("ambiguous redirect")
                    segment.stdin_redirect = redir
                else:  # '>' or '>>'
                    if segment.stdout_redirect:
                        raise ValueError("ambiguous redirect")
                    segment.stdout_redirect = redir

                segment.redirections.append(redir)
                i += 2  # Skip operator and target
            else:
                # Regular command token
                segment.tokens.append(token)
                i += 1

        if not segment.tokens:
            raise ValueError("syntax error: empty command")

        return segment
