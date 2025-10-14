"""Debug utility module.

Messages are printed only when debug mode is enabled via ``-d`` or ``--debug``.
"""

import sys

# Global debug flag. Initially enabled if ``-d`` or ``--debug`` is in ``sys.argv``.
debug_mode = any(arg in ["-d", "--debug"] for arg in sys.argv)


def set_debug_mode(enabled=True):
    """Explicitly enable or disable debug mode."""
    global debug_mode
    debug_mode = enabled
    if debug_mode:
        debug_print("[debug] Debug mode enabled")


def debug_print(*args, **kwargs):
    """Print messages only when debug mode is active."""
    if debug_mode:
        print(*args, **kwargs)


def error_print(*args, **kwargs):
    """Print error messages unconditionally."""
    print(*args, **kwargs)
