"""
Main API class for HookX providing a unified interface.

High-level API that orchestrates scanning, analysis, and reporting
with intelligent defaults and comprehensive error handling.
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union

from ..utils.paths import PathUtils
from ..utils.performance import PerformanceTimer, performance_monitor
from ..utils.validation import ValidationUtils
from .analyzer import ConflictAnalyzer
from .models import ScanResult
from .reporter import HookReporter
from .scanner import HookScanner


class HookX:
    """
    Main API class for HookX - the unified interface for hook analysis.
    
    This class provides a high-level, easy-to-use interface that combines
    scanning, analysis, and reporting into a single cohesive API.
    
    Features:
    - Intelligent path detection and validation
    - Automatic optimization based on scan type
    - Comprehensive error handling and recovery
    - Performance monitoring and metrics
    - Flexible configuration options
    """
    
    def __init__(
        self,
        max_workers: Optional[int] = None,
        enable_cache: bool = True,
        strict_mode: bool = False,
        console_output: bool = True,
    ):
        """
        Initialize HookX with configuration options.
        
        Args:
            max_workers: Maximum worker threads for parallel processing
            enable_cache: Enable intelligent caching for performance
            strict_mode: Treat all conflicts as high severity
            console_output: Enable rich console output
        """
        self.scanner = HookScanner(max_workers=max_workers, enable_cache=enable_cache)
        self.analyzer = ConflictAnalyzer(strict_mode=strict_mode)
        self.reporter = HookReporter() if console_output else None
        
        self.enable_cache = enable_cache
        self.strict_mode = strict_mode
        
        # Performance tracking
        self._scan_history: List[ScanResult] = []
    
    def scan(
        self,
        path: Union[str, Path],
        site_name: Optional[str] = None,
        output_format: str = "table",
        output_file: Optional[Union[str, Path]] = None,
        min_severity: Optional[str] = None,
    ) -> ScanResult:
        """
        Perform comprehensive scan of Frappe hooks with intelligent detection.
        
        Args:
            path: Path to scan (bench, site, or app directory)
            site_name: Site name for app load order (if scanning bench)
            output_format: Output format (table, json, csv, html, markdown)
            output_file: Optional file to save report
            min_severity: Minimum severity level to report
            
        Returns:
            Complete scan result with hooks, conflicts, and metadata
        """
        # Start performance timer
        total_timer = PerformanceTimer("total_scan")
        total_timer.start()
        
        try:
            scan_path = ValidationUtils.validate_scan_path(path)
            if output_format:
                output_format = ValidationUtils.validate_output_format(output_format)
            
            scan_type = self._detect_scan_type(scan_path)
            hooks = self._execute_scan(scan_path, scan_type, site_name)
            conflicts = self.analyzer.analyze_conflicts(hooks)
            
            if min_severity:
                from .models import ConflictSeverity
                min_sev = ValidationUtils.validate_severity_level(min_severity)
                conflicts = self.analyzer.filter_conflicts_by_severity(conflicts, min_sev)
            
            scan_result = ScanResult(
                scan_id=str(uuid.uuid4())[:8],
                timestamp=datetime.now(),
                scan_path=scan_path,
                scan_type=scan_type,
                apps=self._get_scanned_apps(scan_path, scan_type, site_name),
                hooks=hooks,
                conflicts=conflicts,
                scan_duration=total_timer.stop(),
            )
            
            if output_format and self.reporter:
                # Add datetime to filename if output_file specified
                if output_file and output_format != "table":
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_path = Path(output_file)
                    output_file = output_path.parent / f"{output_path.stem}_{timestamp}{output_path.suffix}"
                
                report = self.reporter.generate_report(scan_result, output_format, output_file)
                if output_format == "table":
                    print(report)
                elif output_format == "json":
                    print(report)
                
                # Show file saved message
                if output_file and output_format != "table":
                    print(f"\n📄 Report generated and saved to: {output_file}")
            
            self._scan_history.append(scan_result)
            return scan_result
            
        except (OSError, PermissionError) as e:
            total_timer.stop()
            raise RuntimeError(f"File system error: {e}") from e
        except ValueError as e:
            total_timer.stop()
            raise RuntimeError(f"Invalid input: {e}") from e
        except Exception as e:
            total_timer.stop()
            raise RuntimeError(f"Scan failed: {e}") from e
    
    def scan_bench(
        self,
        bench_path: Union[str, Path],
        site_name: Optional[str] = None,
    ) -> ScanResult:
        """
        Scan entire Frappe bench for hooks.
        
        Args:
            bench_path: Path to Frappe bench directory
            site_name: Optional site name for app load order
            
        Returns:
            Scan result for the bench
        """
        return self.scan(bench_path, site_name=site_name, output_format=None)
    
    def scan_site(
        self,
        site_path: Union[str, Path],
        bench_path: Optional[Union[str, Path]] = None,
    ) -> ScanResult:
        """
        Scan Frappe site with proper app load order.
        
        Args:
            site_path: Path to Frappe site directory
            bench_path: Optional bench path (auto-detected if not provided)
            
        Returns:
            Scan result for the site
        """
        site_path = ValidationUtils.validate_scan_path(site_path)
        
        # Auto-detect bench if not provided
        if not bench_path:
            bench_path = PathUtils.find_bench_root(site_path)
            if not bench_path:
                raise ValueError(f"Could not find bench root for site: {site_path}")
        
        # Use scanner directly for site-specific logic
        hooks = self.scanner.scan_site(site_path, bench_path)
        conflicts = self.analyzer.analyze_conflicts(hooks)
        
        return ScanResult(
            scan_id=str(uuid.uuid4())[:8],
            timestamp=datetime.now(),
            scan_path=site_path,
            scan_type="site",
            hooks=hooks,
            conflicts=conflicts,
            scan_duration=0.0,  # Will be updated by performance timer
        )
    
    def scan_app(self, app_path: Union[str, Path]) -> ScanResult:
        """
        Scan single Frappe app for hooks.
        
        Args:
            app_path: Path to Frappe app directory
            
        Returns:
            Scan result for the app
        """
        app_path = ValidationUtils.validate_scan_path(app_path)
        
        hooks = self.scanner.scan_app(app_path)
        conflicts = self.analyzer.analyze_conflicts(hooks)
        
        return ScanResult(
            scan_id=str(uuid.uuid4())[:8],
            timestamp=datetime.now(),
            scan_path=app_path,
            scan_type="app",
            hooks=hooks,
            conflicts=conflicts,
            scan_duration=0.0,
        )
    
    def validate_hooks(self, path: Union[str, Path]) -> List[str]:
        """
        Validate hooks syntax without full analysis.
        
        Args:
            path: Path to hooks.py file or app directory
            
        Returns:
            List of validation issues (empty if valid)
        """
        path = Path(path)
        
        if path.is_file() and path.name == "hooks.py":
            hooks_file = path
        elif path.is_dir():
            hooks_file = PathUtils.get_hooks_file_path(path)
            if not hooks_file:
                return [f"No hooks.py file found in {path}"]
        else:
            return [f"Invalid path: {path}"]
        
        return self.scanner.validate_hooks_syntax(hooks_file)
    
    def check_conflicts_only(self, path: Union[str, Path], **kwargs) -> bool:
        """
        Quick check for conflicts without full reporting.
        
        Args:
            path: Path to scan
            **kwargs: Additional scan options
            
        Returns:
            True if conflicts found, False otherwise
        """
        result = self.scan(path, output_format=None, **kwargs)
        return len(result.conflicts) > 0
    
    def has_critical_conflicts(self, path: Union[str, Path], **kwargs) -> bool:
        """
        Check for critical conflicts that should fail CI/CD.
        
        Args:
            path: Path to scan
            **kwargs: Additional scan options
            
        Returns:
            True if critical conflicts found, False otherwise
        """
        result = self.scan(path, output_format=None, **kwargs)
        return result.has_critical_conflicts()
    
    def export_for_ci(
        self,
        path: Union[str, Path],
        output_file: Union[str, Path],
        **kwargs
    ) -> bool:
        """
        Export scan results for CI/CD integration.
        
        Args:
            path: Path to scan
            output_file: File to save CI-friendly report
            **kwargs: Additional scan options
            
        Returns:
            True if should fail CI (critical conflicts), False otherwise
        """
        result = self.scan(path, output_format=None, **kwargs)
        
        if self.reporter:
            # Add datetime to filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(output_file)
            final_output = output_path.parent / f"{output_path.stem}_{timestamp}{output_path.suffix}"
            
            result_bool = self.reporter.export_for_ci(result, final_output)
            print(f"\n📄 CI report generated and saved to: {final_output}")
            return result_bool
        else:
            # Fallback JSON export
            import json
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(output_file)
            final_output = output_path.parent / f"{output_path.stem}_{timestamp}{output_path.suffix}"
            
            with open(final_output, 'w') as f:
                json.dump(result.dict(), f, indent=2, default=str)
            print(f"\n📄 CI report generated and saved to: {final_output}")
            return result.has_critical_conflicts()
    
    def get_performance_stats(self) -> dict:
        """Get performance statistics."""
        return performance_monitor.get_all_stats()
    
    def full_scan_report(self, path: Union[str, Path], save_to: Optional[Union[str, Path]] = None) -> dict:
        """
        Complete comprehensive scan with all details - preset function for users.
        
        Args:
            path: Path to Frappe bench, site, or app
            save_to: Optional file path to save detailed report
            
        Returns:
            Complete scan report dictionary with all analysis
        """
        # Perform comprehensive scan
        result = self.scan(path, output_format=None)
        
        # Build comprehensive report
        report = {
            "scan_info": {
                "scan_id": result.scan_id,
                "timestamp": result.timestamp.isoformat(),
                "scan_path": str(result.scan_path),
                "scan_type": result.scan_type,
                "duration": result.scan_duration
            },
            "summary": {
                "total_apps": result.total_apps,
                "total_hooks": result.total_hooks,
                "total_conflicts": result.total_conflicts,
                "has_critical_conflicts": result.has_critical_conflicts()
            },
            "apps": [
                {
                    "name": app.name,
                    "path": str(app.path),
                    "priority": app.priority,
                    "version": app.version,
                    "has_hooks": bool(app.hooks_file)
                } for app in result.apps
            ],
            "hooks_by_type": {
                (hook_type.value if hasattr(hook_type, 'value') else str(hook_type)): [
                    {
                        "app_name": hook.app_name,
                        "hook_name": hook.hook_name,
                        "target": hook.target,
                        "handler": hook.handler,
                        "priority": hook.priority
                    } for hook in hooks
                ] for hook_type, hooks in result.get_hooks_by_type().items() if hooks
            },
            "conflicts": [
                {
                    "severity": conflict.severity.value if hasattr(conflict.severity, 'value') else str(conflict.severity),
                    "hook_type": conflict.hook_type.value if hasattr(conflict.hook_type, 'value') else str(conflict.hook_type),
                    "hook_name": conflict.hook_name,
                    "target": conflict.target,
                    "description": conflict.description,
                    "affected_apps": list(conflict.get_affected_apps()),
                    "winner": conflict.winner.app_name if conflict.winner else None,
                    "resolution_hint": conflict.resolution_hint
                } for conflict in result.conflicts
            ],
            "conflicts_by_severity": {
                (severity.value if hasattr(severity, 'value') else str(severity)): len(conflicts)
                for severity, conflicts in result.get_conflicts_by_severity().items()
                if conflicts
            },
            "hooks_by_app": {
                app_name: len(hooks)
                for app_name, hooks in result.get_hooks_by_app().items()
            }
        }
        
        # Save to file if requested
        if save_to:
            import json
            
            # Add datetime to filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_path = Path(save_to)
            final_path = save_path.parent / f"{save_path.stem}_{timestamp}{save_path.suffix}"
            final_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(final_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"\n📄 Full report generated and saved to: {final_path}")
        
        return report
    
    def quick_scan(self, path: Union[str, Path]) -> dict:
        """
        Quick scan with essential information only.
        
        Args:
            path: Path to scan
            
        Returns:
            Quick summary dictionary
        """
        result = self.scan(path, output_format=None)
        
        from .models import ConflictSeverity
        critical_count = 0
        for c in result.conflicts:
            try:
                severity = c.severity
                if isinstance(severity, str) and severity == 'critical':
                    critical_count += 1
                elif hasattr(severity, 'value') and severity.value == 'critical':
                    critical_count += 1
                elif severity == ConflictSeverity.CRITICAL:
                    critical_count += 1
            except Exception:
                continue
        
        return {
            "status": "critical" if result.has_critical_conflicts() else "ok",
            "apps_scanned": result.total_apps,
            "total_hooks": result.total_hooks,
            "total_conflicts": result.total_conflicts,
            "critical_conflicts": critical_count,
            "scan_duration": result.scan_duration
        }
    
    def get_scan_history(self) -> List[ScanResult]:
        """Get scan history."""
        return self._scan_history.copy()
    
    def clear_cache(self):
        """Clear caches."""
        self.scanner.clear_cache()
        performance_monitor.clear()
        self._scan_history.clear()
    
    def _detect_scan_type(self, path: Path) -> str:
        """Detect the type of path being scanned."""
        if PathUtils.is_frappe_bench(path):
            return "bench"
        elif PathUtils.is_frappe_site(path):
            return "site"
        elif PathUtils.is_frappe_app(path):
            return "app"
        else:
            raise ValueError(f"Unknown Frappe structure type: {path}")
    
    def _execute_scan(self, path: Path, scan_type: str, site_name: Optional[str]) -> list:
        """Execute the appropriate scan based on type."""
        if scan_type == "bench":
            return self.scanner.scan_bench(path, site_name)
        elif scan_type == "site":
            return self.scanner.scan_site(path)
        elif scan_type == "app":
            return self.scanner.scan_app(path)
        else:
            raise ValueError(f"Unknown scan type: {scan_type}")
    
    def _get_scanned_apps(self, path: Path, scan_type: str, site_name: Optional[str]) -> list:
        """Get list of apps that were scanned."""
        if scan_type == "bench":
            if site_name:
                site_path = path / "sites" / site_name
                if site_path.exists():
                    from ..utils.frappe_utils import FrappeUtils
                    return FrappeUtils.get_app_load_order(site_path, path)
            # Fallback to all apps in bench
            app_paths = PathUtils.discover_apps_in_bench(path)
            return [PathUtils.get_app_info_from_path(app_path, i) 
                   for i, app_path in enumerate(app_paths)]
        
        elif scan_type == "site":
            bench_path = PathUtils.find_bench_root(path)
            if bench_path:
                from ..utils.frappe_utils import FrappeUtils
                return FrappeUtils.get_app_load_order(path, bench_path)
            return []
        
        elif scan_type == "app":
            app_info = PathUtils.get_app_info_from_path(path)
            return [app_info] if app_info else []
        
        return []
    
    # Context manager support
    def __enter__(self):
        """Enter context."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        self.clear_cache()