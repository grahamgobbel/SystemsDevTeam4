"""
Application Title: TCU Ambassador Scheduling System
Date: 2026-04-14
Authors: SystemsDevTeam4
Purpose: Create and return SQLite connections for the scheduling application.

The database file is stored in the user's temporary directory so the app can
write reliably even when the project lives in a synced workspace.
"""

import os
import sqlite3
import tempfile


DB_DIR = os.path.join(tempfile.gettempdir(), "SystemsDevTeam4")
DB_PATH = os.path.join(DB_DIR, "SQLite.db")


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection configured for the application.

    Inputs:
        None.
    Outputs:
        A SQLite connection with row_factory enabled for dict-like access.
    """
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
