"""
Command-line interface for HookX with rich features and usability.

Provides a comprehensive CLI with multiple commands, options, and
intelligent defaults for developer productivity.
"""

from .main import main
from .commands import (
    scan_command,
    validate_command,
    check_command,
    export_command,
)

__all__ = [
    "main",
    "scan_command",
    "validate_command", 
    "check_command",
    "export_command",
]