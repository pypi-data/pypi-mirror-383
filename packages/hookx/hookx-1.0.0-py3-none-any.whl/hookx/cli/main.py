"""
Main CLI entry point for HookX with comprehensive command structure.

Provides a rich command-line interface with multiple subcommands,
intelligent defaults, and excellent user experience.
"""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from .. import __version__
from ..core.api import HookX
from .commands import check_command, export_command, scan_command, validate_command

# Global console for rich output
console = Console()


@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version and exit')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, version, verbose):
    """
    🔍 HookX - Advanced Frappe hooks analyzer and conflict detector.
    
    Analyze, inspect, and report on hooks in Frappe applications with
    comprehensive conflict detection and rich reporting capabilities.
    
    Examples:
        hookx scan /path/to/bench
        hookx scan /path/to/site --format json
        hookx check /path/to/bench --strict
        hookx validate /path/to/app
    """
    if version:
        console.print(f"HookX version {__version__}", style="bold green")
        sys.exit(0)
    
    # Set up context
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    
    # If no command specified, show help
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


@cli.command()
@click.argument('path', type=click.Path(exists=True, path_type=Path))
@click.option('--site', '-s', help='Site name for app load order (when scanning bench)')
@click.option('--format', '-f', 'output_format', 
              type=click.Choice(['table', 'json', 'csv', 'html', 'markdown']),
              default='table', help='Output format')
@click.option('--output', '-o', type=click.Path(path_type=Path), 
              help='Output file path')
@click.option('--min-severity', type=click.Choice(['critical', 'high', 'medium', 'low', 'info']),
              help='Minimum severity level to report')
@click.option('--strict', is_flag=True, help='Strict mode - treat all conflicts as high severity')
@click.option('--no-cache', is_flag=True, help='Disable caching for fresh results')
@click.option('--max-workers', type=int, help='Maximum worker threads for parallel processing')
@click.pass_context
def scan(ctx, path, site, output_format, output, min_severity, strict, no_cache, max_workers):
    """
    🔍 Scan Frappe bench, site, or app for hook definitions and conflicts.
    
    Performs comprehensive analysis of hooks across apps, detects conflicts,
    and generates detailed reports in multiple formats.
    
    PATH can be:
    - Frappe bench directory (scans all apps)
    - Frappe site directory (scans installed apps in load order)  
    - Frappe app directory (scans single app)
    
    Examples:
        hookx scan /home/frappe/frappe-bench
        hookx scan /home/frappe/frappe-bench/sites/mysite
        hookx scan /home/frappe/frappe-bench/apps/erpnext --format json
    """
    return scan_command(ctx, path, site, output_format, output, min_severity, strict, no_cache, max_workers)


@cli.command()
@click.argument('path', type=click.Path(exists=True, path_type=Path))
@click.option('--exit-code', is_flag=True, help='Exit with non-zero code if conflicts found')
@click.option('--critical-only', is_flag=True, help='Only check for critical conflicts')
@click.option('--strict', is_flag=True, help='Strict mode - treat all conflicts as critical')
@click.option('--quiet', '-q', is_flag=True, help='Suppress output, only return exit code')
@click.pass_context
def check(ctx, path, exit_code, critical_only, strict, quiet):
    """
    ✅ Quick check for hook conflicts without detailed reporting.
    
    Performs fast conflict detection and returns appropriate exit codes
    for CI/CD integration and automated checks.
    
    Exit codes:
        0 - No conflicts found
        1 - Conflicts found (or critical conflicts if --critical-only)
        2 - Error during scanning
    
    Examples:
        hookx check /path/to/bench --exit-code
        hookx check /path/to/site --critical-only --quiet
    """
    return check_command(ctx, path, exit_code, critical_only, strict, quiet)


@cli.command()
@click.argument('path', type=click.Path(exists=True, path_type=Path))
@click.option('--fix', is_flag=True, help='Attempt to fix common syntax issues')
@click.pass_context
def validate(ctx, path, fix):
    """
    🔧 Validate hooks.py syntax and structure.
    
    Checks hooks.py files for syntax errors, invalid handler paths,
    and common configuration issues without full conflict analysis.
    
    PATH can be:
    - hooks.py file
    - App directory (validates hooks.py in the app)
    - Bench directory (validates all app hooks.py files)
    
    Examples:
        hookx validate /path/to/app/hooks.py
        hookx validate /path/to/app
        hookx validate /path/to/bench --fix
    """
    return validate_command(ctx, path, fix)


@cli.command()
@click.argument('path', type=click.Path(exists=True, path_type=Path))
@click.argument('output_file', type=click.Path(path_type=Path))
@click.option('--format', '-f', 'export_format',
              type=click.Choice(['json', 'csv']),
              default='json', help='Export format')
@click.option('--site', '-s', help='Site name for app load order')
@click.option('--fail-on-conflicts', is_flag=True, 
              help='Exit with code 1 if any conflicts found')
@click.option('--fail-on-critical', is_flag=True,
              help='Exit with code 1 only if critical conflicts found')
@click.pass_context
def export(ctx, path, output_file, export_format, site, fail_on_conflicts, fail_on_critical):
    """
    📤 Export scan results for CI/CD integration and external tools.
    
    Generates machine-readable reports suitable for automated processing,
    dashboard integration, and continuous integration pipelines.
    
    Examples:
        hookx export /path/to/bench results.json
        hookx export /path/to/site report.csv --format csv
        hookx export /path/to/bench ci-report.json --fail-on-critical
    """
    return export_command(ctx, path, output_file, export_format, site, fail_on_conflicts, fail_on_critical)


@cli.command()
@click.option('--clear-cache', is_flag=True, help='Clear all caches')
@click.option('--show-stats', is_flag=True, help='Show performance statistics')
def info(clear_cache, show_stats):
    """
    ℹ️  Show HookX information and manage caches.
    
    Display version information, performance statistics,
    and manage internal caches for optimal performance.
    """
    console.print(f"🔍 HookX v{__version__}", style="bold blue")
    console.print("Advanced Frappe hooks analyzer and conflict detector\n")
    
    if clear_cache:
        # Clear caches
        from ..utils.paths import PathUtils
        from ..utils.frappe_utils import FrappeUtils
        from ..utils.performance import performance_monitor
        
        PathUtils.clear_cache()
        FrappeUtils.clear_cache()
        performance_monitor.clear()
        
        console.print("✅ All caches cleared", style="green")
    
    if show_stats:
        from ..utils.performance import performance_monitor
        stats = performance_monitor.get_all_stats()
        
        if stats:
            console.print("\n📊 Performance Statistics:", style="bold")
            for name, stat_data in stats.items():
                console.print(f"  {name}: {stat_data}")
        else:
            console.print("\n📊 No performance statistics available", style="dim")


def main():
    """Main entry point for the CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n❌ Operation cancelled by user", style="red")
        sys.exit(130)
    except Exception as e:
        console.print(f"\n❌ Error: {e}", style="red bold")
        sys.exit(2)


if __name__ == '__main__':
    main()