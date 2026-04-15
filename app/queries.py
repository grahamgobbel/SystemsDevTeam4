"""
Application Title: TCU Ambassador Scheduling System
Date: 2026-04-14
Authors: SystemsDevTeam4
Purpose: Provide database setup, query helpers, validation, and dashboard
data shaping for the scheduling application.
"""

import random
import sqlite3
from datetime import date, datetime, timedelta


VALID_DAYS = ["Monday", "Tuesday", "Wednesday",
              "Thursday", "Friday", "Saturday", "Sunday"]
VALID_PRIORITIES = ["1st Priority",
                    "2nd Priority", "3rd Priority", "Low Priority"]
VALID_YEARS = ["Freshman", "Sophomore", "Junior", "Senior"]
INVOLVEMENT_LEVELS = ["High", "Medium", "Low"]
MAJOR_GROUPS = [
    ("Neeley School of Business", [
        "Accounting",
        "Business Information Systems",
        "Entrepreneurial Management",
        "Finance",
        "Marketing",
        "Supply Chain Management",
        "Business Analytics (BizTech)",
        "Management",
    ]),
    ("AddRan College of Liberal Arts", [
        "African American & Africana Studies",
        "Anthropology",
        "Asian Studies",
        "Comparative Race & Ethnic Studies",
        "Economics",
        "English",
        "Writing & Rhetoric",
        "Creative Writing",
        "Geography",
        "History",
        "International Relations",
        "Modern Language Studies",
        "Philosophy",
        "Political Science",
        "Religion",
        "Sociology",
        "Spanish & Hispanic Studies",
        "Women & Gender Studies",
    ]),
    ("College of Science & Engineering", [
        "Biology",
        "Biochemistry",
        "Chemistry",
        "Computer Science",
        "Data Science / Digital Culture & Data Analytics",
        "Engineering",
        "Environmental Science & Sustainability",
        "Environmental Earth Resources",
        "Geology",
        "Mathematics",
        "Physics",
        "Actuarial Science",
        "Astronomy",
    ]),
    ("Bob Schieffer College of Communication", [
        "Communication Studies",
        "Journalism",
        "Strategic Communication (PR/Advertising)",
        "Film, Television & Digital Media",
    ]),
    ("College of Fine Arts", [
        "Art Education",
        "Art History",
        "Studio Art",
        "Graphic Design",
        "Interior Design",
        "Fashion Merchandising",
        "Theatre",
        "Dance",
        "Music (multiple concentrations)",
        "Ballet / Contemporary Dance",
        "Arts Leadership & Entrepreneurship",
    ]),
    ("Harris College of Nursing & Health Sciences", [
        "Nursing",
        "Kinesiology",
        "Nutritional Sciences",
        "Athletic Training",
        "Speech-Language Pathology (Communication Disorders)",
    ]),
    ("College of Education", [
        "Early Childhood Education",
        "Middle School Education (various tracks)",
        "Secondary Education (various subjects)",
        "Youth Advocacy & Educational Studies",
        "Educational Studies (double major option)",
    ]),
    ("Other / Specialized", [
        "Ranch Management",
        "Aerospace Studies",
        "Military Science",
    ]),
]
MINOR_OPTIONS = [
    "Accounting",
    "Finance",
    "Marketing",
    "Entrepreneurship",
    "Business Analytics",
    "Economics",
    "Political Science",
    "Philosophy",
    "Religion",
    "Sociology",
    "History",
    "English",
    "Creative Writing",
    "Computer Science",
    "Mathematics",
    "Data Analytics",
    "Environmental Science",
    "Biology",
    "Digital Culture & Data Analytics",
    "Comparative Race & Ethnic Studies",
    "African American & Africana Studies",
    "Latinx Studies",
    "Women & Gender Studies",
    "Studio Art",
    "Design",
    "Theatre",
    "Dance",
    "Music",
    "Educational Studies",
    "Youth Advocacy",
    "Nursing",
    "Kinesiology",
    "Nutritional Sciences",
    "Athletic Training",
    "Speech-Language Pathology",
    "Aerospace Studies",
    "Military Science",
]

