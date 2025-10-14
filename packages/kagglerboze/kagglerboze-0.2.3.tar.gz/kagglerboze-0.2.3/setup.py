"""
Backward compatibility wrapper for setuptools.

Modern Python packaging uses pyproject.toml for configuration.
This file exists only for backward compatibility with older tools.
"""

from setuptools import setup

setup()
