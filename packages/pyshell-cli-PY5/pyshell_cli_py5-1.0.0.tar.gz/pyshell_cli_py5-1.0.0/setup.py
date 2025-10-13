#!/usr/bin/env python3
"""
Setup configuration for PyShell package distribution to PyPI
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="pyshell-cli-PY5",
    version="1.0.0",
    author="PyShell Contributors-PrachiY,KetakiD,Deekshita",
    author_email="2106ketaki@gmail.com",
    description="A modular UNIX-like shell implementation in Python with plugin architecture",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pyshell",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Shells",
        "Topic :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Natural Language :: English",
    ],
    keywords="shell, terminal, command-line, unix, bash, cli, educational, commands",
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies - pure Python standard library only!
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "coverage>=6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pyshell=pyshell.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "pyshell": [
            "resources/*",
        ],
    },
    zip_safe=False,
    project_urls={
        "Bug Reports": "https://github.com/yourusername/pyshell/issues",
        "Source": "https://github.com/yourusername/pyshell",
        "Documentation": "https://github.com/yourusername/pyshell/blob/main/README.md",
    },
)