DAILY_TOUR_TYPE = "Daily Tour"
DAILY_TOUR_LOCATION = "Admissions Office"
MAX_AMBASSADORS = 85
SAMPLE_STUDENT_SPECS = [
    ("Ava Thompson", "Marketing", "Psychology", "Freshman", "High"),
    ("Liam Carter", "Finance", "Data Analytics", "Sophomore", "Medium"),
    ("Sophia Nguyen", "Biology", "Chemistry", "Junior", "High"),
    ("Noah Bennett", "Computer Science", "Mathematics", "Senior", "Low"),
    ("Isabella Flores", "Fashion Merchandising", "Business Analytics", "Sophomore", "High"),
    ("Ethan Brooks", "Accounting", "Information Systems", "Junior", "Medium"),
    ("Mia Patel", "Nursing", "Public Health", "Freshman", "Low"),
    ("Jackson Reed", "Economics", "Political Science", "Senior", "High"),
    ("Chloe Sanders", "Communication Studies", "Digital Media", "Junior", "Medium"),
    ("Lucas Kim", "Engineering", "Physics", "Sophomore", "Low"),
    ("Harper Collins", "English", "Creative Writing", "Senior", "High"),
    ("Aiden Murphy", "Supply Chain Management", "International Business", "Freshman", "Medium"),
    ("Ella Ramirez", "Education", "Spanish & Hispanic Studies", "Junior", "Low"),
    ("Mason Hughes", "Real Estate", "Finance", "Sophomore", "High"),
    ("Lily Foster", "Psychology", "Sociology", "Senior", "Medium"),
    ("Caleb Ward", "Business Information Systems", "Data Analytics", "Junior", "High"),
    ("Grace Kim", "Biochemistry", "Biology", "Sophomore", "Medium"),
    ("Dylan Price", "Political Science", "History", "Freshman", "Low"),
    ("Natalie Cruz", "Strategic Communication", "Marketing", "Senior", "High"),
    ("Owen Hayes", "Mathematics", "Computer Science", "Junior", "Medium"),
    ("Brooke Simmons", "Interior Design", "Studio Art", "Sophomore", "High"),
    ("Connor Blake", "Management", "Entrepreneurship", "Freshman", "Medium"),
    ("Zoe Patel", "Nutritional Sciences", "Kinesiology", "Senior", "Low"),
    ("Ryan Mitchell", "Physics", "Mathematics", "Junior", "High"),
    ("Madison Lee", "Graphic Design", "Design", "Sophomore", "Medium"),
    ("Tyler Scott", "Military Science", "Political Science", "Freshman", "Low"),
    ("Hannah Davis", "Sociology", "Women & Gender Studies", "Senior", "High"),
    ("Jake Turner", "Finance", "Economics", "Junior", "Medium"),
    ("Olivia Green", "Dance", "Theatre", "Sophomore", "High"),
    ("Andrew Cooper", "Computer Science", "Data Analytics", "Freshman", "Low"),
    ("Claire Watson", "Religion", "Philosophy", "Senior", "Medium"),
    ("Zachary Long", "Supply Chain Management", "Business Analytics", "Junior", "High"),
    ("Paige Bennett", "Speech-Language Pathology", "Kinesiology", "Sophomore", "Medium"),
    ("Brandon Ross", "Engineering", "Mathematics", "Freshman", "Low"),
    ("Sydney Howard", "Journalism", "English", "Senior", "High"),
    ("Kevin Nguyen", "Data Science / Digital Culture & Data Analytics", "Computer Science", "Junior", "Medium"),
    ("Lauren Price", "Early Childhood Education", "Educational Studies", "Sophomore", "High"),
    ("Trevor Hall", "Economics", "Finance", "Freshman", "Low"),
    ("Julia Brooks", "Theatre", "Creative Writing", "Senior", "Medium"),
    ("Cameron White", "Actuarial Science", "Mathematics", "Junior", "High"),
    ("Megan Kelly", "Environmental Science & Sustainability", "Environmental Science", "Sophomore", "Medium"),
    ("Austin Gray", "Accounting", "Finance", "Freshman", "Low"),
    ("Rachel Adams", "Spanish & Hispanic Studies", "Sociology", "Senior", "High"),
    ("Eric Foster", "Geology", "Environmental Science", "Junior", "Medium"),
    ("Sarah Bell", "Anthropology", "Comparative Race & Ethnic Studies", "Sophomore", "High"),
    ("Justin Parker", "Marketing", "Entrepreneurship", "Freshman", "Medium"),
    ("Emily Reed", "Nursing", "Nutritional Sciences", "Senior", "Low"),
    ("Dylan Hayes", "Management", "Political Science", "Junior", "High"),
    ("Katie Long", "Art History", "Studio Art", "Sophomore", "Medium"),
    ("Sean Murphy", "Computer Science", "Mathematics", "Freshman", "Low"),
    ("Abigail Turner", "Women & Gender Studies", "Sociology", "Senior", "High"),
    ("Luke Sanders", "Physics", "Astronomy", "Junior", "Medium"),
    ("Vanessa Cruz", "Strategic Communication", "Marketing", "Sophomore", "High"),
    ("Cole Bennett", "Ranch Management", "Business", "Freshman", "Low"),
    ("Brianna Scott", "Kinesiology", "Athletic Training", "Senior", "Medium"),
    ("Jordan Price", "Finance", "Accounting", "Junior", "High"),
    ("Lily Nguyen", "Fashion Merchandising", "Design", "Sophomore", "Medium"),
    ("Matthew Davis", "Engineering", "Computer Science", "Freshman", "Low"),
    ("Sophia Green", "Creative Writing", "English", "Senior", "High"),
    ("Tyler Brooks", "Supply Chain Management", "Business Analytics", "Junior", "Medium"),
    ("Emma Collins", "Biology", "Chemistry", "Sophomore", "High"),
    ("Jack Wilson", "Economics", "Data Analytics", "Freshman", "Medium"),
    ("Grace Turner", "Education", "Youth Advocacy", "Senior", "Low"),
    ("Alex Kim", "Data Science / Digital Culture & Data Analytics", "Mathematics", "Junior", "High"),
    ("Natalie White", "Journalism", "Political Science", "Sophomore", "Medium"),
    ("Ryan Adams", "Accounting", "Finance", "Freshman", "Low"),
    ("Chloe Hall", "Interior Design", "Design", "Senior", "High"),
    ("Ethan Parker", "Computer Science", "Data Analytics", "Junior", "Medium"),
    ("Madison Scott", "Nursing", "Kinesiology", "Sophomore", "High"),
    ("Logan Reed", "Military Science", "History", "Freshman", "Low"),
    ("Bella Martinez", "Spanish & Hispanic Studies", "Latinx Studies", "Senior", "High"),
    ("Carter Hughes", "Management", "Entrepreneurship", "Junior", "Medium"),
    ("Savannah Price", "Environmental Earth Resources", "Environmental Science", "Sophomore", "High"),
    ("Noah Gray", "Mathematics", "Actuarial Science", "Freshman", "Low"),
    ("Hailey Foster", "Communication Studies", "Sociology", "Senior", "Medium"),
    ("Ben Cooper", "Finance", "Business Analytics", "Junior", "High"),
    ("Kayla Watson", "Theatre", "Dance", "Sophomore", "Medium"),
    ("Mason Kelly", "Engineering", "Physics", "Freshman", "Low"),
]
DAILY_TOUR_SLOTS = [
    ("Monday", "10:00 AM", "11:00 AM", 7),
    ("Tuesday", "10:00 AM", "11:00 AM", 7),
    ("Wednesday", "10:00 AM", "11:00 AM", 8),
    ("Thursday", "10:00 AM", "11:00 AM", 8),
    ("Friday", "10:00 AM", "11:00 AM", 13),
    ("Monday", "02:00 PM", "03:00 PM", 9),
    ("Tuesday", "02:00 PM", "03:00 PM", 8),
    ("Wednesday", "02:00 PM", "03:00 PM", 8),
    ("Thursday", "02:00 PM", "03:00 PM", 9),
    ("Friday", "02:00 PM", "03:00 PM", 13),
]


