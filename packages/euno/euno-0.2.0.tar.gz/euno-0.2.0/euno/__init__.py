"""
Euno SDK - A Python library and CLI tool for interacting with Euno instances.

This package provides both programmatic access to Euno functionality
and a command-line interface for common operations.
"""

from .version import __version__

__all__ = ["__version__", "hello_world", "get_version", "config", "api_client"]

from .core import hello_world, get_version
from .config import config
from .api import api_client
