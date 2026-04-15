"""
Query and data shaping helpers for the TCU Ambassador Scheduling System.
"""

import sqlite3


VALID_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
VALID_PRIORITIES = ["1st Priority", "2nd Priority", "3rd Priority", "Low Priority"]
VALID_YEARS = ["Freshman", "Sophomore", "Junior", "Senior"]
VALID_TIMES = [
    "8:00 AM",
    "9:00 AM",
    "10:00 AM",
    "11:00 AM",
    "12:00 PM",
    "1:00 PM",
    "2:00 PM",
    "3:00 PM",
    "4:00 PM",
    "5:00 PM",
]

SLOT_REQUIREMENTS = [
    {"day": "Monday", "time": "10:00 AM", "needed": 7},
    {"day": "Tuesday", "time": "10:00 AM", "needed": 7},
    {"day": "Wednesday", "time": "10:00 AM", "needed": 8},
    {"day": "Thursday", "time": "10:00 AM", "needed": 8},
    {"day": "Friday", "time": "10:00 AM", "needed": 13},
    {"day": "Monday", "time": "2:00 PM", "needed": 9},
    {"day": "Tuesday", "time": "2:00 PM", "needed": 8},
    {"day": "Wednesday", "time": "2:00 PM", "needed": 8},
    {"day": "Thursday", "time": "2:00 PM", "needed": 9},
    {"day": "Friday", "time": "2:00 PM", "needed": 13},
]

DAY_INDEX = {day: index for index, day in enumerate(VALID_DAYS)}
PRIORITY_RANK = {
    "1st Priority": 0,
    "2nd Priority": 1,
    "3rd Priority": 2,
    "Low Priority": 3,
}


MORNING_NAMES = [
    "Blake Edwards",
    "Corey Blake Townsend",
    "Jasmine Durrant",
    "Leah Krampert",
    "Mary Helen Banks",
    "Regan Albertson",
    "Takeshi Suzuki",
    "Gracie Gadler",
    "Cameron La Marca",
    "Jadyn Suarez",
    "Joe Basile",
    "Meredith Vorndran",
    "Owen Sullivan",
    "Zander Mathes",
    "Katie Barnes",
    "Arleth Rivera",
    "Britton Majure",
    "Lillie Ciszek",
    "Logan Kohler",
    "Moti Okunrotifa",
    "Owen Mlakar",
    "Ryan Murray",
    "Carrington Henley",
    "Ava Miller",
    "Claire O'Connor",
    "Emma Huther",
    "Juan Barrio",
    "Roberto Basurto",
    "Tate Deshotels",
    "Teddy O'Hara",
    "Bella Rinaldi",
    "Cooper Quisenberry",
    "Jonah Felger",
    "Jordan Talley",
    "Leah Burcham",
    "Levi Miller",
    "Lizzie Vezzetti",
    "Mac Abele",
    "Reagan White",
    "Riann Alderson",
    "Sarah Kaler",
    "Silvia Romero",
    "Titus Fagan",
]

AFTERNOON_NAMES = [
    "Ashlynn Adams",
    "Camila Parra",
    "Eleni Simatacolos",
    "Jack Grace",
    "Jillian Sisley",
    "Johnny McMonagle",
    "Lily Macken",
    "Michel Graham",
    "Vincent Lopez",
    "Dylan King",
    "AJ Gonzalez",
    "Alexis Garcia",
    "Ayomide Lowo",
    "Caroline Patterson",
    "Daniel Mitchell",
    "Hampton Zidlicky",
    "Keira Braun",
    "Ace Reeder",
    "Addy Haas",
    "Dylan Markey",
    "Hannah Jones",
    "Lexi Kilpatrick",
    "Mia Vu",
    "Reagan Huscher",
    "Stephen Adeoye",
    "Amarachi Nwosu",
    "Charlie Brannen",
    "Charlotte Blank",
    "Franchesca Sabando",
    "Josh Roberts",
    "Kylie Elam",
    "Mike Hilbig",
    "Reese Westlund",
    "Samantha Youngblood",
    "Lilly Bundrant",
    "Chase Robinson",
    "Dulce Sancen",
    "Elise Tjin",
    "Jack Langloh",
    "Katherine Grace",
    "Lona Le",
    "Macy Bayer",
    "Omid Ghuman",
    "Riley Sullivan",
    "Sadie Kreter",
    "Sandra Crowder",
    "Sophia Dockstader",
]

