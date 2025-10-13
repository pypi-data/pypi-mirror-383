#!/usr/bin/env python3
"""
PyShell - A modular UNIX-like shell written in Python.

Main entry point for the shell application.
"""

import sys
import argparse
try:
    from .core.shell import PyShell  # type: ignore[import-not-found]
except ImportError:
    from core.shell import PyShell


def main():
    """
    Main entry point for PyShell.
    """
    parser = argparse.ArgumentParser(
        description='PyShell - A lightweight, modular Python shell',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py              Start interactive shell
  python main.py --debug      Start with debug logging
        """
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='PyShell 0.1.0'
    )

    args = parser.parse_args()

    try:
        # Create and run the shell
        shell = PyShell()
        shell.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

