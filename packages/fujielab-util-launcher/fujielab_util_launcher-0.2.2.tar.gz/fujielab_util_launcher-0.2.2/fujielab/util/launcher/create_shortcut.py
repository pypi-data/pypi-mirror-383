"""
Shortcut creation helpers.

This module keeps backwards compatibility while delegating the platform
specific implementations to dedicated modules for readability.
"""

from .create_shortcut_windows import create_windows_shortcut  # noqa: F401
from .create_shortcut_macos import create_macos_shortcut  # noqa: F401

__all__ = ["create_windows_shortcut", "create_macos_shortcut"]
