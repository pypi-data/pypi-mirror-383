from flamecraft.info.project_info import get_project_name

def greet(name: str) -> str:
    """Return a friendly greeting."""
    return f"Hello, {name}! Welcome to {get_project_name()}."
