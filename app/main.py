"""
main.py - Entry point for the SystemsDevTeam4 project.

Run with:
    python app/main.py

What this script does:
    1. Opens a connection to the SQLite database (data/SQLite.db).
    2. Ensures the 'users' table exists.
    3. Inserts two sample users (if the table is empty).
    4. Retrieves and prints all users.
    5. Demonstrates a single-user lookup.
"""

from database import get_connection
from queries import create_users_table, insert_user, get_all_users, get_user_by_id
from utils import format_user, current_timestamp, print_section


def main() -> None:
    print_section("SystemsDevTeam4 — Project Startup")
    print(f"  Started at: {current_timestamp()}")

    # ------------------------------------------------------------------
    # 1. Open database connection
    # ------------------------------------------------------------------
    print_section("Connecting to database")
    conn = get_connection()
    print("  Connected to data/SQLite.db")

    # ------------------------------------------------------------------
    # 2. Ensure schema exists
    # ------------------------------------------------------------------
    create_users_table(conn)
    print("  'users' table ready")

    # ------------------------------------------------------------------
    # 3. Seed sample data (only when the table is empty)
    # ------------------------------------------------------------------
    print_section("Seeding sample data")
    existing_users = get_all_users(conn)
    if not existing_users:
        insert_user(conn, "Alice Smith", "alice@example.com")
        insert_user(conn, "Bob Jones",  "bob@example.com")
        print("  Inserted 2 sample users")
    else:
        print(f"  Table already contains {len(existing_users)} user(s) — skipping seed")

    # ------------------------------------------------------------------
    # 4. Display all users
    # ------------------------------------------------------------------
    print_section("All users")
    for user in get_all_users(conn):
        print(" ", format_user(user))

    # ------------------------------------------------------------------
    # 5. Look up a specific user
    # ------------------------------------------------------------------
    print_section("Look up user id=1")
    user = get_user_by_id(conn, 1)
    if user:
        print(" ", format_user(user))
    else:
        print("  User not found")

    # ------------------------------------------------------------------
    # Done
    # ------------------------------------------------------------------
    conn.close()
    print_section("Done")
    print(f"  Finished at: {current_timestamp()}\n")


if __name__ == "__main__":
    main()
