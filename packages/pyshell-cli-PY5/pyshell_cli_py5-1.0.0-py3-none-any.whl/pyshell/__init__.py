"""
PyShell - A modular UNIX-like shell implementation in Python.

A lightweight, educational shell with plugin-based command architecture.
"""

__version__ = "1.0.0"
__author__ = "PyShell Contributors"
__license__ = "MIT"

# Make main components easily accessible
from .core.shell import PyShell
from .main import main

__all__ = ["PyShell", "main", "__version__"]

