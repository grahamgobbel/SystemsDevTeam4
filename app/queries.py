"""
Query and data shaping helpers for the TCU Ambassador Scheduling System.
"""

import sqlite3
from datetime import date


VALID_DAYS = ["Monday", "Tuesday", "Wednesday",
              "Thursday", "Friday", "Saturday", "Sunday"]
VALID_PRIORITIES = ["1st Priority",
                    "2nd Priority", "3rd Priority", "Low Priority"]
VALID_YEARS = ["Freshman", "Sophomore", "Junior", "Senior"]


def initialize_database(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            major TEXT,
            minor TEXT,
            year TEXT,
            personality TEXT,
            status TEXT DEFAULT 'Active',
            ambassador_since TEXT,
            tours_completed INTEGER DEFAULT 0,
            total_hours INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            detail TEXT NOT NULL,
            kind TEXT NOT NULL,
            age_label TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS availability_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            day TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            priority TEXT NOT NULL,
            submitted INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS tours (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tour_type TEXT NOT NULL,
            tour_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            location TEXT NOT NULL,
            ambassadors_needed INTEGER NOT NULL,
            published INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS tour_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tour_id INTEGER NOT NULL,
            ambassador_id INTEGER NOT NULL,
            FOREIGN KEY(tour_id) REFERENCES tours(id),
            FOREIGN KEY(ambassador_id) REFERENCES users(id)
        );
        """
    )
    conn.commit()

    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
        return

    users = [
        ("Admin Dashboard", "admin@tcu.edu", "", "admin",
         None, None, None, None, "Active", None, 0, 0),
        ("Ambassador User", "graham.gobbel@tcu.edu", "", "ambassador",
         "Computer Science", "Business", "Junior", "ENFP", "Active", "Fall 2024", 47, 24),
        ("Emily Johnson", "emily.johnson@tcu.edu", "", "ambassador", "Marketing",
         "Spanish", "Junior", "ENFJ", "Active", "Fall 2023", 31, 24),
        ("Michael Chen", "michael.chen@tcu.edu", "", "ambassador", "Finance",
         "Data Science", "Senior", "INTJ", "Active", "Fall 2022", 42, 30),
        ("Sarah Williams", "sarah.williams@tcu.edu", "", "ambassador", "Business Information Systems",
         "Psychology", "Sophomore", "INFJ", "Active", "Fall 2024", 18, 16),
        ("David Martinez", "david.martinez@tcu.edu", "", "ambassador", "Accounting",
         "Economics", "Junior", "ENTP", "Active", "Spring 2024", 22, 20),
        ("Jessica Brown", "jessica.brown@tcu.edu", "", "ambassador", "Strategic Communication",
         "Journalism", "Senior", "ESFJ", "Active", "Fall 2022", 39, 18),
        ("James Wilson", "james.wilson@tcu.edu", "", "ambassador",
         "Management", "Music", "Junior", "ISFP", "Active", "Fall 2023", 27, 22)
    ]
    conn.executemany(
        """
        INSERT INTO users (
            name, email, password, role, major, minor, year, personality, status,
            ambassador_since, tours_completed, total_hours
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        users,
    )

    ambassador_id = conn.execute(
        "SELECT id FROM users WHERE email = 'graham.gobbel@tcu.edu'").fetchone()[0]
    notifications = [
        (ambassador_id, "New schedule posted for next month (April)",
         "Please review and accept", "success", "1 hour ago"),
        (ambassador_id, "Tour conflict with your business leadership in APSU5 dm",
         "Review your submitted schedule", "warning", "2 minutes ago"),
        (ambassador_id, "There was a conflict with your business leadership",
         "Winter Miller requested you last Friday", "info", "1 hour ago"),
    ]
    conn.executemany(
        "INSERT INTO notifications (user_id, title, detail, kind, age_label) VALUES (?, ?, ?, ?, ?)", notifications)

    availability = [
        (ambassador_id, "Monday", "10:00 AM", "12:00 PM", "1st Priority", 1),
        (ambassador_id, "Tuesday", "01:00 PM", "03:00 PM", "2nd Priority", 1),
        (ambassador_id, "Thursday", "09:00 AM", "11:00 AM", "1st Priority", 1),
        (ambassador_id, "Friday", "02:00 PM", "04:00 PM", "3rd Priority", 1),
    ]
    conn.executemany(
        "INSERT INTO availability_slots (user_id, day, start_time, end_time, priority, submitted) VALUES (?, ?, ?, ?, ?, ?)",
        availability,
    )

    tours = [
        ("Tour Types", "2026-04-25", "01:30 PM", "03:30 PM", "Location", 1, 1),
        ("Freshman Orientation", "2026-04-26", "09:00 AM",
         "12:00 PM", "Brown-Lupton University Union", 1, 1),
        ("Monday at TCU", "2026-04-28", "10:00 AM",
         "11:30 AM", "Admissions Office", 2, 0),
        ("Transfer Student Tour", "2026-04-22", "11:00 AM",
         "01:00 PM", "Admissions Office", 2, 0),
    ]
    conn.executemany(
        "INSERT INTO tours (tour_type, tour_date, start_time, end_time, location, ambassadors_needed, published) VALUES (?, ?, ?, ?, ?, ?, ?)",
        tours,
    )

    assignments = [
        (1, ambassador_id),
        (2, ambassador_id),
        (4, 3),
    ]
    conn.executemany(
        "INSERT INTO tour_assignments (tour_id, ambassador_id) VALUES (?, ?)", assignments)
    conn.commit()


def lookup_user(conn: sqlite3.Connection, email: str, password: str, role: str):
    normalized_email = email.strip()
    if not normalized_email:
        return None

    normalized_role = role if role in {"admin", "ambassador"} else "ambassador"
    row = conn.execute(
        "SELECT id, name, email, role FROM users WHERE lower(email) = lower(?)",
        (normalized_email,),
    ).fetchone()

    if row:
        if row["role"] != normalized_role:
            conn.execute("UPDATE users SET role = ? WHERE id = ?",
                         (normalized_role, row["id"]))
            conn.commit()
            row = conn.execute(
                "SELECT id, name, email, role FROM users WHERE id = ?",
                (row["id"],),
            ).fetchone()
        return dict(row)

    local_part = normalized_email.split(
        "@", 1)[0] if "@" in normalized_email else normalized_email
    display_name = " ".join(part.capitalize() for part in local_part.replace(
        ".", " ").replace("_", " ").replace("-", " ").split()) or normalized_email
    conn.execute(
        """
        INSERT INTO users (
            name, email, password, role, major, minor, year, personality, status,
            ambassador_since, tours_completed, total_hours
        ) VALUES (?, ?, '', ?, NULL, NULL, NULL, NULL, 'Active', NULL, 0, 0)
        """,
        (display_name, normalized_email, normalized_role),
    )
    conn.commit()
    row = conn.execute(
        "SELECT id, name, email, role FROM users WHERE lower(email) = lower(?)",
        (normalized_email,),
    ).fetchone()
    return dict(row) if row else None


def build_ambassador_dashboard(conn: sqlite3.Connection, user_id: int) -> dict:
    user = _get_user(conn, user_id, "ambassador")
    notifications = [dict(row) for row in conn.execute(
        "SELECT title, detail, kind, age_label FROM notifications WHERE user_id = ? ORDER BY id", (user_id,)).fetchall()]
    assignments = [
        dict(row)
        for row in conn.execute(
            """
            SELECT tours.id, tours.tour_type, tours.tour_date, tours.start_time, tours.end_time, tours.location,
                   tours.ambassadors_needed,
                   CASE WHEN tours.published = 1 THEN 'confirmed' ELSE 'pending' END AS status
            FROM tours
            JOIN tour_assignments ON tour_assignments.tour_id = tours.id
            WHERE tour_assignments.ambassador_id = ?
            ORDER BY tours.tour_date
            """,
            (user_id,),
        ).fetchall()
    ]
    return {"user": user, "notifications": notifications, "assignments": assignments, "stats": {"total_tours": 12, "hours_completed": user["total_hours"], "upcoming_events": 3}}


def build_availability_page(conn: sqlite3.Connection, user_id: int, view: str, message: str = "", error: str = "") -> dict:
    user = _get_user(conn, user_id, "ambassador")
    slots = [dict(row) for row in conn.execute(
        "SELECT id, day, start_time, end_time, priority, submitted FROM availability_slots WHERE user_id = ? ORDER BY day, start_time", (user_id,)).fetchall()]
    return {
        "user": user,
        "view": view if view in {"dashboard", "weekly"} else "dashboard",
        "message": message,
        "error": error,
        "slots": slots,
        "days": VALID_DAYS,
        "priorities": VALID_PRIORITIES,
        "time_labels": _time_labels(),
        "week_label": "Week of April 6, 2026",
        "slot_count": len(slots),
    }


def build_profile_page(conn: sqlite3.Connection, user_id: int, message: str = "", error: str = "") -> dict:
    user = _get_user(conn, user_id, "ambassador")
    return {
        "user": user,
        "message": message,
        "error": error,
        "majors": ["Computer Science", "Marketing", "Finance", "Accounting", "Management", "Business Information Systems", "Strategic Communication"],
        "minors": ["", "Business", "Data Science", "Spanish", "Economics", "Psychology", "Journalism", "Music"],
        "years": VALID_YEARS,
        "personalities": ["ENFP", "ENFJ", "INFJ", "ENTP", "ISFP", "INTJ", "ESFJ"],
    }


def build_admin_dashboard(conn: sqlite3.Connection, user_id: int, message: str = "", error: str = "") -> dict:
    user = _get_user(conn, user_id, "admin")
    ambassadors = [dict(row) for row in conn.execute(
        "SELECT id, name, email, total_hours, major, year FROM users WHERE role = 'ambassador' ORDER BY name").fetchall()]
    tours = [
        dict(row)
        for row in conn.execute(
            """
            SELECT tours.id, tours.tour_type, tours.tour_date, tours.start_time, tours.end_time, tours.location,
                   tours.ambassadors_needed, tours.published,
                   COUNT(tour_assignments.id) AS assigned_count
            FROM tours
            LEFT JOIN tour_assignments ON tour_assignments.tour_id = tours.id
            GROUP BY tours.id
            ORDER BY tours.tour_date
            """
        ).fetchall()
    ]
    for tour in tours:
        eligible = [dict(row) for row in conn.execute(
            "SELECT id, name, email, total_hours FROM users WHERE role = 'ambassador' ORDER BY total_hours DESC, name LIMIT 3"
        ).fetchall()]
        tour["eligible"] = eligible
    scheduled = len(tours)
    assigned = sum(1 for tour in tours if tour["assigned_count"] > 0)
    unassigned = sum(1 for tour in tours if tour["assigned_count"] == 0)
    return {
        "user": user,
        "message": message,
        "error": error,
        "ambassadors": ambassadors,
        "tours": tours,
        "stats": {"total_ambassadors": len(ambassadors), "scheduled": scheduled, "assigned": assigned, "unassigned": unassigned},
    }


def add_availability_slot(conn: sqlite3.Connection, user_id: int, day: str, start_time: str, end_time: str, priority: str):
    if day not in VALID_DAYS:
        return False, "Choose a valid day of the week."
    if not start_time or not end_time or len(start_time) < 7 or len(end_time) < 7:
        return False, "Time slots must follow the HH:MM AM/PM format."
    if priority not in VALID_PRIORITIES:
        return False, "Choose one of the predefined priority rankings."
    if start_time >= end_time:
        return False, "End time must be later than start time."
    overlap = conn.execute(
        "SELECT COUNT(*) FROM availability_slots WHERE user_id = ? AND day = ? AND start_time = ? AND end_time = ?",
        (user_id, day, start_time, end_time),
    ).fetchone()[0]
    if overlap:
        return False, "Duplicate weekly slots are not allowed."
    conn.execute(
        "INSERT INTO availability_slots (user_id, day, start_time, end_time, priority, submitted) VALUES (?, ?, ?, ?, ?, 0)",
        (user_id, day, start_time, end_time, priority),
    )
    conn.commit()
    return True, "Weekly slot added successfully."


def update_profile(conn: sqlite3.Connection, user_id: int, major: str, minor: str, year: str, personality: str):
    if not major or not year:
        return False, "Major and year are required."
    if year not in VALID_YEARS:
        return False, "Choose a valid undergraduate year."
    conn.execute(
        "UPDATE users SET major = ?, minor = ?, year = ?, personality = ? WHERE id = ?",
        (major, minor, year, personality, user_id),
    )
    conn.commit()
    return True, "Profile changes saved."


def add_tour(conn: sqlite3.Connection, tour_type: str, tour_date: str, start_time: str, end_time: str, location: str, ambassadors_needed: int):
    if not all([tour_type, tour_date, start_time, end_time, location]):
        return False, "All tour fields are required."
    if ambassadors_needed < 1 or ambassadors_needed > 10:
        return False, "Ambassadors needed must stay within a reasonable range."
    conn.execute(
        "INSERT INTO tours (tour_type, tour_date, start_time, end_time, location, ambassadors_needed, published) VALUES (?, ?, ?, ?, ?, ?, 0)",
        (tour_type, tour_date, start_time, end_time, location, ambassadors_needed),
    )
    conn.commit()
    return True, "Tour created and ready for assignment."


def assign_ambassador_to_tour(conn: sqlite3.Connection, tour_id: int, ambassador_id: int):
    if tour_id <= 0 or ambassador_id <= 0:
        return False, "Select a valid tour and ambassador."
    exists = conn.execute(
        "SELECT COUNT(*) FROM tour_assignments WHERE tour_id = ? AND ambassador_id = ?",
        (tour_id, ambassador_id),
    ).fetchone()[0]
    if exists:
        return False, "That ambassador is already assigned to this tour."
    conn.execute("INSERT INTO tour_assignments (tour_id, ambassador_id) VALUES (?, ?)",
                 (tour_id, ambassador_id))
    conn.commit()
    return True, "Ambassador assigned to the tour."


def add_ambassador(conn: sqlite3.Connection, name: str, email: str, major: str, year: str):
    if not name or not email or not major or not year:
        return False, "Name, email, major, and year are required."
    if "@" not in email or not email.endswith(".edu"):
        return False, "Ambassador emails must include a valid return address."
    if conn.execute("SELECT COUNT(*) FROM users WHERE lower(email) = lower(?)", (email,)).fetchone()[0]:
        return False, "Only one profile is allowed per ambassador email."
    conn.execute(
        "INSERT INTO users (name, email, password, role, major, minor, year, personality, status, ambassador_since, tours_completed, total_hours) VALUES (?, ?, '', 'ambassador', ?, '', ?, 'ENFP', 'Active', ?, 0, 0)",
        (name, email, major, year, str(date.today().year)),
    )
    conn.commit()
    return True, "Ambassador added successfully."


def delete_ambassador(conn: sqlite3.Connection, ambassador_id: int):
    if ambassador_id <= 0:
        return False, "Select a valid ambassador."
    conn.execute(
        "DELETE FROM tour_assignments WHERE ambassador_id = ?", (ambassador_id,))
    conn.execute(
        "DELETE FROM availability_slots WHERE user_id = ?", (ambassador_id,))
    conn.execute("DELETE FROM notifications WHERE user_id = ?",
                 (ambassador_id,))
    conn.execute(
        "DELETE FROM users WHERE id = ? AND role = 'ambassador'", (ambassador_id,))
    conn.commit()
    return True, "Ambassador removed from the roster."


def publish_tours(conn: sqlite3.Connection):
    conn.execute("UPDATE tours SET published = 1")
    conn.commit()
    return True, "Tours published to ambassadors."


def _get_user(conn: sqlite3.Connection, user_id: int, role: str) -> dict:
    row = conn.execute(
        "SELECT * FROM users WHERE id = ? AND role = ?", (user_id, role)).fetchone()
    if not row:
        raise PermissionError
    return dict(row)


def _time_labels() -> list[str]:
    return ["8:00 AM", "9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM"]
