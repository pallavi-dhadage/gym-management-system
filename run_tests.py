#!/usr/bin/env python
"""
Test runner script for SetFit Gym Management System
Runs all tests and generates coverage report
"""
import sys
import pytest


def run_tests():
    """Run all tests with coverage"""
    args = [
        'tests/',
        '-v',  # Verbose output
        '--cov=app',  # Coverage for app directory
        '--cov-report=html',  # Generate HTML report
        '--cov-report=term-missing',  # Show missing lines in terminal
        '--tb=short',  # Shorter traceback format
        '-ra',  # Show summary of all test results
    ]
    
    # Add any command line args
    args.extend(sys.argv[1:])
    
    print("=" * 70)
    print("SetFit Gym - Test Suite")
    print("=" * 70)
    print()
    
    # Run tests
    result = pytest.main(args)
    
    print()
    print("=" * 70)
    if result == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed. Review the output above.")
    print("=" * 70)
    print()
    print("📊 Coverage report generated at: htmlcov/index.html")
    print()
    
    return result


if __name__ == '__main__':
    sys.exit(run_tests())
