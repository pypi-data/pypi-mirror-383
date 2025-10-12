"""
Data models for HookX using Pydantic for validation and performance.

Defines all data structures used throughout the library for type safety,
validation, and optimal serialization performance.
"""

from __future__ import annotations

import os
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from pydantic import BaseModel, Field, validator


class HookType(str, Enum):
    """Enumeration of supported Frappe hook types for categorization."""
    
    DOC_EVENTS = "doc_events"
    OVERRIDE_WHITELISTED_METHODS = "override_whitelisted_methods"
    OVERRIDE_DOCTYPE_CLASS = "override_doctype_class"
    SCHEDULER_EVENTS = "scheduler_events"
    BOOT_SESSION = "boot_session"
    WEBSITE_ROUTE_RULES = "website_route_rules"
    WEBSITE_REDIRECTS = "website_redirects"
    JINJA = "jinja"
    FIXTURES = "fixtures"
    CUSTOM = "custom"


class ConflictSeverity(str, Enum):
    """Severity levels for hook conflicts to prioritize resolution."""
    
    CRITICAL = "critical"    # Will cause runtime errors
    HIGH = "high"           # Likely to cause issues
    MEDIUM = "medium"       # May cause unexpected behavior
    LOW = "low"            # Informational, unlikely to cause issues
    INFO = "info"          # Just informational


class AppInfo(BaseModel):
    """Information about a Frappe app including metadata and paths."""
    
    name: str = Field(..., description="App name")
    path: Path = Field(..., description="Absolute path to app directory")
    hooks_file: Optional[Path] = Field(None, description="Path to hooks.py file")
    priority: int = Field(0, description="App load priority (lower = higher priority)")
    version: Optional[str] = Field(None, description="App version if available")
    installed: bool = Field(True, description="Whether app is installed in site")
    
    @validator('path')
    def validate_path_exists(cls, v):
        """Ensure app path exists."""
        if not v.exists():
            raise ValueError(f"App path does not exist: {v}")
        return v
    
    @validator('hooks_file')
    def validate_hooks_file(cls, v, values):
        """Validate hooks.py file exists if specified."""
        if v and not v.exists():
            # Auto-detect hooks.py in app directory
            app_path = values.get('path')
            if app_path:
                hooks_path = app_path / 'hooks.py'
                if hooks_path.exists():
                    return hooks_path
        return v
    
    class Config:
        """Pydantic configuration for optimal performance."""
        arbitrary_types_allowed = True
        use_enum_values = True


class HookDefinition(BaseModel):
    """Represents a single hook definition found in hooks.py."""
    
    app_name: str = Field(..., description="Name of the app defining this hook")
    hook_type: HookType = Field(..., description="Type/category of the hook")
    hook_name: str = Field(..., description="Name of the hook (e.g., 'before_save')")
    target: Optional[str] = Field(None, description="Target DocType or method")
    handler: str = Field(..., description="Handler function/method path")
    line_number: int = Field(0, description="Line number in hooks.py")
    file_path: Path = Field(..., description="Path to hooks.py file")
    priority: int = Field(0, description="App priority for conflict resolution")
    raw_definition: Optional[Dict[str, Any]] = Field(None, description="Raw hook data")
    
    @validator('handler')
    def validate_handler_format(cls, v):
        """Ensure handler is in proper module.function format."""
        if not v or '.' not in v:
            raise ValueError(f"Invalid handler format: {v}")
        return v
    
    def get_conflict_key(self) -> str:
        """Generate unique key for conflict detection."""
        if self.target:
            return f"{self.hook_type}:{self.hook_name}:{self.target}"
        return f"{self.hook_type}:{self.hook_name}"
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
        use_enum_values = True


class ConflictReport(BaseModel):
    """Report of conflicts found between hook definitions."""
    
    conflict_key: str = Field(..., description="Unique identifier for this conflict")
    hook_type: HookType = Field(..., description="Type of hooks in conflict")
    hook_name: str = Field(..., description="Name of the conflicting hook")
    target: Optional[str] = Field(None, description="Target DocType/method if applicable")
    severity: ConflictSeverity = Field(..., description="Severity level of conflict")
    conflicting_hooks: List[HookDefinition] = Field(..., description="All conflicting hooks")
    winner: Optional[HookDefinition] = Field(None, description="Hook that will execute (highest priority)")
    description: str = Field(..., description="Human-readable conflict description")
    resolution_hint: Optional[str] = Field(None, description="Suggested resolution")
    
    @validator('conflicting_hooks')
    def validate_multiple_hooks(cls, v):
        """Ensure we have multiple hooks for a conflict."""
        if len(v) < 2:
            raise ValueError("Conflict must have at least 2 hooks")
        return v
    
    def get_affected_apps(self) -> Set[str]:
        """Get set of app names involved in this conflict."""
        return {hook.app_name for hook in self.conflicting_hooks}
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True


