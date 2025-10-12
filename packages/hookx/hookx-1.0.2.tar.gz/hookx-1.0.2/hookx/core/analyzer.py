"""
Advanced conflict analyzer for HookX with intelligent conflict detection.

Analyzes hook definitions to detect conflicts, overlaps, and potential issues
with sophisticated algorithms and comprehensive reporting.
"""

from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple

from ..utils.performance import timed, performance_monitor
from .models import ConflictReport, ConflictSeverity, HookDefinition, HookType


class ConflictAnalyzer:
    """
    Intelligent analyzer for detecting hook conflicts and overlaps.
    
    Features:
    - Multi-level conflict detection (critical, high, medium, low)
    - App priority-aware analysis
    - Performance-optimized algorithms
    - Comprehensive conflict categorization
    """
    
    def __init__(self, strict_mode: bool = False):
        """
        Initialize conflict analyzer.
        
        Args:
            strict_mode: If True, treat all conflicts as critical
        """
        self.strict_mode = strict_mode
        
        # Conflict severity rules based on hook types
        self.severity_rules = {
            HookType.OVERRIDE_WHITELISTED_METHODS: ConflictSeverity.CRITICAL,
            HookType.OVERRIDE_DOCTYPE_CLASS: ConflictSeverity.CRITICAL,
            HookType.DOC_EVENTS: ConflictSeverity.HIGH,
            HookType.SCHEDULER_EVENTS: ConflictSeverity.MEDIUM,
            HookType.BOOT_SESSION: ConflictSeverity.MEDIUM,
            HookType.WEBSITE_ROUTE_RULES: ConflictSeverity.HIGH,
            HookType.WEBSITE_REDIRECTS: ConflictSeverity.MEDIUM,
            HookType.JINJA: ConflictSeverity.LOW,
            HookType.FIXTURES: ConflictSeverity.LOW,
            HookType.CUSTOM: ConflictSeverity.MEDIUM,
        }
    
    @timed("analyze_conflicts")
    def analyze_conflicts(self, hooks: List[HookDefinition]) -> List[ConflictReport]:
        """
        Analyze hooks for conflicts and generate comprehensive reports.
        
        Args:
            hooks: List of hook definitions to analyze
            
        Returns:
            List of conflict reports found
        """
        if not hooks:
            return []
        
        performance_monitor.start_timer("conflict_analysis")
        
        try:
            # Group hooks by conflict key for efficient analysis
            hook_groups = self._group_hooks_by_conflict_key(hooks)
            
            conflicts = []
            
            # Analyze each group for conflicts
            for conflict_key, hook_list in hook_groups.items():
                if len(hook_list) > 1:
                    conflict = self._analyze_hook_group(conflict_key, hook_list)
                    if conflict:
                        conflicts.append(conflict)
            
            # Sort conflicts by severity and app priority
            conflicts.sort(key=lambda c: (
                self._severity_priority(c.severity),
                min(h.priority for h in c.conflicting_hooks)
            ))
            
            return conflicts
            
        finally:
            performance_monitor.stop_timer("conflict_analysis")
    
    def _group_hooks_by_conflict_key(self, hooks: List[HookDefinition]) -> Dict[str, List[HookDefinition]]:
        """Group hooks by their conflict detection key."""
        groups = defaultdict(list)
        
        for hook in hooks:
            conflict_key = hook.get_conflict_key()
            groups[conflict_key].append(hook)
        
        return dict(groups)
    
    def _analyze_hook_group(self, conflict_key: str, hooks: List[HookDefinition]) -> Optional[ConflictReport]:
        """Analyze a group of hooks with the same conflict key."""
        if len(hooks) < 2:
            return None
        
        # Sort hooks by priority (lower number = higher priority)
        sorted_hooks = sorted(hooks, key=lambda h: h.priority)
        
        # Determine conflict severity
        hook_type = hooks[0].hook_type
        base_severity = self.severity_rules.get(hook_type, ConflictSeverity.MEDIUM)
        
        # Adjust severity based on conflict characteristics
        severity = self._calculate_conflict_severity(hooks, base_severity)
        
        # Override in strict mode
        if self.strict_mode and severity != ConflictSeverity.CRITICAL:
            severity = ConflictSeverity.HIGH
        
        # Determine winner (highest priority hook)
        winner = sorted_hooks[0]
        
        # Generate description and resolution hint
        description = self._generate_conflict_description(hooks, winner)
        resolution_hint = self._generate_resolution_hint(hooks, hook_type)
        
        return ConflictReport(
            conflict_key=conflict_key,
            hook_type=hook_type,
            hook_name=hooks[0].hook_name,
            target=hooks[0].target,
            severity=severity,
            conflicting_hooks=hooks,
            winner=winner,
            description=description,
            resolution_hint=resolution_hint,
        )
    
    def _calculate_conflict_severity(self, hooks: List[HookDefinition], base_severity: ConflictSeverity) -> ConflictSeverity:
        """Calculate conflict severity based on hook characteristics."""
        # Factors that increase severity
        severity_factors = []
        
        # Different apps involved
        app_names = {h.app_name for h in hooks}
        if len(app_names) > 2:
            severity_factors.append("multiple_apps")
        
        # Core Frappe apps involved
        core_apps = {"frappe", "erpnext", "hrms", "payments"}
        if any(app in core_apps for app in app_names):
            severity_factors.append("core_app_involved")
        
        # Override hooks are always critical
        if hooks[0].hook_type in [HookType.OVERRIDE_WHITELISTED_METHODS, HookType.OVERRIDE_DOCTYPE_CLASS]:
            return ConflictSeverity.CRITICAL
        
        # Same handler in different apps (likely copy-paste error)
        handlers = {h.handler for h in hooks}
        if len(handlers) == 1:
            severity_factors.append("identical_handlers")
        
        # Adjust severity based on factors
        if "core_app_involved" in severity_factors:
            if base_severity == ConflictSeverity.LOW:
                return ConflictSeverity.MEDIUM
            elif base_severity == ConflictSeverity.MEDIUM:
                return ConflictSeverity.HIGH
        
        if "multiple_apps" in severity_factors and len(app_names) > 3:
            if base_severity in [ConflictSeverity.LOW, ConflictSeverity.MEDIUM]:
                return ConflictSeverity.HIGH
        
        return base_severity
    
    def _generate_conflict_description(self, hooks: List[HookDefinition], winner: HookDefinition) -> str:
        """Generate human-readable conflict description."""
        app_names = [h.app_name for h in hooks]
        hook_name = hooks[0].hook_name
        target = hooks[0].target
        
        if target:
            base_desc = f"Multiple apps define {hook_name} hook for {target}"
        else:
            base_desc = f"Multiple apps define {hook_name} hook"
        
        apps_desc = f"Apps involved: {', '.join(app_names)}"
        winner_desc = f"Winner: {winner.app_name} (priority {winner.priority})"
        
        return f"{base_desc}. {apps_desc}. {winner_desc}."
    
    def _generate_resolution_hint(self, hooks: List[HookDefinition], hook_type: HookType) -> str:
        """Generate resolution hint based on conflict type."""
        if hook_type == HookType.OVERRIDE_WHITELISTED_METHODS:
            return "Consider consolidating method overrides into a single app or using different method names."
        
        elif hook_type == HookType.OVERRIDE_DOCTYPE_CLASS:
            return "DocType class overrides should be unique. Consider using inheritance or composition patterns."
        
        elif hook_type == HookType.DOC_EVENTS:
            return "Multiple doc event handlers will execute in app priority order. Ensure handlers are idempotent."
        
        elif hook_type == HookType.SCHEDULER_EVENTS:
            return "Multiple scheduler events may cause duplicate execution. Consider consolidating or using different schedules."
        
        elif hook_type == HookType.WEBSITE_ROUTE_RULES:
            return "Conflicting route rules may cause routing issues. Ensure routes are unique or properly prioritized."
        
        else:
            return "Review hook definitions and consider consolidating or using different hook names."
    
    def _severity_priority(self, severity: ConflictSeverity) -> int:
        """Get numeric priority for severity sorting."""
        priority_map = {
            ConflictSeverity.CRITICAL: 0,
            ConflictSeverity.HIGH: 1,
            ConflictSeverity.MEDIUM: 2,
            ConflictSeverity.LOW: 3,
            ConflictSeverity.INFO: 4,
        }
        return priority_map.get(severity, 5)
    
    @timed("analyze_app_dependencies")
    def analyze_app_dependencies(self, hooks: List[HookDefinition]) -> Dict[str, Set[str]]:
        """
        Analyze potential app dependencies based on hook patterns.
        
        Args:
            hooks: List of hook definitions
            
        Returns:
            Dictionary mapping app names to their potential dependencies
        """
        dependencies = defaultdict(set)
        
        # Group hooks by app
        app_hooks = defaultdict(list)
        for hook in hooks:
            app_hooks[hook.app_name].append(hook)
        
        # Analyze each app's hooks for dependency patterns
        for app_name, app_hook_list in app_hooks.items():
            for hook in app_hook_list:
                # Check if handler references other apps
                handler_parts = hook.handler.split('.')
                if len(handler_parts) > 1:
                    potential_app = handler_parts[0]
                    if potential_app != app_name and potential_app in app_hooks:
                        dependencies[app_name].add(potential_app)
        
        return dict(dependencies)
    
    @timed("analyze_hook_coverage")
    def analyze_hook_coverage(self, hooks: List[HookDefinition]) -> Dict[str, Dict[str, int]]:
        """
        Analyze hook coverage across apps and DocTypes.
        
        Args:
            hooks: List of hook definitions
            
        Returns:
            Coverage statistics by app and hook type
        """
        coverage = defaultdict(lambda: defaultdict(int))
        
        for hook in hooks:
            try:
                hook_type = hook.hook_type
                if isinstance(hook_type, str):
                    hook_type_key = hook_type
                elif hasattr(hook_type, 'value'):
                    hook_type_key = hook_type.value
                else:
                    hook_type_key = str(hook_type)
                coverage[hook.app_name][hook_type_key] += 1
            except Exception:
                continue
            
            # Track DocType coverage for doc_events
            if hook_type == HookType.DOC_EVENTS and hook.target:
                doctype_key = f"doctype_{hook.target}"
                coverage[hook.app_name][doctype_key] += 1
        
        return dict(coverage)
    
    def get_conflict_summary(self, conflicts: List[ConflictReport]) -> Dict[str, any]:
        """
        Generate summary statistics for conflicts.
        
        Args:
            conflicts: List of conflict reports
            
        Returns:
            Summary statistics dictionary
        """
        if not conflicts:
            return {
                'total_conflicts': 0,
                'by_severity': {},
                'by_hook_type': {},
                'affected_apps': set(),
                'critical_count': 0,
            }
        
        # Count by severity
        by_severity = defaultdict(int)
        for conflict in conflicts:
            try:
                severity = conflict.severity
                if isinstance(severity, str):
                    severity_key = severity
                elif hasattr(severity, 'value'):
                    severity_key = severity.value
                else:
                    severity_key = str(severity)
                by_severity[severity_key] += 1
            except Exception:
                continue
        
        # Count by hook type
        by_hook_type = defaultdict(int)
        for conflict in conflicts:
            try:
                hook_type = conflict.hook_type
                if isinstance(hook_type, str):
                    hook_type_key = hook_type
                elif hasattr(hook_type, 'value'):
                    hook_type_key = hook_type.value
                else:
                    hook_type_key = str(hook_type)
                by_hook_type[hook_type_key] += 1
            except Exception:
                continue
        
        # Get affected apps
        affected_apps = set()
        for conflict in conflicts:
            affected_apps.update(conflict.get_affected_apps())
        
        # Count critical conflicts
        critical_count = sum(1 for c in conflicts if c.severity == ConflictSeverity.CRITICAL)
        
        return {
            'total_conflicts': len(conflicts),
            'by_severity': dict(by_severity),
            'by_hook_type': dict(by_hook_type),
            'affected_apps': affected_apps,
            'critical_count': critical_count,
            'has_critical': critical_count > 0,
        }
    
    def filter_conflicts_by_severity(self, conflicts: List[ConflictReport], min_severity: ConflictSeverity) -> List[ConflictReport]:
        """Filter conflicts by minimum severity level."""
        severity_order = [
            ConflictSeverity.CRITICAL,
            ConflictSeverity.HIGH, 
            ConflictSeverity.MEDIUM,
            ConflictSeverity.LOW,
            ConflictSeverity.INFO,
        ]
        
        min_index = severity_order.index(min_severity)
        return [c for c in conflicts if severity_order.index(c.severity) <= min_index]
    
    def filter_conflicts_by_apps(self, conflicts: List[ConflictReport], app_names: Set[str]) -> List[ConflictReport]:
        """Filter conflicts involving specific apps."""
        return [c for c in conflicts if c.get_affected_apps().intersection(app_names)]
    
    def filter_conflicts_by_hook_type(self, conflicts: List[ConflictReport], hook_types: Set[HookType]) -> List[ConflictReport]:
        """Filter conflicts by hook types."""
        return [c for c in conflicts if c.hook_type in hook_types]