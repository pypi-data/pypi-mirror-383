from . import (
    greet, 
    get_author, 
    get_project_name, 
    get_version,
    get_description,
    run_test_suite,
    pretty_print_results
)

def main():
    print("=== Project Info ===")
    print(f"Project Name: {get_project_name()}")
    print(f"Version: {get_version()}")
    print(f"Author: {get_author()}")
    print(f"Description: {get_description()}")
    
    print("\n=== Greet Example ===")
    print(greet("Victor"))
    
    print("\n=== Agentic AI Test Demo ===")
    # Sample test cases to demonstrate the new functionality
    test_cases = [
        {
            "name": "Basic Functionality Test",
            "input": {"action": "greet", "name": "TestUser"},
            "expected": {"message": "Hello, TestUser! Welcome to Flamecraft."}
        },
        {
            "name": "Project Info Validation",
            "input": {"info_type": "name"},
            "expected": {"value": "Flamecraft"}
        }
    ]
    
    results = run_test_suite(test_cases)
    pretty_print_results(results)

if __name__ == "__main__":
    main()