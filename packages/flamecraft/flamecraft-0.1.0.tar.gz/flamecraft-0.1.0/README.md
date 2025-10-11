# Flamecraft

[![PyPI version](https://badge.fury.io/py/flamecraft.svg)](https://badge.fury.io/py/flamecraft)
[![Python Version](https://img.shields.io/pypi/pyversions/flamecraft)](https://pypi.org/project/flamecraft/)
[![License](https://img.shields.io/pypi/l/flamecraft)](https://github.com/flamecraft/flamecraft/blob/main/LICENSE)

**Flamecraft** is a powerful agentic AI testing package with advanced pretty print features designed for modern software development workflows. It provides intuitive tools for running, analyzing, and reporting AI-driven test suites with beautiful, human-readable output.

## Features

- 🤖 **Agentic AI Testing**: Run intelligent test suites that adapt to your application
- 🎨 **Pretty Print Results**: Beautifully formatted test output for easy analysis
- 📊 **Comprehensive Reporting**: Generate detailed reports in multiple formats
- ⚡ **High Performance**: Optimized for speed and efficiency
- 🛠️ **Easy Integration**: Simple API that integrates seamlessly with existing workflows
- 📦 **Lightweight**: Minimal dependencies with maximum functionality

## Installation

```bash
pip install flamecraft
```

## Quick Start

### Basic Usage

```python
from flamecraft import greet

# Simple greeting
print(greet("Developer"))
# Output: Hello, Developer! Welcome to Flamecraft.
```

### Running AI Test Suites

```python
from flamecraft import run_test_suite, pretty_print_results

# Define your test cases
test_cases = [
    {
        "name": "User Authentication Test",
        "input": {"username": "testuser", "password": "password123"},
        "expected": {"status": "authenticated"}
    },
    {
        "name": "Data Validation Test",
        "input": {"data": {"email": "test@example.com"}},
        "expected": {"valid": True}
    }
]

# Run the test suite
results = run_test_suite(test_cases)

# Pretty print the results
pretty_print_results(results)
```

### Generating Reports

```python
from flamecraft import generate_test_report

# Generate a JSON report
json_report = generate_test_report(results, format="json")
print(json_report)

# Generate a text report
text_report = generate_test_report(results, format="text")
print(text_report)
```

## API Reference

### Core Functions

#### `greet(name: str) -> str`
Returns a friendly greeting message.

#### `run_test_suite(test_cases: List[Dict[str, Any]]) -> Dict[str, Any]`
Executes a suite of agentic AI tests and returns detailed results.

#### `pretty_print_results(results: Dict[str, Any]) -> None`
Displays test results in a beautifully formatted way.

#### `generate_test_report(results: Dict[str, Any], format: str = "json") -> str`
Generates a test report in the specified format (JSON or text).

### Project Information

#### `get_project_name() -> str`
Returns the project name.

#### `get_version() -> str`
Returns the current version.

#### `get_author() -> str`
Returns the author name.

#### `get_description() -> str`
Returns the project description.

#### `get_license() -> str`
Returns the project license.

#### `get_python_version() -> str`
Returns the minimum required Python version.

#### `get_project_url() -> str`
Returns the project homepage URL.

## Requirements

- Python >= 3.9
- No external dependencies

## Contributing

We welcome contributions to Flamecraft! Please see our [Contributing Guide](CONTRIBUTING.md) for more details.

1. Fork the repository
2. Create a new branch for your feature
3. Add your feature or improvement
4. Write tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions, please [file an issue](https://github.com/flamecraft/flamecraft/issues) on our GitHub repository.