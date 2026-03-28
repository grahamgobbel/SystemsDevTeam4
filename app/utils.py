"""
utils.py - General-purpose helper functions used across the project.
"""

from datetime import datetime


def format_user(user: dict) -> str:
    """
    Return a human-readable string for a user dict.

    Expected keys: id, name, email.

    Example
    -------
    >>> format_user({"id": 1, "name": "Alice", "email": "alice@example.com"})
    '[1] Alice <alice@example.com>'
    """
    return f"[{user['id']}] {user['name']} <{user['email']}>"


def current_timestamp() -> str:
    """
    Return the current local date and time as a formatted string.

    Example output: '2025-01-15 09:30:00'
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def print_section(title: str) -> None:
    """
    Print a simple section header to stdout.

    Useful for producing readable output when running the project from the
    command line.
    """
    separator = "-" * 40
    print(f"\n{separator}")
    print(f"  {title}")
    print(separator)
