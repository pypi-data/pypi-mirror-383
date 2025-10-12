"""
Frappe-specific utilities for understanding app structure and configuration.

Provides deep integration with Frappe framework conventions, app loading
order, site configuration, and hook parsing with optimized performance.
"""

import ast
import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from .performance import cached_property, memoize, timer
from ..core.models import AppInfo, HookType


class FrappeUtils:
    """Utilities for Frappe framework integration and app analysis."""
    
    # Common Frappe hook patterns for fast recognition
    HOOK_PATTERNS = {
        HookType.DOC_EVENTS: [
            'before_insert', 'after_insert', 'before_save', 'after_save',
            'before_submit', 'after_submit', 'before_cancel', 'after_cancel',
            'before_delete', 'after_delete', 'before_update_after_submit',
            'after_update_after_submit', 'on_update', 'on_change', 'validate',
            'on_trash', 'after_rename', 'before_rename', 'before_print',
        ],
        HookType.SCHEDULER_EVENTS: [
            'all', 'hourly', 'daily', 'weekly', 'monthly', 'cron',
        ],
        HookType.BOOT_SESSION: ['boot_session'],
        HookType.WEBSITE_ROUTE_RULES: ['website_route_rules'],
        HookType.WEBSITE_REDIRECTS: ['website_redirects'],
        HookType.JINJA: ['jinja'],
        HookType.FIXTURES: ['fixtures'],
    }
    
    @staticmethod
    @lru_cache(maxsize=64)
    def get_site_config(site_path: Union[str, Path]) -> Dict[str, Any]:
        """Load and parse site configuration with caching."""
        site_path = Path(site_path)
        config_file = site_path / "site_config.json"
        
        if not config_file.exists():
            return {}
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    
    @staticmethod
    @lru_cache(maxsize=32)
    def get_installed_apps(site_path: Union[str, Path]) -> List[str]:
        """Get list of installed apps for a site with proper ordering."""
        config = FrappeUtils.get_site_config(site_path)
        
        # Get installed apps from site config
        installed_apps = config.get('installed_apps', [])
        
        # Ensure frappe is first if not present
        if 'frappe' not in installed_apps:
            installed_apps.insert(0, 'frappe')
        elif installed_apps[0] != 'frappe':
            installed_apps.remove('frappe')
            installed_apps.insert(0, 'frappe')
        
        return installed_apps
    
    @staticmethod
    def get_app_load_order(site_path: Union[str, Path], bench_path: Union[str, Path]) -> List[AppInfo]:
        """Get apps in their load order with priority assignment."""
        from .paths import PathUtils
        
        site_path = Path(site_path)
        bench_path = Path(bench_path)
        
        # Get installed apps in order
        installed_apps = FrappeUtils.get_installed_apps(site_path)
        
        # Get apps directory
        apps_dir = PathUtils.get_apps_directory(bench_path)
        if not apps_dir:
            return []
        
        app_infos = []
        for priority, app_name in enumerate(installed_apps):
            app_path = apps_dir / app_name
            
            if PathUtils.is_frappe_app(app_path):
                app_info = PathUtils.get_app_info_from_path(app_path, priority)
                if app_info:
                    app_infos.append(app_info)
        
        return app_infos
    
    @staticmethod
    @memoize(maxsize=128)
    def parse_hooks_file(hooks_file_path: Union[str, Path]) -> Dict[str, Any]:
        """Parse hooks.py file and extract all hook definitions."""
        hooks_file_path = Path(hooks_file_path)
        
        if not hooks_file_path.exists():
            return {}
        
        try:
            with timer(f"parse_hooks:{hooks_file_path.name}"):
                with open(hooks_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                hooks = {}
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                hook_name = target.id
                                hook_value = FrappeUtils._extract_ast_value(node.value)
                                if hook_value is not None:
                                    hooks[hook_name] = hook_value
                
                return hooks
                
        except (OSError, SyntaxError, UnicodeDecodeError):
            return FrappeUtils._parse_hooks_regex(hooks_file_path)
    
    @staticmethod
    def _extract_ast_value(node: ast.AST) -> Any:
        """Extract value from AST node safely."""
        try:
            if isinstance(node, (ast.Str, ast.Constant)):
                return node.s if hasattr(node, 's') else node.value
            elif isinstance(node, ast.List):
                return [FrappeUtils._extract_ast_value(item) for item in node.elts]
            elif isinstance(node, ast.Dict):
                result = {}
                for key, value in zip(node.keys, node.values):
                    key_val = FrappeUtils._extract_ast_value(key)
                    val_val = FrappeUtils._extract_ast_value(value)
                    if key_val is not None:
                        result[key_val] = val_val
                return result
            elif isinstance(node, ast.Name):
                return node.id
            else:
                # For complex expressions, return string representation
                return ast.unparse(node) if hasattr(ast, 'unparse') else str(node)
        except:
            return None
    
    @staticmethod
    def _parse_hooks_regex(hooks_file_path: Path) -> Dict[str, Any]:
        """Fallback regex-based hooks parsing for malformed files."""
        try:
            with open(hooks_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            hooks = {}
            
            patterns = [
                r'^(\w+)\s*=\s*"([^"]+)"',
                r'^(\w+)\s*=\s*\[([^\]]+)\]',
                r'^(\w+)\s*=\s*{([^}]+)}',
            ]
            
            for line in content.split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                for pattern in patterns:
                    match = re.match(pattern, line)
                    if match:
                        hook_name = match.group(1)
                        hook_value = match.group(2)
                        
                        try:
                            hooks[hook_name] = eval(f"[{hook_value}]" if '[' not in hook_value else hook_value)
                        except:
                            hooks[hook_name] = hook_value
                        break
            
            return hooks
            
        except (OSError, UnicodeDecodeError):
            return {}
    
    @staticmethod
    def classify_hook_type(hook_name: str, hook_value: Any) -> HookType:
        """Classify hook type based on name and value patterns."""
        hook_name_lower = hook_name.lower()
        
        for hook_type, patterns in FrappeUtils.HOOK_PATTERNS.items():
            if any(pattern in hook_name_lower for pattern in patterns):
                return hook_type
        
        if 'override' in hook_name_lower:
            if 'method' in hook_name_lower:
                return HookType.OVERRIDE_WHITELISTED_METHODS
            elif 'doctype' in hook_name_lower or 'class' in hook_name_lower:
                return HookType.OVERRIDE_DOCTYPE_CLASS
        
        if isinstance(hook_value, dict):
            for key in hook_value.keys():
                if isinstance(key, str) and key.replace('_', ' ').title() == key.replace('_', ' ').title():
                    return HookType.DOC_EVENTS
        
        return HookType.CUSTOM
    
    @staticmethod
    def extract_hook_handlers(hook_name: str, hook_value: Any) -> List[Tuple[str, str]]:
        """Extract handler functions from hook value."""
        handlers = []
        
        if isinstance(hook_value, str):
            handlers.append(("", hook_value))
        elif isinstance(hook_value, list):
            for item in hook_value:
                if isinstance(item, str):
                    handlers.append(("", item))
                elif isinstance(item, dict):
                    for target, handler in item.items():
                        if isinstance(handler, str):
                            handlers.append((target, handler))
                        elif isinstance(handler, list):
                            for h in handler:
                                if isinstance(h, str):
                                    handlers.append((target, h))
        elif isinstance(hook_value, dict):
            for target, handler in hook_value.items():
                if isinstance(handler, str):
                    handlers.append((target, handler))
                elif isinstance(handler, list):
                    for h in handler:
                        if isinstance(h, str):
                            handlers.append((target, h))
                elif isinstance(handler, dict):
                    for event, event_handlers in handler.items():
                        if isinstance(event_handlers, str):
                            handlers.append((f"{target}.{event}", event_handlers))
                        elif isinstance(event_handlers, list):
                            for eh in event_handlers:
                                if isinstance(eh, str):
                                    handlers.append((f"{target}.{event}", eh))
        
        return handlers
    
    @staticmethod
    def validate_handler_path(handler: str) -> bool:
        """Validate if handler path is in correct format."""
        if not handler or not isinstance(handler, str):
            return False
        
        parts = handler.split('.')
        if len(parts) < 2:
            return False
        
        return all(part.isidentifier() for part in parts)
    
    @staticmethod
    def get_hook_execution_order(hooks: List[Any], app_priorities: Dict[str, int]) -> List[Any]:
        """Sort hooks by app priority for execution order."""
        return sorted(hooks, key=lambda h: app_priorities.get(h.app_name, 999))
    
    @staticmethod
    @lru_cache(maxsize=32)
    def get_frappe_version(bench_path: Union[str, Path]) -> Optional[str]:
        """Get Frappe framework version from bench."""
        bench_path = Path(bench_path)
        
        # Try to get version from frappe app
        frappe_app = bench_path / "apps" / "frappe"
        if frappe_app.exists():
            init_file = frappe_app / "__init__.py"
            if init_file.exists():
                try:
                    with open(init_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Look for __version__
                    version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
                    if version_match:
                        return version_match.group(1)
                except (OSError, UnicodeDecodeError):
                    pass
        
        return None
    
    @staticmethod
    def clear_cache():
        """Clear all cached data for memory management."""
        FrappeUtils.get_site_config.cache_clear()
        FrappeUtils.get_installed_apps.cache_clear()
        FrappeUtils.parse_hooks_file.cache_clear()
        FrappeUtils.get_frappe_version.cache_clear()