def initialize_database(conn: sqlite3.Connection) -> None:
    """Create the database schema and seed required demo data.

    Inputs:
        conn: Open SQLite connection.
    Outputs:
        Creates tables and inserts starter data when needed.
    """
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

        CREATE TABLE IF NOT EXISTS app_meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        """
    )
    conn.commit()

    if not conn.execute("SELECT value FROM app_meta WHERE key = 'demo_seed_cleaned'").fetchone():
        ambassador_row = conn.execute(
            "SELECT id FROM users WHERE lower(email) = lower('graham.gobbel@tcu.edu')"
        ).fetchone()
        if ambassador_row:
            ambassador_id = ambassador_row[0]
            conn.execute(
                "DELETE FROM tour_assignments WHERE ambassador_id = ?", (ambassador_id,))
            conn.execute(
                "DELETE FROM notifications WHERE user_id = ?", (ambassador_id,))
            conn.execute(
                "DELETE FROM availability_slots WHERE user_id = ?", (ambassador_id,))
        conn.execute(
            "INSERT OR REPLACE INTO app_meta (key, value) VALUES ('demo_seed_cleaned', '1')"
        )
        conn.commit()

    if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
        _sync_fixed_daily_tours(conn)
        _normalize_ambassador_roster(conn, MAX_AMBASSADORS)
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

    conn.commit()

    _sync_fixed_daily_tours(conn)
    _normalize_ambassador_roster(conn, MAX_AMBASSADORS)


def lookup_user(conn: sqlite3.Connection, email: str, password: str, role: str):
    """Find or create a user record based on email and role.

    Inputs:
        conn: Open SQLite connection.
        email: User-provided email address.
        password: Unused placeholder kept for interface compatibility.
        role: Requested account role.
    Outputs:
        A dictionary with user details, or None when email is empty.
    """
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

    return None


def build_ambassador_dashboard(conn: sqlite3.Connection, user_id: int) -> dict:
    """Build the dashboard data for an ambassador.

    Inputs:
        conn: Open SQLite connection.
        user_id: Ambassador account id.
    Outputs:
        Dictionary containing the user record, assignments, notifications, and
        summary stats.
    """
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
    stats = _ambassador_stats(assignments)
    return {"user": user, "notifications": notifications, "assignments": assignments, "stats": stats}


def build_availability_page(conn: sqlite3.Connection, user_id: int, view: str, message: str = "", error: str = "") -> dict:
    """Build the data needed by the availability views.

    Inputs:
        conn: Open SQLite connection.
        user_id: Ambassador account id.
        view: Requested subview name.
        message: Success feedback text.
        error: Error feedback text.
    Outputs:
        Dictionary containing slots, labels, and view state.
    """
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
    """Build the data needed by the ambassador profile page.

    Inputs:
        conn: Open SQLite connection.
        user_id: Ambassador account id.
        message: Success feedback text.
        error: Error feedback text.
    Outputs:
        Dictionary containing profile options and account information.
    """
    user = _get_user(conn, user_id, "ambassador")
    tours_completed = conn.execute(
        "SELECT COUNT(*) FROM tour_assignments WHERE ambassador_id = ?",
        (user_id,),
    ).fetchone()[0]
    return {
        "user": user,
        "message": message,
        "error": error,
        "major_groups": MAJOR_GROUPS,
        "minors": MINOR_OPTIONS,
        "years": VALID_YEARS,
        "involvement_levels": INVOLVEMENT_LEVELS,
        "tours_completed": tours_completed,
    }


def build_admin_dashboard(
    conn: sqlite3.Connection,
    user_id: int,
    message: str = "",
    error: str = "",
    ambassador_search: str = "",
    tour_status: str = "all",
) -> dict:
    """Build the data needed by the admin dashboard.

    Inputs:
        conn: Open SQLite connection.
        user_id: Admin account id.
        message: Success feedback text.
        error: Error feedback text.
        ambassador_search: Search text for ambassadors.
        tour_status: Filter value for tours.
    Outputs:
        Dictionary containing ambassadors, tours, and summary stats.
    """
    user = _get_user(conn, user_id, "admin")
    _sync_fixed_daily_tours(conn)

    search_term = ambassador_search.strip()
    ambassador_filters = ["role = 'ambassador'"]
    ambassador_params: list[str] = []
    if search_term:
        wildcard = f"%{search_term}%"
        ambassador_filters.append(
            "(name LIKE ? OR email LIKE ? OR major LIKE ?)")
        ambassador_params.extend([wildcard, wildcard, wildcard])

    ambassador_query = (
        "SELECT id, name, email, total_hours, major, year "
        "FROM users WHERE " +
        " AND ".join(ambassador_filters) + " ORDER BY name"
    )
    ambassadors = [
        dict(row)
        for row in conn.execute(ambassador_query, tuple(ambassador_params)).fetchall()
    ]

    tours = [
        dict(row)
        for row in conn.execute(
            """
            SELECT tours.id, tours.tour_type, tours.tour_date, tours.start_time, tours.end_time, tours.location,
                   tours.ambassadors_needed, tours.published,
                   COUNT(tour_assignments.id) AS assigned_count
            FROM tours
            LEFT JOIN tour_assignments ON tour_assignments.tour_id = tours.id
            WHERE tours.tour_type = ?
            GROUP BY tours.id
            ORDER BY tours.tour_date
            """,
            (DAILY_TOUR_TYPE,),
        ).fetchall()
    ]

    normalized_tour_status = tour_status if tour_status in {
        "all", "published", "draft", "assigned", "unassigned"
    } else "all"

    if normalized_tour_status == "published":
        tours = [tour for tour in tours if tour["published"] == 1]
    elif normalized_tour_status == "draft":
        tours = [tour for tour in tours if tour["published"] == 0]
    elif normalized_tour_status == "assigned":
        tours = [
            tour
            for tour in tours
            if tour["assigned_count"] >= tour["ambassadors_needed"]
        ]
    elif normalized_tour_status == "unassigned":
        tours = [
            tour
            for tour in tours
            if tour["assigned_count"] < tour["ambassadors_needed"]
        ]

    availability_rows = [
        dict(row)
        for row in conn.execute(
            "SELECT user_id, day, start_time, end_time, priority FROM availability_slots"
        ).fetchall()
    ]
    slots_by_user: dict[int, list[dict]] = {}
    for slot in availability_rows:
        slots_by_user.setdefault(slot["user_id"], []).append(slot)

    for tour in tours:
        assigned_people = [
            dict(row)
            for row in conn.execute(
                """
                SELECT users.id, users.name
                FROM tour_assignments
                JOIN users ON users.id = tour_assignments.ambassador_id
                WHERE tour_assignments.tour_id = ?
                ORDER BY users.name
                """,
                (tour["id"],),
            ).fetchall()
        ]
        assigned_ids = {person["id"] for person in assigned_people}
        assigned_names = {person["name"] for person in assigned_people}
        tour_day = datetime.strptime(
            tour["tour_date"], "%Y-%m-%d").strftime("%A")

        eligible = []
        for ambassador in ambassadors:
            ambassador_id = ambassador["id"]
            if ambassador_id in assigned_ids:
                continue
            if ambassador["name"] in assigned_names:
                continue
            rank = _best_priority_for_tour(
                slots_by_user.get(ambassador_id, []),
                tour_day,
                tour["start_time"],
                tour["end_time"],
            )
            if rank is None:
                continue

            eligible.append(
                {
                    "id": ambassador_id,
                    "name": ambassador["name"],
                    "email": ambassador["email"],
                    "total_hours": ambassador["total_hours"],
                    "priority_rank": rank,
                    "priority": _priority_label_from_rank(rank),
                }
            )

        eligible.sort(key=lambda row: (
            row["priority_rank"], row["total_hours"], row["name"]))
        tour["eligible"] = eligible
        tour["assigned_names"] = [person["name"] for person in assigned_people]
        tour["remaining_slots"] = max(
            tour["ambassadors_needed"] - tour["assigned_count"], 0)

    report_query = (
        "SELECT users.id, users.name, users.email, users.major, users.year, users.total_hours, "
        "COUNT(tour_assignments.id) AS assigned_tours "
        "FROM users "
        "LEFT JOIN tour_assignments ON tour_assignments.ambassador_id = users.id "
        "WHERE role = 'ambassador'"
    )
    report_params: list[str] = []
    if search_term:
        wildcard = f"%{search_term}%"
        report_query += " AND (users.name LIKE ? OR users.email LIKE ? OR users.major LIKE ?)"
        report_params.extend([wildcard, wildcard, wildcard])
    report_query += " GROUP BY users.id ORDER BY assigned_tours DESC, users.total_hours DESC, users.name"
    report_rows = [
        dict(row)
        for row in conn.execute(report_query, tuple(report_params)).fetchall()
    ]

    assignment_totals = [row["assigned_tours"] for row in report_rows]
    avg_assigned = round(sum(assignment_totals) /
                         len(assignment_totals), 2) if assignment_totals else 0
    max_assigned = max(assignment_totals) if assignment_totals else 0

    scheduled = len(tours)
    assigned = sum(
        1
        for tour in tours
        if tour["assigned_count"] >= tour["ambassadors_needed"]
    )
    in_progress = sum(
        1
        for tour in tours
        if 0 < tour["assigned_count"] < tour["ambassadors_needed"]
    )
    unassigned = sum(
        1
        for tour in tours
        if tour["assigned_count"] == 0
    )
    return {
        "user": user,
        "message": message,
        "error": error,
        "ambassadors": ambassadors,
        "tours": tours,
        "filters": {
            "search": search_term,
            "tour_status": normalized_tour_status,
            "tour_status_options": ["all", "published", "draft", "assigned", "unassigned"],
        },
        "report": {
            "generated_on": date.today().isoformat(),
            "rows": report_rows,
            "total_rows": len(report_rows),
            "avg_assigned": avg_assigned,
            "max_assigned": max_assigned,
        },
        "stats": {
            "total_ambassadors": len(ambassadors),
            "scheduled": scheduled,
            "assigned": assigned,
            "in_progress": in_progress,
            "unassigned": unassigned,
        },
        "weekly_schedule": _build_weekly_schedule(conn),
    }


def add_availability_slot(conn: sqlite3.Connection, user_id: int, day: str, start_time: str, end_time: str, priority: str):
    """Add one availability slot for an ambassador.

    Inputs:
        conn: Open SQLite connection.
        user_id: Ambassador account id.
        day: Weekday name.
        start_time: Slot start time.
        end_time: Slot end time.
        priority: Priority ranking string.
    Outputs:
        Tuple of success flag and feedback message.
    """
    if day not in VALID_DAYS:
        return False, "Choose a valid day of the week."
    if not start_time or not end_time or len(start_time) < 7 or len(end_time) < 7:
        return False, "Time slots must follow the HH:MM AM/PM format."
    if priority not in VALID_PRIORITIES:
        return False, "Choose one of the predefined priority rankings."
    try:
        start_dt = datetime.strptime(start_time, "%I:%M %p")
        end_dt = datetime.strptime(end_time, "%I:%M %p")
    except ValueError:
        return False, "Time slots must follow the HH:MM AM/PM format."
    if start_dt >= end_dt:
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


def clear_availability_slots(conn: sqlite3.Connection, user_id: int):
    """Delete all availability slots for one ambassador.

    Inputs:
        conn: Open SQLite connection.
        user_id: Ambassador account id.
    Outputs:
        Tuple of success flag and feedback message.
    """
    if user_id <= 0:
        return False, "Invalid ambassador account."
    conn.execute(
        "DELETE FROM availability_slots WHERE user_id = ?", (user_id,))
    conn.commit()
    return True, "All weekly availability slots were cleared."


def update_profile(conn: sqlite3.Connection, user_id: int, major: str, minor: str, year: str, involvement_level: str):
    """Update an ambassador profile.

    Inputs:
        conn: Open SQLite connection.
        user_id: Ambassador account id.
        major: Selected major.
        minor: Selected minor.
        year: Undergraduate year.
        involvement_level: TCU involvement level.
    Outputs:
        Tuple of success flag and feedback message.
    """
    if not major or not year:
        return False, "Major and year are required."
    if year not in VALID_YEARS:
        return False, "Choose a valid undergraduate year."
    if involvement_level and involvement_level not in INVOLVEMENT_LEVELS:
        return False, "Choose a valid TCU involvement level."
    conn.execute(
        "UPDATE users SET major = ?, minor = ?, year = ?, personality = ? WHERE id = ?",
        (major, minor, year, involvement_level, user_id),
    )
    conn.commit()
    return True, "Profile changes saved."


def add_tour(conn: sqlite3.Connection, tour_type: str, tour_date: str, start_time: str, end_time: str, location: str, ambassadors_needed: int):
    """Insert a new tour record.

    Inputs:
        conn: Open SQLite connection.
        tour_type: Tour label.
        tour_date: Tour date string.
        start_time: Tour start time.
        end_time: Tour end time.
        location: Tour location.
        ambassadors_needed: Required ambassador count.
    Outputs:
        Tuple of success flag and feedback message.
    """
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
    """Assign one ambassador to one tour.

    Inputs:
        conn: Open SQLite connection.
        tour_id: Tour record id.
        ambassador_id: Ambassador user id.
    Outputs:
        Tuple of success flag and feedback message.
    """
    if tour_id <= 0 or ambassador_id <= 0:
        return False, "Select a valid tour and ambassador."

    tour = conn.execute(
        "SELECT id, tour_date, start_time, end_time, ambassadors_needed FROM tours WHERE id = ?",
        (tour_id,),
    ).fetchone()
    if not tour:
        return False, "Select a valid tour and ambassador."

    ambassador = conn.execute(
        "SELECT id, name FROM users WHERE id = ? AND role = 'ambassador'",
        (ambassador_id,),
    ).fetchone()
    if not ambassador:
        return False, "Select a valid tour and ambassador."

    assigned_count = conn.execute(
        "SELECT COUNT(*) FROM tour_assignments WHERE tour_id = ?",
        (tour_id,),
    ).fetchone()[0]
    if assigned_count >= tour["ambassadors_needed"]:
        return False, "This tour is already full."

    exists = conn.execute(
        "SELECT COUNT(*) FROM tour_assignments WHERE tour_id = ? AND ambassador_id = ?",
        (tour_id, ambassador_id),
    ).fetchone()[0]
    if exists:
        return False, "That ambassador is already assigned to this tour."

    same_name_exists = conn.execute(
        """
        SELECT COUNT(*)
        FROM tour_assignments
        JOIN users ON users.id = tour_assignments.ambassador_id
        WHERE tour_assignments.tour_id = ? AND users.name = ?
        """,
        (tour_id, ambassador["name"]),
    ).fetchone()[0]
    if same_name_exists:
        return False, "A person with that name is already assigned to this tour."

    slots = [
        dict(row)
        for row in conn.execute(
            "SELECT day, start_time, end_time, priority FROM availability_slots WHERE user_id = ?",
            (ambassador_id,),
        ).fetchall()
    ]
    day_name = datetime.strptime(tour["tour_date"], "%Y-%m-%d").strftime("%A")
    availability_rank = _best_priority_for_tour(
        slots,
        day_name,
        tour["start_time"],
        tour["end_time"],
    )
    if availability_rank is None:
        return False, "This ambassador is not available for that tour time."

    conn.execute("INSERT INTO tour_assignments (tour_id, ambassador_id) VALUES (?, ?)",
                 (tour_id, ambassador_id))
    conn.commit()
    return True, "Ambassador assigned to the tour."


def add_ambassador(conn: sqlite3.Connection, name: str, email: str, major: str, year: str):
    """Create a new ambassador account.

    Inputs:
        conn: Open SQLite connection.
        name: Display name.
        email: Ambassador email address.
        major: Selected major.
        year: Undergraduate year.
    Outputs:
        Tuple of success flag and feedback message.
    """
    if not name or not email or not major or not year:
        return False, "Name, email, major, and year are required."
    current_count = conn.execute(
        "SELECT COUNT(*) FROM users WHERE role = 'ambassador'"
    ).fetchone()[0]
    if current_count >= MAX_AMBASSADORS:
        return False, f"Roster is capped at {MAX_AMBASSADORS} ambassadors."
    if "@" not in email or not email.endswith(".edu"):
        return False, "Ambassador emails must include a valid return address."
    if conn.execute("SELECT COUNT(*) FROM users WHERE lower(email) = lower(?)", (email,)).fetchone()[0]:
        return False, "Only one profile is allowed per ambassador email."
    conn.execute(
        "INSERT INTO users (name, email, password, role, major, minor, year, personality, status, ambassador_since, tours_completed, total_hours) VALUES (?, ?, '', 'ambassador', ?, '', ?, 'Medium', 'Active', ?, 0, 0)",
        (name, email, major, year, str(date.today().year)),
    )
    conn.commit()
    return True, "Ambassador added successfully."


def delete_ambassador(conn: sqlite3.Connection, ambassador_id: int):
    """Delete an ambassador and related records.

    Inputs:
        conn: Open SQLite connection.
        ambassador_id: Ambassador user id.
    Outputs:
        Tuple of success flag and feedback message.
    """
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
    """Mark all tours as published.

    Inputs:
        conn: Open SQLite connection.
    Outputs:
        Tuple of success flag and feedback message.
    """
    conn.execute("UPDATE tours SET published = 1")
    conn.commit()
    return True, "Tours published to ambassadors."


def auto_assign_daily_tours(conn: sqlite3.Connection):
    """Automatically assign ambassadors to the fixed daily tours.

    Inputs:
        conn: Open SQLite connection.
    Outputs:
        Tuple of success flag and feedback message.
    """
    _sync_fixed_daily_tours(conn)

    conn.execute("DELETE FROM tour_assignments")

    tours = [
        dict(row)
        for row in conn.execute(
            """
            SELECT id, tour_date, start_time, end_time, ambassadors_needed
            FROM tours
            WHERE tour_type = ?
            ORDER BY tour_date, start_time
            """,
            (DAILY_TOUR_TYPE,),
        ).fetchall()
    ]
    ambassadors = [
        dict(row)
        for row in conn.execute(
            "SELECT id, name, total_hours FROM users WHERE role = 'ambassador' ORDER BY name"
        ).fetchall()
    ]
    slots = [
        dict(row)
        for row in conn.execute(
            "SELECT user_id, day, start_time, end_time, priority FROM availability_slots"
        ).fetchall()
    ]

    slots_by_user = {}
    for slot in slots:
        slots_by_user.setdefault(slot["user_id"], []).append(slot)

    assigned_tours_by_user = {amb["id"]: 0 for amb in ambassadors}
    assigned_days_by_user = {amb["id"]: set() for amb in ambassadors}
    total_needed = 0
    total_assigned = 0

    for tour in tours:
        tour_day = datetime.strptime(
            tour["tour_date"], "%Y-%m-%d").strftime("%A")
        candidates = []
        selected_names = set()
        for ambassador in ambassadors:
            user_id = ambassador["id"]
            name = ambassador["name"]
            if tour_day in assigned_days_by_user[user_id]:
                continue
            if name in selected_names:
                continue

            best_priority = _best_priority_for_tour(
                slots_by_user.get(user_id, []),
                tour_day,
                tour["start_time"],
                tour["end_time"],
            )
            if best_priority is None:
                continue

            candidates.append(
                (
                    best_priority,
                    assigned_tours_by_user[user_id],
                    ambassador["total_hours"],
                    name,
                    user_id,
                )
            )

        candidates.sort()
        selected = candidates[: tour["ambassadors_needed"]]

        for _, _, _, name, user_id in selected:
            conn.execute(
                "INSERT INTO tour_assignments (tour_id, ambassador_id) VALUES (?, ?)",
                (tour["id"], user_id),
            )
            assigned_tours_by_user[user_id] += 1
            assigned_days_by_user[user_id].add(tour_day)
            selected_names.add(name)

        total_needed += tour["ambassadors_needed"]
        total_assigned += len(selected)

    conn.commit()

    unfilled = total_needed - total_assigned
    if unfilled > 0:
        return True, f"Auto-assignment complete. Assigned {total_assigned} of {total_needed} slots ({unfilled} unfilled)."
    return True, f"Auto-assignment complete. Assigned all {total_needed} slots."


def seed_test_availability(conn: sqlite3.Connection):
    """Populate test availability slots with rotating priorities.

    Inputs:
        conn: Open SQLite connection.
    Outputs:
        Tuple of success flag and feedback message.
    """
    ambassadors = [
        dict(row)
        for row in conn.execute(
            "SELECT id FROM users WHERE role = 'ambassador' ORDER BY id"
        ).fetchall()
    ]
    if not ambassadors:
        return False, "No ambassadors found to seed availability."

    user_ids = [row["id"] for row in ambassadors]
    placeholders = ",".join(["?"] * len(user_ids))
    conn.execute(
        f"DELETE FROM availability_slots WHERE user_id IN ({placeholders})",
        tuple(user_ids),
    )

    weekday_slots = [
        ("Monday", "10:00 AM", "11:00 AM"),
        ("Monday", "02:00 PM", "03:00 PM"),
        ("Tuesday", "10:00 AM", "11:00 AM"),
        ("Tuesday", "02:00 PM", "03:00 PM"),
        ("Wednesday", "10:00 AM", "11:00 AM"),
        ("Wednesday", "02:00 PM", "03:00 PM"),
        ("Thursday", "10:00 AM", "11:00 AM"),
        ("Thursday", "02:00 PM", "03:00 PM"),
        ("Friday", "10:00 AM", "11:00 AM"),
        ("Friday", "02:00 PM", "03:00 PM"),
    ]

    rows_to_insert = []
    for ambassador in ambassadors:
        user_id = ambassador["id"]
        for slot_index, (day, start_time, end_time) in enumerate(weekday_slots):
            priority = VALID_PRIORITIES[(
                user_id + slot_index) % len(VALID_PRIORITIES)]
            rows_to_insert.append(
                (user_id, day, start_time, end_time, priority, 1))

    conn.executemany(
        "INSERT INTO availability_slots (user_id, day, start_time, end_time, priority, submitted) VALUES (?, ?, ?, ?, ?, ?)",
        rows_to_insert,
    )
    conn.commit()
    return True, f"Test availability generated for {len(ambassadors)} ambassadors."


def seed_sample_student_database(conn: sqlite3.Connection):
    """Replace ambassador records with the sample student roster and schedules.

    Inputs:
        conn: Open SQLite connection.
    Outputs:
        Tuple of success flag and feedback message.
    """
    if len(SAMPLE_STUDENT_SPECS) > MAX_AMBASSADORS:
        return False, f"Sample roster exceeds cap of {MAX_AMBASSADORS} ambassadors."

    ambassador_rows = [
        dict(row)
        for row in conn.execute(
            "SELECT id FROM users WHERE role = 'ambassador'"
        ).fetchall()
    ]
    ambassador_ids = [row["id"] for row in ambassador_rows]
    if ambassador_ids:
        placeholders = ",".join(["?"] * len(ambassador_ids))
        conn.execute(
            f"DELETE FROM tour_assignments WHERE ambassador_id IN ({placeholders})",
            tuple(ambassador_ids),
        )
        conn.execute(
            f"DELETE FROM availability_slots WHERE user_id IN ({placeholders})",
            tuple(ambassador_ids),
        )
        conn.execute(
            f"DELETE FROM notifications WHERE user_id IN ({placeholders})",
            tuple(ambassador_ids),
        )
        conn.execute(
            f"DELETE FROM users WHERE id IN ({placeholders})",
            tuple(ambassador_ids),
        )

    used_emails: set[str] = set()
    inserted_users: list[tuple[int, str]] = []
    for name, major, minor, year, involvement in SAMPLE_STUDENT_SPECS:
        email = _build_unique_email(name, used_emails)
        conn.execute(
            """
            INSERT INTO users (
                name, email, password, role, major, minor, year, personality, status,
                ambassador_since, tours_completed, total_hours
            ) VALUES (?, ?, '', 'ambassador', ?, ?, ?, ?, 'Active', ?, 0, 0)
            """,
            (name, email, major, minor, year, involvement, str(date.today().year)),
        )
        inserted_users.append((conn.execute("SELECT last_insert_rowid()").fetchone()[0], involvement))

    slot_templates = [
        ("Monday", "10:00 AM", "11:00 AM"),
        ("Monday", "02:00 PM", "03:00 PM"),
        ("Tuesday", "10:00 AM", "11:00 AM"),
        ("Tuesday", "02:00 PM", "03:00 PM"),
        ("Wednesday", "10:00 AM", "11:00 AM"),
        ("Wednesday", "02:00 PM", "03:00 PM"),
        ("Thursday", "10:00 AM", "11:00 AM"),
        ("Thursday", "02:00 PM", "03:00 PM"),
        ("Friday", "10:00 AM", "11:00 AM"),
        ("Friday", "02:00 PM", "03:00 PM"),
    ]
    rows_to_insert = []
    for user_id, involvement in inserted_users:
        rng = random.Random(user_id * 97)
        base_count = {
            "High": 8,
            "Medium": 6,
            "Low": 4,
        }.get(involvement, 5)
        slot_count = max(2, min(len(slot_templates), base_count + rng.choice([-1, 0, 1])))
        selected_slots = rng.sample(slot_templates, slot_count)
        for day, start_time, end_time in selected_slots:
            rows_to_insert.append(
                (
                    user_id,
                    day,
                    start_time,
                    end_time,
                    _random_priority_for_involvement(rng, involvement),
                    1,
                )
            )

    conn.executemany(
        "INSERT INTO availability_slots (user_id, day, start_time, end_time, priority, submitted) VALUES (?, ?, ?, ?, ?, ?)",
        rows_to_insert,
    )
    _sync_fixed_daily_tours(conn)
    conn.commit()
    return True, f"Sample student database created with {len(SAMPLE_STUDENT_SPECS)} ambassadors and {len(rows_to_insert)} weekly availability slots."


def _build_unique_email(name: str, used_emails: set[str]) -> str:
    """Generate unique TCU email addresses from full names."""
    parts = [part.lower() for part in name.split() if part]
    if not parts:
        parts = ["student"]
    base = f"{parts[0]}.{parts[-1]}"
    candidate = f"{base}@tcu.edu"
    suffix = 2
    while candidate in used_emails:
        candidate = f"{base}{suffix}@tcu.edu"
        suffix += 1
    used_emails.add(candidate)
    return candidate


def _random_priority_for_involvement(rng: random.Random, involvement: str) -> str:
    """Pick a realistic priority level based on involvement."""
    if involvement == "High":
        weights = [0.45, 0.30, 0.20, 0.05]
    elif involvement == "Medium":
        weights = [0.25, 0.35, 0.25, 0.15]
    else:
        weights = [0.10, 0.25, 0.35, 0.30]
    return rng.choices(VALID_PRIORITIES, weights=weights, k=1)[0]


def _get_user(conn: sqlite3.Connection, user_id: int, role: str) -> dict:
    """Load one user row for the requested role.

    Inputs:
        conn: Open SQLite connection.
        user_id: User record id.
        role: Expected role string.
    Outputs:
        User dictionary.
    """
    row = conn.execute(
        "SELECT * FROM users WHERE id = ? AND role = ?", (user_id, role)).fetchone()
    if not row:
        raise PermissionError
    return dict(row)


def _time_labels() -> list[str]:
    """Return the display labels used in the weekly availability grid.

    Inputs:
        None.
    Outputs:
        Ordered list of time labels.
    """
    return ["8:00 AM", "9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM"]


def _ambassador_stats(assignments: list[dict]) -> dict:
    """Summarize ambassador assignment data.

    Inputs:
        assignments: Assignment records for one ambassador.
    Outputs:
        Dictionary with totals, hours completed, and upcoming events.
    """
    today = date.today()
    total_tours = len(assignments)
    hours_completed = 0.0
    upcoming_events = 0

    for assignment in assignments:
        hours_completed += _tour_duration_hours(assignment.get(
            "start_time", ""), assignment.get("end_time", ""))
        tour_date = assignment.get("tour_date", "")
        if tour_date and tour_date >= today.isoformat():
            upcoming_events += 1

    hours_value = int(hours_completed) if hours_completed.is_integer(
    ) else round(hours_completed, 1)
    return {"total_tours": total_tours, "hours_completed": hours_value, "upcoming_events": upcoming_events}


def _tour_duration_hours(start_time: str, end_time: str) -> float:
    """Calculate tour duration in hours.

    Inputs:
        start_time: Start time string.
        end_time: End time string.
    Outputs:
        Duration in hours as a float.
    """
    if not start_time or not end_time:
        return 0.0
    start = datetime.strptime(start_time, "%I:%M %p")
    end = datetime.strptime(end_time, "%I:%M %p")
    duration = end - start
    return max(duration.total_seconds() / 3600, 0.0)


def _sync_fixed_daily_tours(conn: sqlite3.Connection) -> None:
    """Ensure this week has the required fixed daily tours.

    Inputs:
        conn: Open SQLite connection.
    Outputs:
        None.
    """
    monday = _week_monday(date.today())
    week_key = monday.isoformat()
    existing_key_row = conn.execute(
        "SELECT value FROM app_meta WHERE key = 'daily_tour_week_key'"
    ).fetchone()
    existing_key = existing_key_row[0] if existing_key_row else ""

    if existing_key == week_key:
        return

    conn.execute(
        "DELETE FROM tour_assignments WHERE tour_id IN (SELECT id FROM tours WHERE tour_type = ?)",
        (DAILY_TOUR_TYPE,),
    )
    conn.execute("DELETE FROM tours WHERE tour_type = ?", (DAILY_TOUR_TYPE,))

    date_by_day = {
        (monday + timedelta(days=offset)).strftime("%A"): (monday + timedelta(days=offset)).isoformat()
        for offset in range(7)
    }

    tours = [
        (
            DAILY_TOUR_TYPE,
            date_by_day[day],
            start_time,
            end_time,
            DAILY_TOUR_LOCATION,
            ambassadors_needed,
            1,
        )
        for day, start_time, end_time, ambassadors_needed in DAILY_TOUR_SLOTS
    ]
    conn.executemany(
        "INSERT INTO tours (tour_type, tour_date, start_time, end_time, location, ambassadors_needed, published) VALUES (?, ?, ?, ?, ?, ?, ?)",
        tours,
    )

    conn.execute(
        "INSERT OR REPLACE INTO app_meta (key, value) VALUES ('daily_tour_week_key', ?)",
        (week_key,),
    )
    conn.commit()


def _normalize_ambassador_roster(conn: sqlite3.Connection, max_ambassadors: int) -> None:
    """Limit the ambassador roster to the configured maximum.

    Inputs:
        conn: Open SQLite connection.
        max_ambassadors: Maximum ambassador records allowed.
    Outputs:
        None.
    """
    count = conn.execute(
        "SELECT COUNT(*) FROM users WHERE role = 'ambassador'"
    ).fetchone()[0]
    overflow = count - max_ambassadors
    if overflow <= 0:
        return

    remove_rows = conn.execute(
        "SELECT id FROM users WHERE role = 'ambassador' ORDER BY id DESC LIMIT ?",
        (overflow,),
    ).fetchall()
    remove_ids = [row[0] for row in remove_rows]
    if not remove_ids:
        return

    placeholders = ",".join(["?"] * len(remove_ids))
    conn.execute(
        f"DELETE FROM tour_assignments WHERE ambassador_id IN ({placeholders})",
        tuple(remove_ids),
    )
    conn.execute(
        f"DELETE FROM availability_slots WHERE user_id IN ({placeholders})",
        tuple(remove_ids),
    )
    conn.execute(
        f"DELETE FROM notifications WHERE user_id IN ({placeholders})",
        tuple(remove_ids),
    )
    conn.execute(
        f"DELETE FROM users WHERE id IN ({placeholders})",
        tuple(remove_ids),
    )
    conn.commit()


def _week_monday(anchor: date) -> date:
    """Return the Monday date for the week containing anchor.

    Inputs:
        anchor: Any date.
    Outputs:
        Date of that week's Monday.
    """
    return anchor - timedelta(days=anchor.weekday())


def _best_priority_for_tour(slots: list[dict], day: str, start_time: str, end_time: str):
    """Return the best availability priority rank for a tour time.

    Inputs:
        slots: Ambassador availability slots.
        day: Tour day name.
        start_time: Tour start time.
        end_time: Tour end time.
    Outputs:
        Lowest priority rank or None when unavailable.
    """
    tour_start = datetime.strptime(start_time, "%I:%M %p")
    tour_end = datetime.strptime(end_time, "%I:%M %p")
    ranks = []

    for slot in slots:
        if slot["day"] != day:
            continue
        slot_start = datetime.strptime(slot["start_time"], "%I:%M %p")
        slot_end = datetime.strptime(slot["end_time"], "%I:%M %p")
        if slot_start <= tour_start and slot_end >= tour_end:
            ranks.append(_priority_rank(slot))

    if not ranks:
        return None
    return min(ranks)


def _build_weekly_schedule(conn: sqlite3.Connection) -> dict:
    """Build a Monday-Friday schedule payload for the admin page.

    Inputs:
        conn: Open SQLite connection.
    Outputs:
        Structured schedule data for 10 AM and 2 PM tables.
    """
    rows = [
        dict(row)
        for row in conn.execute(
            """
            SELECT tours.id, tours.tour_date, tours.start_time, tours.ambassadors_needed, users.name
            FROM tours
            LEFT JOIN tour_assignments ON tour_assignments.tour_id = tours.id
            LEFT JOIN users ON users.id = tour_assignments.ambassador_id
            WHERE tours.tour_type = ?
            ORDER BY tours.tour_date, tours.start_time, users.name
            """,
            (DAILY_TOUR_TYPE,),
        ).fetchall()
    ]

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    schedule = {
        "10:00 AM": {day: {"needed": 0, "names": []} for day in days},
        "02:00 PM": {day: {"needed": 0, "names": []} for day in days},
    }

    for row in rows:
        day = datetime.strptime(row["tour_date"], "%Y-%m-%d").strftime("%A")
        time = row["start_time"]
        if day not in days or time not in schedule:
            continue
        schedule[time][day]["needed"] = row["ambassadors_needed"]
        if row["name"]:
            schedule[time][day]["names"].append(row["name"])

    for time in schedule:
        for day in days:
            needed = schedule[time][day]["needed"]
            names = schedule[time][day]["names"]
            remaining = max(needed - len(names), 0)
            if remaining > 0:
                names.extend(["Unassigned"] * remaining)

    return {
        "days": days,
        "morning": schedule["10:00 AM"],
        "afternoon": schedule["02:00 PM"],
    }


def _priority_rank(slot: dict) -> int:
    """Map a slot priority to a sort order.

    Inputs:
        slot: Availability slot record.
    Outputs:
        Numeric rank where lower means higher priority.
    """
    ranks = {
        "1st Priority": 0,
        "2nd Priority": 1,
        "3rd Priority": 2,
        "Low Priority": 3,
    }
    return ranks.get(slot.get("priority", ""), 99)


def _priority_label_from_rank(rank: int) -> str:
    """Convert a numeric priority rank into its display label.

    Inputs:
        rank: Priority rank from _priority_rank.
    Outputs:
        Display label used in the admin UI.
    """
    labels = {
        0: "1st Priority",
        1: "2nd Priority",
        2: "3rd Priority",
        3: "Low Priority",
    }
    return labels.get(rank, "Unknown")