SEED_AMBASSADORS = [
    {"name": "Graham Gobbel", "email": "graham.gobbel@tcu.edu", "major": "Computer Science", "minor": "Business", "year": "Junior", "personality": "ENFP", "since": "Fall 2024", "tours_completed": 47},
]

for name in MORNING_NAMES + AFTERNOON_NAMES:
    email = name.lower().replace("'", "").replace(".", "").replace(" ", ".") + "@tcu.edu"
    if email == "graham.gobbel@tcu.edu":
        continue
    SEED_AMBASSADORS.append(
        {
            "name": name,
            "email": email,
            "major": "Business Information Systems",
            "minor": "",
            "year": "Junior",
            "personality": "ENFP",
            "since": "Fall 2024",
            "tours_completed": 12,
        }
    )


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
            tours_completed INTEGER DEFAULT 0
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
        """
    )
    conn.commit()

    _ensure_user(
        conn,
        {
            "name": "Admin Dashboard",
            "email": "admin@tcu.edu",
            "major": "",
            "minor": "",
            "year": "",
            "personality": "",
            "since": "",
            "tours_completed": 0,
        },
        role="admin",
    )

    for ambassador in SEED_AMBASSADORS:
        ambassador_id = _ensure_user(conn, ambassador, role="ambassador")
        _ensure_seed_availability(conn, ambassador_id)

    graham_id = conn.execute(
        "SELECT id FROM users WHERE lower(email) = 'graham.gobbel@tcu.edu'"
    ).fetchone()[0]
    _ensure_notifications(conn, graham_id)
    conn.commit()


def lookup_user(conn: sqlite3.Connection, email: str, password: str, role: str):
    row = conn.execute(
        "SELECT id, name, email, role FROM users WHERE lower(email) = lower(?) AND password = ? AND role = ?",
        (email, password, role),
    ).fetchone()
    return dict(row) if row else None


def build_ambassador_dashboard(conn: sqlite3.Connection, user_id: int) -> dict:
    user = _get_user(conn, user_id, "ambassador")
    schedule = generate_weekly_schedule(conn)
    assignments = []
    for slot in schedule["slots"]:
        if any(item["id"] == user_id for item in slot["assigned"]):
            assignments.append(
                {
                    "tour_type": "Daily Tour",
                    "tour_date_label": slot["label"],
                    "tour_time": slot["time"],
                    "location": "Admissions Office",
                    "status": "confirmed" if slot["filled"] else "pending",
                }
            )
    notifications = [
        dict(row)
        for row in conn.execute(
            "SELECT title, detail, kind, age_label FROM notifications WHERE user_id = ? ORDER BY id",
            (user_id,),
        ).fetchall()
    ]
    return {
        "user": user,
        "notifications": notifications,
        "assignments": assignments,
        "stats": {
            "total_tours": len(assignments),
            "hours_completed": user["tours_completed"],
            "upcoming_events": len(assignments),
        },
    }


def build_availability_page(
    conn: sqlite3.Connection,
    user_id: int,
    view: str,
    message: str = "",
    error: str = "",
) -> dict:
    user = _get_user(conn, user_id, "ambassador")
    slots = [
        dict(row)
        for row in conn.execute(
            "SELECT id, day, start_time, end_time, priority, submitted FROM availability_slots WHERE user_id = ? ORDER BY CASE day WHEN 'Monday' THEN 1 WHEN 'Tuesday' THEN 2 WHEN 'Wednesday' THEN 3 WHEN 'Thursday' THEN 4 WHEN 'Friday' THEN 5 END, start_time",
            (user_id,),
        ).fetchall()
    ]
    grid = _build_availability_grid(slots)
    return {
        "user": user,
        "view": view if view in {"dashboard", "weekly"} else "dashboard",
        "message": message,
        "error": error,
        "slots": slots,
        "days": VALID_DAYS,
        "priorities": VALID_PRIORITIES,
        "time_labels": VALID_TIMES,
        "week_label": "Standard Weekly Daily Tour Schedule",
        "slot_count": len(slots),
        "grid": grid,
    }


def build_profile_page(conn: sqlite3.Connection, user_id: int, message: str = "", error: str = "") -> dict:
    user = _get_user(conn, user_id, "ambassador")
    return {
        "user": user,
        "message": message,
        "error": error,
        "majors": [
            "Computer Science",
            "Marketing",
            "Finance",
            "Accounting",
            "Management",
            "Business Information Systems",
            "Strategic Communication",
        ],
        "minors": ["", "Business", "Data Science", "Spanish", "Economics", "Psychology", "Journalism", "Music"],
        "years": VALID_YEARS,
        "personalities": ["ENFP", "ENFJ", "INFJ", "ENTP", "ISFP", "INTJ", "ESFJ"],
    }


def build_admin_dashboard(conn: sqlite3.Connection, user_id: int, message: str = "", error: str = "") -> dict:
    user = _get_user(conn, user_id, "admin")
    ambassadors = [
        dict(row)
        for row in conn.execute(
            "SELECT id, name, email, major, year, tours_completed FROM users WHERE role = 'ambassador' ORDER BY name"
        ).fetchall()
    ]
    schedule = generate_weekly_schedule(conn)
    return {
        "user": user,
        "message": message,
        "error": error,
        "ambassadors": ambassadors,
        "schedule": schedule,
        "stats": {
            "total_ambassadors": len(ambassadors),
            "tour_slots": len(schedule["slots"]),
            "filled_slots": sum(1 for slot in schedule["slots"] if slot["filled"]),
            "unfilled_positions": schedule["total_open_positions"],
        },
    }


def generate_weekly_schedule(conn: sqlite3.Connection) -> dict:
    ambassadors = [
        dict(row)
        for row in conn.execute(
            "SELECT id, name, email FROM users WHERE role = 'ambassador' ORDER BY name"
        ).fetchall()
    ]
    availability_rows = [
        dict(row)
        for row in conn.execute(
            "SELECT user_id, day, start_time, end_time, priority FROM availability_slots ORDER BY user_id, day, start_time"
        ).fetchall()
    ]
    availability_by_user = {}
    for row in availability_rows:
        availability_by_user.setdefault(row["user_id"], []).append(row)

    assignment_counts = {ambassador["id"]: 0 for ambassador in ambassadors}
    slots = []

    for requirement in SLOT_REQUIREMENTS:
        eligible = []
        for ambassador in ambassadors:
            best_priority = _best_priority_for_slot(
                availability_by_user.get(ambassador["id"], []),
                requirement["day"],
                requirement["time"],
            )
            if best_priority is None:
                continue
            eligible.append(
                {
                    "id": ambassador["id"],
                    "name": ambassador["name"],
                    "priority": best_priority,
                    "assignment_count": assignment_counts[ambassador["id"]],
                }
            )

        eligible.sort(
            key=lambda item: (
                PRIORITY_RANK[item["priority"]],
                item["assignment_count"],
                item["name"],
            )
        )
        selected = eligible[: requirement["needed"]]
        for item in selected:
            assignment_counts[item["id"]] += 1

        slots.append(
            {
                "day": requirement["day"],
                "time": requirement["time"],
                "label": f"{requirement['day']} - {requirement['time']}",
                "needed": requirement["needed"],
                "assigned": selected,
                "filled": len(selected) == requirement["needed"],
                "open_positions": requirement["needed"] - len(selected),
            }
        )

    slots_by_time = {
        "10:00 AM": [slot for slot in slots if slot["time"] == "10:00 AM"],
        "2:00 PM": [slot for slot in slots if slot["time"] == "2:00 PM"],
    }
    return {
        "slots": slots,
        "slots_by_time": slots_by_time,
        "total_open_positions": sum(slot["open_positions"] for slot in slots),
    }


def add_availability_slot(
    conn: sqlite3.Connection,
    user_id: int,
    day: str,
    start_time: str,
    end_time: str,
    priority: str,
):
    if day not in VALID_DAYS:
        return False, "Choose a valid weekday."
    if start_time not in VALID_TIMES or end_time not in VALID_TIMES:
        return False, "Choose start and end times from the list."
    if priority not in VALID_PRIORITIES:
        return False, "Choose one of the predefined priority rankings."
    start_minutes = _time_to_minutes(start_time)
    end_minutes = _time_to_minutes(end_time)
    if end_minutes <= start_minutes:
        return False, "End time must be later than start time."

    existing_rows = conn.execute(
        "SELECT start_time, end_time FROM availability_slots WHERE user_id = ? AND day = ?",
        (user_id, day),
    ).fetchall()
    for row in existing_rows:
        existing_start = _time_to_minutes(row["start_time"])
        existing_end = _time_to_minutes(row["end_time"])
        if start_minutes < existing_end and end_minutes > existing_start:
            return False, "Overlapping or duplicate entries are not allowed."

    conn.execute(
        "INSERT INTO availability_slots (user_id, day, start_time, end_time, priority, submitted) VALUES (?, ?, ?, ?, ?, 1)",
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


def add_ambassador(conn: sqlite3.Connection, name: str, email: str, major: str, year: str):
    if not name or not email or not major or not year:
        return False, "Name, email, major, and year are required."
    if "@" not in email or not email.endswith(".edu"):
        return False, "Ambassador emails must include a valid .edu return address."
    if conn.execute("SELECT COUNT(*) FROM users WHERE lower(email) = lower(?)", (email,)).fetchone()[0]:
        return False, "Only one profile is allowed per ambassador email."
    conn.execute(
        "INSERT INTO users (name, email, password, role, major, minor, year, personality, status, ambassador_since, tours_completed) VALUES (?, ?, 'frog2026', 'ambassador', ?, '', ?, 'ENFP', 'Active', 'Fall 2024', 0)",
        (name, email, major, year),
    )
    ambassador_id = conn.execute(
        "SELECT id FROM users WHERE lower(email) = lower(?)",
        (email,),
    ).fetchone()[0]
    _ensure_seed_availability(conn, ambassador_id)
    conn.commit()
    return True, "Ambassador added successfully."


def delete_ambassador(conn: sqlite3.Connection, ambassador_id: int):
    if ambassador_id <= 0:
        return False, "Select a valid ambassador."
    conn.execute("DELETE FROM availability_slots WHERE user_id = ?", (ambassador_id,))
    conn.execute("DELETE FROM notifications WHERE user_id = ?", (ambassador_id,))
    conn.execute("DELETE FROM users WHERE id = ? AND role = 'ambassador'", (ambassador_id,))
    conn.commit()
    return True, "Ambassador removed from the roster."


def _ensure_user(conn: sqlite3.Connection, data: dict, role: str) -> int:
    row = conn.execute(
        "SELECT id FROM users WHERE lower(email) = lower(?)",
        (data["email"],),
    ).fetchone()
    if row:
        conn.execute(
            "UPDATE users SET name = ?, role = ?, major = ?, minor = ?, year = ?, personality = ?, status = 'Active', ambassador_since = ?, tours_completed = ? WHERE id = ?",
            (
                data["name"],
                role,
                data.get("major", ""),
                data.get("minor", ""),
                data.get("year", ""),
                data.get("personality", ""),
                data.get("since", ""),
                data.get("tours_completed", 0),
                row[0],
            ),
        )
        return row[0]

    cursor = conn.execute(
        "INSERT INTO users (name, email, password, role, major, minor, year, personality, status, ambassador_since, tours_completed) VALUES (?, ?, 'frog2026', ?, ?, ?, ?, ?, 'Active', ?, ?)",
        (
            data["name"],
            data["email"],
            role,
            data.get("major", ""),
            data.get("minor", ""),
            data.get("year", ""),
            data.get("personality", ""),
            data.get("since", ""),
            data.get("tours_completed", 0),
        ),
    )
    return cursor.lastrowid


def _ensure_notifications(conn: sqlite3.Connection, user_id: int) -> None:
    count = conn.execute(
        "SELECT COUNT(*) FROM notifications WHERE user_id = ?",
        (user_id,),
    ).fetchone()[0]
    if count:
        return
    notifications = [
        (user_id, "Auto-generated daily tour schedule is live", "Review your weekly assignments.", "success", "Today"),
        (user_id, "Availability updates affect next refresh", "Add time blocks in Weekly Availability to improve assignments.", "info", "Today"),
        (user_id, "Friday staffing is the busiest", "Morning and afternoon Friday tours need the largest teams.", "warning", "Today"),
    ]
    conn.executemany(
        "INSERT INTO notifications (user_id, title, detail, kind, age_label) VALUES (?, ?, ?, ?, ?)",
        notifications,
    )


def _ensure_seed_availability(conn: sqlite3.Connection, user_id: int) -> None:
    count = conn.execute(
        "SELECT COUNT(*) FROM availability_slots WHERE user_id = ?",
        (user_id,),
    ).fetchone()[0]
    if count:
        return
    seed_slots = []
    for day in VALID_DAYS:
        seed_slots.append((user_id, day, "9:00 AM", "12:00 PM", "1st Priority", 1))
        seed_slots.append((user_id, day, "1:00 PM", "4:00 PM", "2nd Priority", 1))
    conn.executemany(
        "INSERT INTO availability_slots (user_id, day, start_time, end_time, priority, submitted) VALUES (?, ?, ?, ?, ?, ?)",
        seed_slots,
    )


def _get_user(conn: sqlite3.Connection, user_id: int, role: str) -> dict:
    row = conn.execute(
        "SELECT * FROM users WHERE id = ? AND role = ?",
        (user_id, role),
    ).fetchone()
    if not row:
        raise PermissionError
    return dict(row)


def _build_availability_grid(slots: list[dict]) -> dict:
    grid = {day: {time_label: "" for time_label in VALID_TIMES} for day in VALID_DAYS}
    for slot in slots:
        start_minutes = _time_to_minutes(slot["start_time"])
        end_minutes = _time_to_minutes(slot["end_time"])
        for time_label in VALID_TIMES:
            minute_value = _time_to_minutes(time_label)
            if start_minutes <= minute_value < end_minutes:
                grid[slot["day"]][time_label] = slot["priority"]
    return grid


def _best_priority_for_slot(availability_rows: list[dict], day: str, slot_time: str):
    target_minutes = _time_to_minutes(slot_time)
    best_priority = None
    for row in availability_rows:
        if row["day"] != day:
            continue
        start_minutes = _time_to_minutes(row["start_time"])
        end_minutes = _time_to_minutes(row["end_time"])
        if start_minutes <= target_minutes < end_minutes:
            if best_priority is None or PRIORITY_RANK[row["priority"]] < PRIORITY_RANK[best_priority]:
                best_priority = row["priority"]
    return best_priority


def _time_to_minutes(value: str) -> int:
    time_part, meridiem = value.split(" ")
    hour_string, minute_string = time_part.split(":")
    hour = int(hour_string)
    minute = int(minute_string)
    if meridiem == "PM" and hour != 12:
        hour += 12
    if meridiem == "AM" and hour == 12:
        hour = 0
    return hour * 60 + minute
