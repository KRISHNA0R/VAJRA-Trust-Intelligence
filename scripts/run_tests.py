#!/usr/bin/env python3
"""
Test runner script for deepfake-detector

Usage:
    python scripts/run_tests.py              # Run all tests
    python scripts/run_tests.py --unit       # Run only unit tests
    python scripts/run_tests.py --integration # Run only integration tests
    python scripts/run_tests.py --coverage   # Run with coverage report
"""
import subprocess
import sys
import argparse
from pathlib import Path


def run_command(cmd, description):
    """Run a command and print status"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print(f"\n✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} - FAILED (exit code: {e.returncode})")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run tests for deepfake-detector")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--markers", action="store_true", help="Show available test markers")
    
    args = parser.parse_args()
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    
    # Show markers if requested
    if args.markers:
        run_command(
            ["pytest", "--markers"],
            "Showing available test markers"
        )
        return 0
    
    # Build pytest command
    pytest_cmd = ["pytest", "tests/"]
    
    # Add verbosity
    if args.verbose:
        pytest_cmd.append("-vv")
    else:
        pytest_cmd.append("-v")
    
    # Add markers
    if args.unit:
        pytest_cmd.extend(["-m", "unit"])
    elif args.integration:
        pytest_cmd.extend(["-m", "integration"])
    
    # Add coverage
    if args.coverage:
        pytest_cmd.extend([
            "--cov=app",
            "--cov-report=html",
            "--cov-report=term",
            "--cov-report=xml"
        ])
    
    # Add other options
    pytest_cmd.extend([
        "--tb=short",  # Shorter traceback format
        "-ra",         # Show extra test summary info
    ])
    
    # Run tests
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "RUNNING TESTS" + " "*30 + "║")
    print("╚" + "="*58 + "╝")
    
    if args.unit:
        print("📋 Test Scope: Unit tests only")
    elif args.integration:
        print("📋 Test Scope: Integration tests only")
    else:
        print("📋 Test Scope: All tests")
    
    success = run_command(pytest_cmd, "Running pytest")
    
    # Show coverage report location if generated
    if args.coverage and success:
        coverage_html = project_root / "htmlcov" / "index.html"
        print(f"\n📊 Coverage report generated:")
        print(f"   HTML: {coverage_html}")
        print(f"   XML:  {project_root / 'coverage.xml'}")
    
    # Summary
    print(f"\n{'='*60}")
    if success:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check the output above.")
    print(f"{'='*60}\n")
    
    return 0 if success else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(130)

