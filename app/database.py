"""
database.py - SQLite database connection setup.

Provides a function to get a connection to the SQLite database stored at
data/SQLite.db (relative to the project root). The database file is created
automatically if it does not yet exist.
"""

import sqlite3
import os

# Resolve the path to data/SQLite.db regardless of where the script is run from.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(_PROJECT_ROOT, "data", "SQLite.db")


def get_connection() -> sqlite3.Connection:
    """
    Return a new SQLite connection to data/SQLite.db.

    The database file (and the data/ directory) will be created automatically
    if they do not already exist.
    """
    # Ensure the data/ directory exists before opening the database
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    # Return rows as sqlite3.Row objects so columns can be accessed by name
    conn.row_factory = sqlite3.Row
    return conn
