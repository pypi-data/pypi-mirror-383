"""
Core modules for frappeye - the heart of hook analysis and conflict detection.

This package contains the main business logic for scanning Frappe apps,
analyzing hooks, detecting conflicts, and generating reports.
"""

from .scanner import HookScanner
from .analyzer import ConflictAnalyzer  
from .reporter import HookReporter
from .api import FrappEye
from .models import (
    HookDefinition,
    ConflictReport,
    ScanResult,
    AppInfo,
    HookType,
    ConflictSeverity,
)

__all__ = [
    "HookScanner",
    "ConflictAnalyzer", 
    "HookReporter",
    "FrappEye",
    "HookDefinition",
    "ConflictReport",
    "ScanResult", 
    "AppInfo",
    "HookType",
    "ConflictSeverity",
]