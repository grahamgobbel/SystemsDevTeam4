"""
queries.py - Example database query functions.

All functions accept a sqlite3.Connection (obtained from database.get_connection)
and return plain Python objects so callers are not coupled to the database layer.
"""

import sqlite3


# ---------------------------------------------------------------------------
# Table initialisation
# ---------------------------------------------------------------------------

def create_users_table(conn: sqlite3.Connection) -> None:
    """Create the 'users' table if it does not already exist."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            name  TEXT    NOT NULL,
            email TEXT    NOT NULL UNIQUE
        )
        """
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Write operations
# ---------------------------------------------------------------------------

def insert_user(conn: sqlite3.Connection, name: str, email: str) -> int:
    """
    Insert a new user row and return the new row's id.

    Parameters
    ----------
    conn  : open SQLite connection
    name  : display name for the user
    email : unique e-mail address for the user
    """
    cursor = conn.execute(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        (name, email),
    )
    conn.commit()
    return cursor.lastrowid


# ---------------------------------------------------------------------------
# Read operations
# ---------------------------------------------------------------------------

def get_all_users(conn: sqlite3.Connection) -> list[dict]:
    """
    Return all rows from the 'users' table as a list of dicts.

    Each dict has keys: id, name, email.
    """
    cursor = conn.execute("SELECT id, name, email FROM users")
    rows = cursor.fetchall()
    # Convert sqlite3.Row objects to plain dicts for easy use downstream
    return [dict(row) for row in rows]


def get_user_by_id(conn: sqlite3.Connection, user_id: int) -> dict | None:
    """
    Return the user with the given id, or None if not found.

    Parameters
    ----------
    conn    : open SQLite connection
    user_id : primary-key value to look up
    """
    cursor = conn.execute(
        "SELECT id, name, email FROM users WHERE id = ?",
        (user_id,),
    )
    row = cursor.fetchone()
    return dict(row) if row else None
