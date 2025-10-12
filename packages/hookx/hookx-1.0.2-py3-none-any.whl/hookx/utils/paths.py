"""
Path utilities for hook with optimized file system operations.

Provides high-performance path resolution, validation, and Frappe-specific
directory structure handling with caching for repeated operations.
"""

import os
import sys
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Set, Tuple, Union

from ..core.models import AppInfo


class PathUtils:
    """Optimized path utilities for Frappe environments with intelligent caching."""
    
    # Cache for expensive file system operations
    _path_cache: dict = {}
    _app_cache: dict = {}
    
    @staticmethod
    @lru_cache(maxsize=256)
    def normalize_path(path: Union[str, Path]) -> Path:
        """Normalize and resolve path with caching for performance."""
        if isinstance(path, str):
            path = Path(path)
        return path.resolve()
    
    @staticmethod
    @lru_cache(maxsize=128)
    def is_frappe_bench(path: Union[str, Path]) -> bool:
        """Check if path is a valid Frappe bench directory."""
        path = PathUtils.normalize_path(path)
        
        # Check for bench indicators
        bench_indicators = [
            path / "sites",
            path / "apps", 
            path / "config",
            path / "env",
        ]
        
        # At least sites and apps should exist
        return (path / "sites").exists() and (path / "apps").exists()
    
    @staticmethod
    @lru_cache(maxsize=128)
    def is_frappe_site(path: Union[str, Path]) -> bool:
        """Check if path is a valid Frappe site directory."""
        path = PathUtils.normalize_path(path)
        
        # Check for site indicators
        site_indicators = [
            path / "site_config.json",
            path / "private",
            path / "public",
        ]
        
        return (path / "site_config.json").exists()
    
    @staticmethod
    @lru_cache(maxsize=128) 
    def is_frappe_app(path: Union[str, Path]) -> bool:
        """Check if path is a valid Frappe app directory."""
        path = PathUtils.normalize_path(path)
        
        # Check for app indicators - Frappe apps have nested structure
        # Look for app_name/app_name/__init__.py or app_name/__init__.py
        nested_init = path / path.name / "__init__.py"
        root_init = path / "__init__.py"
        
        # Valid if either structure exists
        return nested_init.exists() or root_init.exists()
    
    @staticmethod
    def find_bench_root(start_path: Union[str, Path]) -> Optional[Path]:
        """Find Frappe bench root by traversing up the directory tree."""
        current = PathUtils.normalize_path(start_path)
        
        # Traverse up to find bench root
        for _ in range(10):  # Limit traversal depth
            if PathUtils.is_frappe_bench(current):
                return current
            
            parent = current.parent
            if parent == current:  # Reached filesystem root
                break
            current = parent
        
        return None
    
    @staticmethod
    def find_site_root(start_path: Union[str, Path]) -> Optional[Path]:
        """Find Frappe site root by traversing up the directory tree."""
        current = PathUtils.normalize_path(start_path)
        
        # Traverse up to find site root
        for _ in range(10):  # Limit traversal depth
            if PathUtils.is_frappe_site(current):
                return current
                
            parent = current.parent
            if parent == current:  # Reached filesystem root
                break
            current = parent
        
        return None
    
    @staticmethod
    def get_apps_directory(bench_path: Union[str, Path]) -> Optional[Path]:
        """Get apps directory from bench path."""
        bench_path = PathUtils.normalize_path(bench_path)
        apps_dir = bench_path / "apps"
        
        return apps_dir if apps_dir.exists() else None
    
    @staticmethod
    def get_sites_directory(bench_path: Union[str, Path]) -> Optional[Path]:
        """Get sites directory from bench path.""" 
        bench_path = PathUtils.normalize_path(bench_path)
        sites_dir = bench_path / "sites"
        
        return sites_dir if sites_dir.exists() else None
    
    @staticmethod
    def discover_apps_in_bench(bench_path: Union[str, Path]) -> List[Path]:
        """Discover all Frappe apps in a bench directory."""
        cache_key = f"apps_in_bench:{bench_path}"
        if cache_key in PathUtils._path_cache:
            return PathUtils._path_cache[cache_key]
        
        apps_dir = PathUtils.get_apps_directory(bench_path)
        if not apps_dir:
            return []
        
        apps = []
        try:
            # Scan apps directory for valid Frappe apps
            for item in apps_dir.iterdir():
                if item.is_dir() and PathUtils.is_frappe_app(item):
                    apps.append(item)
        except (OSError, PermissionError):
            # Handle permission errors gracefully
            pass
        
        # Cache result for performance
        PathUtils._path_cache[cache_key] = apps
        return apps
    
    @staticmethod
    def discover_sites_in_bench(bench_path: Union[str, Path]) -> List[Path]:
        """Discover all Frappe sites in a bench directory."""
        cache_key = f"sites_in_bench:{bench_path}"
        if cache_key in PathUtils._path_cache:
            return PathUtils._path_cache[cache_key]
        
        sites_dir = PathUtils.get_sites_directory(bench_path)
        if not sites_dir:
            return []
        
        sites = []
        try:
            # Scan sites directory for valid Frappe sites
            for item in sites_dir.iterdir():
                if item.is_dir() and PathUtils.is_frappe_site(item):
                    sites.append(item)
        except (OSError, PermissionError):
            # Handle permission errors gracefully
            pass
        
        # Cache result for performance
        PathUtils._path_cache[cache_key] = sites
        return sites
    
    @staticmethod
    def get_hooks_file_path(app_path: Union[str, Path]) -> Optional[Path]:
        """Get hooks.py file path for an app."""
        app_path = PathUtils.normalize_path(app_path)
        
        # Try nested structure first (app_name/app_name/hooks.py)
        nested_hooks = app_path / app_path.name / "hooks.py"
        if nested_hooks.exists():
            return nested_hooks
        
        # Fallback to root structure (app_name/hooks.py)
        root_hooks = app_path / "hooks.py"
        if root_hooks.exists():
            return root_hooks
        
        return None
    
    @staticmethod
    def get_app_info_from_path(app_path: Union[str, Path], priority: int = 0) -> Optional[AppInfo]:
        """Create AppInfo object from app path with validation."""
        app_path = PathUtils.normalize_path(app_path)
        
        if not PathUtils.is_frappe_app(app_path):
            return None
        
        # Get app name from directory name
        app_name = app_path.name
        
        # Find hooks.py file
        hooks_file = PathUtils.get_hooks_file_path(app_path)
        
        # Try to get version from __init__.py
        version = PathUtils._get_app_version(app_path)
        
        return AppInfo(
            name=app_name,
            path=app_path,
            hooks_file=hooks_file,
            priority=priority,
            version=version,
            installed=True,
        )
    
    @staticmethod
    @lru_cache(maxsize=64)
    def _get_app_version(app_path: Path) -> Optional[str]:
        """Extract version from app's __init__.py file."""
        init_file = app_path / "__init__.py"
        if not init_file.exists():
            return None
        
        try:
            with open(init_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Look for __version__ = "x.y.z" pattern
            import re
            version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
            if version_match:
                return version_match.group(1)
                
        except (OSError, UnicodeDecodeError):
            pass
        
        return None
    
    @staticmethod
    def clear_cache():
        """Clear internal path caches for memory management."""
        PathUtils._path_cache.clear()
        PathUtils._app_cache.clear()
        
        # Clear LRU caches
        PathUtils.normalize_path.cache_clear()
        PathUtils.is_frappe_bench.cache_clear()
        PathUtils.is_frappe_site.cache_clear()
        PathUtils.is_frappe_app.cache_clear()
        PathUtils._get_app_version.cache_clear()
    
    @staticmethod
    def get_relative_path(path: Union[str, Path], base: Union[str, Path]) -> Path:
        """Get relative path from base directory."""
        path = PathUtils.normalize_path(path)
        base = PathUtils.normalize_path(base)
        
        try:
            return path.relative_to(base)
        except ValueError:
            # Paths are not relative, return absolute path
            return path