#!/usr/bin/env python3
"""
Comprehensive usage examples for HookX library.

Demonstrates preset functions for complete hook analysis,
quick scans, and report saving/loading capabilities.
"""

from pathlib import Path
from hookx import HookX

def full_scan_example():
    """Complete comprehensive scan example with all details."""
    print("🔍 Full Comprehensive Scan Example")
    print("=" * 50)
    
    # Initialize HookX
    scanner = HookX()
    
    # Scan a Frappe bench (replace with your path)
    bench_path = "/path/to/frappe-bench"
    
    try:
        report = scanner.full_scan_report(bench_path, save_to="full_scan_report.json")
        
        print(f"✅ Full scan completed!")
        print(f"📊 Complete Summary:")
        print(f"  - Scan ID: {report['scan_info']['scan_id']}")
        print(f"  - Scan Type: {report['scan_info']['scan_type']}")
        print(f"  - Apps scanned: {report['summary']['total_apps']}")
        print(f"  - Hooks found: {report['summary']['total_hooks']}")
        print(f"  - Conflicts detected: {report['summary']['total_conflicts']}")
        print(f"  - Duration: {report['scan_info']['duration']:.3f}s")
        
        print(f"\n📱 Apps Details:")
        for app in report['apps']:
            print(f"  - {app['name']} (v{app['version'] or 'unknown'}) - Priority: {app['priority']}")
        
        print(f"\n🔗 Hooks by App:")
        for app_name, count in report.get('hooks_by_app', {}).items():
            print(f"  - {app_name}: {count} hooks")
        
        if report['conflicts']:
            print(f"\n⚠️  Conflicts by Severity:")
            for severity, count in report['conflicts_by_severity'].items():
                print(f"  - {severity.upper()}: {count}")
            
            print(f"\n🔍 Detailed Conflicts:")
            for conflict in report['conflicts'][:5]:
                print(f"  - [{conflict['severity'].upper()}] {conflict['description']}")
                if conflict['resolution_hint']:
                    print(f"    💡 {conflict['resolution_hint']}")
        
        print(f"\n💾 Full report saved to: full_scan_report.json")
        
        return report
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def quick_scan_example():
    """Quick scan example for fast checks."""
    print("\n⚡ Quick Scan Example")
    print("=" * 50)
    
    scanner = HookX()
    bench_path = "/path/to/frappe-bench"
    
    try:
        quick_result = scanner.quick_scan(bench_path)
        
        print(f"✅ Quick scan completed!")
        print(f"📊 Quick Summary:")
        print(f"  - Status: {quick_result['status'].upper()}")
        print(f"  - Apps: {quick_result['apps_scanned']}")
        print(f"  - Hooks: {quick_result['total_hooks']}")
        print(f"  - Conflicts: {quick_result['total_conflicts']}")
        print(f"  - Critical: {quick_result['critical_conflicts']}")
        print(f"  - Duration: {quick_result['scan_duration']:.3f}s")
        
        return quick_result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def save_and_load_example():
    """Example of saving and loading scan reports."""
    print("\n💾 Save & Load Report Example")
    print("=" * 50)
    
    scanner = HookX()
    bench_path = "/path/to/frappe-bench"
    
    try:
        report = scanner.full_scan_report(bench_path, save_to="my_scan_report.json")
        print(f"✅ Report saved to: my_scan_report.json")
        
        import json
        with open("my_scan_report.json", 'r') as f:
            loaded_report = json.load(f)
        
        print(f"📂 Loaded report:")
        print(f"  - Scan ID: {loaded_report['scan_info']['scan_id']}")
        print(f"  - Total conflicts: {loaded_report['summary']['total_conflicts']}")
        
        return loaded_report
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


if __name__ == "__main__":
    full_scan_example()
    quick_scan_example()
    save_and_load_example()
    
    print("\n🎉 All examples completed!")
    print("Check the generated JSON files for detailed reports.")