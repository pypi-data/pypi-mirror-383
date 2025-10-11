from .core.greet import greet
from .core.agent_test import run_test_suite, pretty_print_results, generate_test_report
from .info.project_info import (
    get_project_name, 
    get_version, 
    get_author,
    get_description,
    get_license,
    get_python_version,
    get_project_url
)

__all__ = [
    "greet", 
    "run_test_suite", 
    "pretty_print_results", 
    "generate_test_report",
    "get_project_name", 
    "get_version", 
    "get_author",
    "get_description",
    "get_license",
    "get_python_version",
    "get_project_url"
]