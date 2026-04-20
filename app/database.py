"""
Application Title: TCU Ambassador Scheduling System
Date: 2026-04-20
Authors: Graham Gobbel
Purpose: Create and return SQLite connections for the scheduling application.

The database file is stored in the data/ folder at the project root.
"""

import os
import sqlite3


# Database stored in data/ folder at project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DB_DIR = os.path.join(PROJECT_ROOT, "data")
DB_PATH = os.path.join(DB_DIR, "SQLite.db")


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection configured for the application.

    Inputs:
        None.
    Outputs:
        A SQLite connection with row_factory enabled for dict-like access.
    """
    # Ensure first-time runs can create the DB file successfully.
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    # Return rows as mapping-like objects for cleaner query helpers.
    conn.row_factory = sqlite3.Row
    return conn
