"""
Core module for PyShell - A modular UNIX-like shell written in Python.
"""

__version__ = "0.1.0"

from .shell import PyShell, main
from .pipeline_executor import PipelineExecutor

__all__ = [
    'PyShell',
    'main',
    'PipelineExecutor'
]
