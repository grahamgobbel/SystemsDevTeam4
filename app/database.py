"""
database.py - SQLite database connection setup.

Stores the database in the user's local temp directory so the app can write
reliably even when the project itself lives in a synced OneDrive folder.
"""

import os
import sqlite3
import tempfile


DB_DIR = os.path.join(tempfile.gettempdir(), "SystemsDevTeam4")
DB_PATH = os.path.join(DB_DIR, "SQLite.db")


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection for the advising dashboard data."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn