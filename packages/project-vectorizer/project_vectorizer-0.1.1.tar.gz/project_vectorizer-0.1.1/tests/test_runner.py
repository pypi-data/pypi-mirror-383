"""Test runner script for project vectorizer tests."""

import sys
import asyncio
import pytest
from pathlib import Path

# Add the project to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_all_tests():
    """Run all test suites with appropriate configuration."""
    
    # Configure pytest arguments
    pytest_args = [
        str(Path(__file__).parent),  # Test directory
        "-v",  # Verbose output
        "-s",  # Don't capture output
        "--tb=short",  # Short traceback format
        "--strict-markers",  # Strict marker enforcement
        "-p", "no:warnings",  # Disable warnings plugin for cleaner output
        "--asyncio-mode=auto",  # Auto async mode
        "--maxfail=5",  # Stop after 5 failures
    ]
    
    # Run the tests
    exit_code = pytest.main(pytest_args)
    return exit_code

def run_specific_test_suite(suite_name: str):
    """Run a specific test suite."""
    
    test_files = {
        "env": "test_environment_variables.py",
        "search": "test_single_word_search.py", 
        "chunking": "test_multi_level_chunking.py",
        "workflow": "test_complete_workflow.py",
        "errors": "test_error_handling.py",
    }
    
    if suite_name not in test_files:
        print(f"Unknown test suite: {suite_name}")
        print(f"Available suites: {', '.join(test_files.keys())}")
        return 1
    
    test_file = Path(__file__).parent / test_files[suite_name]
    
    pytest_args = [
        str(test_file),
        "-v",
        "-s", 
        "--tb=short",
        "--asyncio-mode=auto",
    ]
    
    exit_code = pytest.main(pytest_args)
    return exit_code

def run_quick_tests():
    """Run a quick subset of tests for fast feedback."""
    
    # Run only the most important tests quickly
    pytest_args = [
        str(Path(__file__).parent),
        "-v",
        "-k", "test_single_word_exact_match or test_environment_variable_override or test_function_and_class_chunking",
        "--tb=short",
        "--asyncio-mode=auto",
        "--maxfail=3",
    ]
    
    exit_code = pytest.main(pytest_args)
    return exit_code

def run_performance_tests():
    """Run performance-focused tests."""
    
    pytest_args = [
        str(Path(__file__).parent),
        "-v",
        "-k", "performance or large_project or memory_pressure",
        "--tb=short", 
        "--asyncio-mode=auto",
    ]
    
    exit_code = pytest.main(pytest_args)
    return exit_code

def main():
    """Main entry point for test runner."""
    
    if len(sys.argv) == 1:
        print("Running all tests...")
        return run_all_tests()
    
    command = sys.argv[1].lower()
    
    if command == "all":
        print("Running all tests...")
        return run_all_tests()
    
    elif command == "quick":
        print("Running quick tests...")
        return run_quick_tests()
        
    elif command == "perf" or command == "performance":
        print("Running performance tests...")
        return run_performance_tests()
        
    elif command in ["env", "search", "chunking", "workflow", "errors"]:
        print(f"Running {command} test suite...")
        return run_specific_test_suite(command)
        
    else:
        print(f"Unknown command: {command}")
        print("Available commands:")
        print("  all        - Run all tests")
        print("  quick      - Run quick subset of tests")
        print("  perf       - Run performance tests")
        print("  env        - Run environment variable tests")
        print("  search     - Run single-word search tests")
        print("  chunking   - Run multi-level chunking tests") 
        print("  workflow   - Run complete workflow tests")
        print("  errors     - Run error handling tests")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)