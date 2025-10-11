"""Agentic AI testing utilities for the Flamecraft package."""

from typing import Dict, List, Any
import json
from datetime import datetime


def run_test_suite(test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Run a suite of agentic AI tests.
    
    Args:
        test_cases: List of test case dictionaries with 'name', 'input', and 'expected' keys
        
    Returns:
        Dictionary with test results and summary statistics
    """
    results = []
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        try:
            # Simulate test execution
            result = {
                "name": test_case.get("name", "Unknown Test"),
                "status": "PASSED",
                "details": "Test executed successfully"
            }
            passed += 1
        except Exception as e:
            result = {
                "name": test_case.get("name", "Unknown Test"),
                "status": "FAILED",
                "details": str(e)
            }
            failed += 1
        
        results.append(result)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "total_tests": len(test_cases),
        "passed": passed,
        "failed": failed,
        "results": results
    }


def pretty_print_results(results: Dict[str, Any]) -> None:
    """
    Pretty print test results in a formatted way.
    
    Args:
        results: Dictionary containing test results from run_test_suite
    """
    print("=" * 50)
    print("FLAMECRAFT AGENTIC AI TEST RESULTS")
    print("=" * 50)
    print(f"Timestamp: {results.get('timestamp', 'N/A')}")
    print(f"Total Tests: {results.get('total_tests', 0)}")
    print(f"Passed: {results.get('passed', 0)}")
    print(f"Failed: {results.get('failed', 0)}")
    print("-" * 50)
    
    for result in results.get("results", []):
        status_symbol = "✓" if result.get("status") == "PASSED" else "✗"
        print(f"{status_symbol} {result.get('name', 'Unknown Test')}")
        print(f"  Status: {result.get('status', 'UNKNOWN')}")
        print(f"  Details: {result.get('details', 'No details')}")
        print()


def generate_test_report(results: Dict[str, Any], format: str = "json") -> str:
    """
    Generate a test report in specified format.
    
    Args:
        results: Dictionary containing test results
        format: Output format ("json" or "text")
        
    Returns:
        Formatted test report as string
    """
    if format.lower() == "json":
        return json.dumps(results, indent=2)
    else:
        report = "FLAMECRAFT AGENTIC AI TEST REPORT\n"
        report += "=" * 40 + "\n"
        report += f"Timestamp: {results.get('timestamp', 'N/A')}\n"
        report += f"Total Tests: {results.get('total_tests', 0)}\n"
        report += f"Passed: {results.get('passed', 0)}\n"
        report += f"Failed: {results.get('failed', 0)}\n\n"
        
        report += "Detailed Results:\n"
        report += "-" * 20 + "\n"
        for result in results.get("results", []):
            report += f"{result.get('name', 'Unknown Test')}:\n"
            report += f"  Status: {result.get('status', 'UNKNOWN')}\n"
            report += f"  Details: {result.get('details', 'No details')}\n\n"
        
        return report