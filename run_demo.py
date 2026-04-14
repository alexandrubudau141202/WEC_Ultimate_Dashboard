"""
WEC Telemetry Dashboard - Demo Runner
=====================================

Runs all three optimization modules and generates visualizations.

Author: Alexandru
Version: 1.0
"""

import subprocess
import sys


def run_module(module_name: str, description: str):
    """Run a Python module and display output"""
    print("\n" + "=" * 80)
    print(f"RUNNING: {description}")
    print("=" * 80 + "\n")
    
    try:
        result = subprocess.run(
            [sys.executable, module_name],
            capture_output=False,
            text=True,
            check=True
        )
        print(f"\n✓ {module_name} completed successfully")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ {module_name} failed with error code {e.returncode}")
        return False
    
    return True


def main():
    """Run all demo modules"""
    print("=" * 80)
    print("WEC TELEMETRY STRATEGY DASHBOARD - FULL DEMO")
    print("=" * 80)
    print("\nThis will run all three optimization modules:")
    print("  1. Hybrid Deployment Optimizer")
    print("  2. Tire Strategy Optimizer")
    print("  3. Fuel Strategy Optimizer")
    print("\nEach will generate visualizations and analysis.")
    print("=" * 80)
    
    input("\nPress Enter to continue...")
    
    modules = [
        ("hybrid_optimizer.py", "Hybrid Energy Deployment Analysis"),
        ("tire_strategy.py", "Tire Degradation and Stint Strategy"),
        ("fuel_optimizer.py", "Fuel Strategy and Pit Windows"),
    ]
    
    results = []
    for module, description in modules:
        success = run_module(module, description)
        results.append((module, success))
        if success:
            input(f"\nPress Enter to continue to next module...")
    
    # Summary
    print("\n" + "=" * 80)
    print("DEMO COMPLETE - RESULTS SUMMARY")
    print("=" * 80 + "\n")
    
    for module, success in results:
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"  {status}: {module}")
    
    print("\n" + "=" * 80)
    print("Generated visualizations:")
    print("  - hybrid_deployment_le_mans.png")
    print("  - tire_strategy_comparison.png")
    print("  - fuel_strategy_24h.png")
    print("=" * 80)

if __name__ == "__main__":
    main()