class ScanResult(BaseModel):
    """Complete result of a HookX scan operation."""
    
    # Scan metadata
    scan_id: str = Field(..., description="Unique scan identifier")
    timestamp: datetime = Field(default_factory=datetime.now, description="Scan timestamp")
    scan_path: Path = Field(..., description="Path that was scanned")
    scan_type: str = Field(..., description="Type of scan (site/bench/app)")
    
    # Scanned data
    apps: List[AppInfo] = Field(default_factory=list, description="Apps that were scanned")
    hooks: List[HookDefinition] = Field(default_factory=list, description="All hooks found")
    conflicts: List[ConflictReport] = Field(default_factory=list, description="Conflicts detected")
    
    # Statistics
    total_apps: int = Field(0, description="Total number of apps scanned")
    total_hooks: int = Field(0, description="Total number of hooks found")
    total_conflicts: int = Field(0, description="Total number of conflicts")
    
    # Performance metrics
    scan_duration: float = Field(0.0, description="Scan duration in seconds")
    
    @validator('total_apps', always=True)
    def set_total_apps(cls, v, values):
        """Auto-calculate total apps."""
        apps = values.get('apps', [])
        return len(apps)
    
    @validator('total_hooks', always=True) 
    def set_total_hooks(cls, v, values):
        """Auto-calculate total hooks."""
        hooks = values.get('hooks', [])
        return len(hooks)
    
    @validator('total_conflicts', always=True)
    def set_total_conflicts(cls, v, values):
        """Auto-calculate total conflicts."""
        conflicts = values.get('conflicts', [])
        return len(conflicts)
    
    def get_conflicts_by_severity(self) -> Dict[ConflictSeverity, List[ConflictReport]]:
        """Group conflicts by severity level."""
        result = {severity: [] for severity in ConflictSeverity}
        for conflict in self.conflicts:
            try:
                # Ensure severity is proper enum
                severity = conflict.severity
                if isinstance(severity, str):
                    try:
                        severity = ConflictSeverity(severity)
                    except ValueError:
                        # Skip invalid severity values
                        continue
                elif hasattr(severity, 'value'):
                    # Already an enum, use as-is
                    pass
                else:
                    # Unknown type, skip
                    continue
                result[severity].append(conflict)
            except Exception:
                continue
        return result
    
    def get_hooks_by_app(self) -> Dict[str, List[HookDefinition]]:
        """Group hooks by app name."""
        result = {}
        for hook in self.hooks:
            if hook.app_name not in result:
                result[hook.app_name] = []
            result[hook.app_name].append(hook)
        return result
    
    def get_hooks_by_type(self) -> Dict[HookType, List[HookDefinition]]:
        """Group hooks by type."""
        result = {hook_type: [] for hook_type in HookType}
        for hook in self.hooks:
            try:
                # Ensure hook_type is proper enum
                hook_type = hook.hook_type
                if isinstance(hook_type, str):
                    try:
                        hook_type = HookType(hook_type)
                    except ValueError:
                        # Skip invalid hook types
                        continue
                elif hasattr(hook_type, 'value'):
                    # Already an enum, use as-is
                    pass
                else:
                    # Unknown type, skip
                    continue
                result[hook_type].append(hook)
            except Exception:
                # Skip problematic hooks
                continue
        return result
    
    def has_critical_conflicts(self) -> bool:
        """Check if scan found any critical conflicts."""
        for conflict in self.conflicts:
            try:
                severity = conflict.severity
                # Handle both string and enum values
                if isinstance(severity, str):
                    if severity == "critical":
                        return True
                elif hasattr(severity, 'value'):
                    if severity.value == "critical":
                        return True
                elif severity == ConflictSeverity.CRITICAL:
                    return True
            except Exception:
                continue
        return False
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            Path: lambda v: str(v),
        }