"""
Application Title: TCU Ambassador Scheduling System
Date: 2026-04-14
Authors: SystemsDevTeam4
Purpose: Provide database setup, query helpers, validation, and dashboard
data shaping for the scheduling application.
"""

import sqlite3
from datetime import date, datetime


VALID_DAYS = ["Monday", "Tuesday", "Wednesday",
              "Thursday", "Friday", "Saturday", "Sunday"]
VALID_PRIORITIES = ["1st Priority",
                    "2nd Priority", "3rd Priority", "Low Priority"]
VALID_YEARS = ["Freshman", "Sophomore", "Junior", "Senior"]
VALID_PERSONALITIES = ["Introvert", "Ambivert", "Extrovert"]
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

HARD_CODED_AMBASSADORS = [
    ("Ava Thompson", "ava.thompson@tcu.edu",
     "Marketing", "Spanish", "Freshman", "Ambivert"),
    ("Liam Carter", "liam.carter@tcu.edu", "Finance",
     "Economics", "Sophomore", "Extrovert"),
    ("Noah Bennett", "noah.bennett@tcu.edu",
     "Computer Science", "Mathematics", "Junior", "Introvert"),
    ("Emma Collins", "emma.collins@tcu.edu",
     "Accounting", "", "Senior", "Ambivert"),
    ("Olivia Ramirez", "olivia.ramirez@tcu.edu",
     "Strategic Communication (PR/Advertising)", "Journalism", "Freshman", "Extrovert"),
    ("Elijah Brooks", "elijah.brooks@tcu.edu", "Management",
     "Entrepreneurship", "Sophomore", "Ambivert"),
    ("Sophia Reed", "sophia.reed@tcu.edu", "Business Information Systems",
     "Data Analytics", "Junior", "Introvert"),
    ("Mason Hayes", "mason.hayes@tcu.edu", "Supply Chain Management",
     "Business Analytics", "Senior", "Ambivert"),
    ("Isabella Jenkins", "isabella.jenkins@tcu.edu",
     "Nursing", "", "Freshman", "Extrovert"),
    ("Lucas Foster", "lucas.foster@tcu.edu", "Kinesiology",
     "Nutritional Sciences", "Sophomore", "Ambivert"),
    ("Mia Howard", "mia.howard@tcu.edu", "Psychology",
     "Sociology", "Junior", "Introvert"),
    ("Ethan Morris", "ethan.morris@tcu.edu",
     "Economics", "Finance", "Senior", "Ambivert"),
    ("Amelia Diaz", "amelia.diaz@tcu.edu", "English",
     "Creative Writing", "Freshman", "Extrovert"),
    ("Logan Price", "logan.price@tcu.edu", "History",
     "Political Science", "Sophomore", "Ambivert"),
    ("Harper Long", "harper.long@tcu.edu",
     "Biology", "Chemistry", "Junior", "Introvert"),
    ("Jackson Ward", "jackson.ward@tcu.edu",
     "Engineering", "Mathematics", "Senior", "Ambivert"),
    ("Evelyn Perry", "evelyn.perry@tcu.edu",
     "Studio Art", "Design", "Freshman", "Extrovert"),
    ("Aiden Cooper", "aiden.cooper@tcu.edu",
     "Graphic Design", "Studio Art", "Sophomore", "Ambivert"),
    ("Scarlett Kelly", "scarlett.kelly@tcu.edu", "Interior Design",
     "Fashion Merchandising", "Junior", "Ambivert"),
    ("Henry Ross", "henry.ross@tcu.edu", "Film, Television & Digital Media",
     "Journalism", "Senior", "Extrovert"),
    ("Aria Barnes", "aria.barnes@tcu.edu",
     "Communication Studies", "Marketing", "Freshman", "Ambivert"),
    ("Wyatt Powell", "wyatt.powell@tcu.edu", "Journalism",
     "Strategic Communication (PR/Advertising)", "Sophomore", "Extrovert"),
    ("Ella Simmons", "ella.simmons@tcu.edu",
     "Anthropology", "Religion", "Junior", "Introvert"),
    ("Leo Butler", "leo.butler@tcu.edu",
     "Philosophy", "History", "Senior", "Ambivert"),
    ("Chloe Patterson", "chloe.patterson@tcu.edu",
     "International Relations", "Political Science", "Freshman", "Ambivert"),
    ("Owen Hughes", "owen.hughes@tcu.edu", "Mathematics",
     "Computer Science", "Sophomore", "Introvert"),
    ("Grace Bell", "grace.bell@tcu.edu", "Physics",
     "Astronomy", "Junior", "Introvert"),
    ("Caleb Rivera", "caleb.rivera@tcu.edu",
     "Environmental Science & Sustainability", "Biology", "Senior", "Ambivert"),
    ("Lily Flores", "lily.flores@tcu.edu",
     "Environmental Earth Resources", "Geology", "Freshman", "Ambivert"),
    ("Gabriel Nguyen", "gabriel.nguyen@tcu.edu",
     "Actuarial Science", "Economics", "Sophomore", "Introvert"),
    ("Zoe Sanders", "zoe.sanders@tcu.edu", "Data Science / Digital Culture & Data Analytics",
     "Data Analytics", "Junior", "Ambivert"),
    ("Julian Ortega", "julian.ortega@tcu.edu", "Accounting",
     "Business Analytics", "Senior", "Extrovert"),
    ("Nora Phillips", "nora.phillips@tcu.edu",
     "Finance", "Management", "Freshman", "Ambivert"),
    ("Samuel Kim", "samuel.kim@tcu.edu", "Marketing",
     "Entrepreneurship", "Sophomore", "Extrovert"),
    ("Riley Evans", "riley.evans@tcu.edu", "Business Information Systems",
     "Computer Science", "Junior", "Introvert"),
    ("Levi Turner", "levi.turner@tcu.edu",
     "Management", "Music", "Senior", "Ambivert"),
    ("Hannah Scott", "hannah.scott@tcu.edu",
     "Nutritional Sciences", "Kinesiology", "Freshman", "Ambivert"),
    ("Dylan Cruz", "dylan.cruz@tcu.edu", "Speech-Language Pathology (Communication Disorders)",
     "Psychology", "Sophomore", "Introvert"),
    ("Stella Griffin", "stella.griffin@tcu.edu", "Early Childhood Education",
     "Educational Studies", "Junior", "Extrovert"),
    ("Asher Owens", "asher.owens@tcu.edu",
     "Secondary Education (various subjects)", "History", "Senior", "Ambivert"),
    ("Layla Bryant", "layla.bryant@tcu.edu",
     "Youth Advocacy & Educational Studies", "Sociology", "Freshman", "Ambivert"),
    ("Carter Richardson", "carter.richardson@tcu.edu",
     "Educational Studies (double major option)", "Political Science", "Sophomore", "Introvert"),
    ("Penelope Cox", "penelope.cox@tcu.edu", "Spanish & Hispanic Studies",
     "International Relations", "Junior", "Extrovert"),
    ("Jayden Wood", "jayden.wood@tcu.edu",
     "Writing & Rhetoric", "English", "Senior", "Ambivert"),
    ("Audrey Washington", "audrey.washington@tcu.edu",
     "Creative Writing", "English", "Freshman", "Introvert"),
    ("Lincoln Stewart", "lincoln.stewart@tcu.edu",
     "Geography", "History", "Sophomore", "Ambivert"),
    ("Savannah Gray", "savannah.gray@tcu.edu",
     "Religion", "Philosophy", "Junior", "Ambivert"),
    ("Isaac Murphy", "isaac.murphy@tcu.edu", "Sociology",
     "Women & Gender Studies", "Senior", "Extrovert"),
    ("Addison Torres", "addison.torres@tcu.edu",
     "Women & Gender Studies", "Sociology", "Freshman", "Ambivert"),
    ("Mateo Russell", "mateo.russell@tcu.edu", "African American & Africana Studies",
     "Comparative Race & Ethnic Studies", "Sophomore", "Extrovert"),
    ("Victoria Hamilton", "victoria.hamilton@tcu.edu", "Comparative Race & Ethnic Studies",
     "African American & Africana Studies", "Junior", "Ambivert"),
    ("Josiah Graham", "josiah.graham@tcu.edu", "Asian Studies",
     "International Relations", "Senior", "Introvert"),
    ("Claire Sullivan", "claire.sullivan@tcu.edu", "Modern Language Studies",
     "Spanish & Hispanic Studies", "Freshman", "Ambivert"),
    ("Thomas Wallace", "thomas.wallace@tcu.edu", "Ranch Management",
     "Environmental Science", "Sophomore", "Ambivert"),
    ("Skylar West", "skylar.west@tcu.edu", "Aerospace Studies",
     "Military Science", "Junior", "Extrovert"),
    ("Charles Cole", "charles.cole@tcu.edu", "Military Science",
     "Aerospace Studies", "Senior", "Ambivert"),
    ("Lucy Jordan", "lucy.jordan@tcu.edu",
     "Dance", "Theatre", "Freshman", "Extrovert"),
    ("Christopher Dean", "christopher.dean@tcu.edu",
     "Theatre", "Dance", "Sophomore", "Ambivert"),
    ("Paisley Hunter", "paisley.hunter@tcu.edu", "Music (multiple concentrations)",
     "Arts Leadership & Entrepreneurship", "Junior", "Ambivert"),
    ("Andrew Hicks", "andrew.hicks@tcu.edu",
     "Ballet / Contemporary Dance", "Dance", "Senior", "Extrovert"),
    ("Natalie Schmidt", "natalie.schmidt@tcu.edu",
     "Art Education", "Studio Art", "Freshman", "Ambivert"),
    ("Nathan Weaver", "nathan.weaver@tcu.edu",
     "Art History", "Studio Art", "Sophomore", "Introvert"),
    ("Ellie Hansen", "ellie.hansen@tcu.edu", "Fashion Merchandising",
     "Interior Design", "Junior", "Ambivert"),
    ("Ryan Ford", "ryan.ford@tcu.edu", "Business Analytics (BizTech)",
     "Business Information Systems", "Senior", "Introvert"),
    ("Brooklyn Riley", "brooklyn.riley@tcu.edu",
     "Entrepreneurial Management", "Marketing", "Freshman", "Extrovert"),
    ("Adrian Chavez", "adrian.chavez@tcu.edu",
     "Supply Chain Management", "Finance", "Sophomore", "Ambivert"),
    ("Kennedy Lawson", "kennedy.lawson@tcu.edu",
     "Computer Science", "Data Analytics", "Junior", "Introvert"),
    ("Aaron Meyers", "aaron.meyers@tcu.edu",
     "Chemistry", "Biochemistry", "Senior", "Introvert"),
    ("Maya Pierce", "maya.pierce@tcu.edu",
     "Biochemistry", "Chemistry", "Freshman", "Ambivert"),
    ("Isaiah Stone", "isaiah.stone@tcu.edu", "Geology",
     "Environmental Earth Resources", "Sophomore", "Ambivert"),
    ("Anna Hawkins", "anna.hawkins@tcu.edu",
     "Political Science", "Economics", "Junior", "Extrovert"),
    ("Connor Walters", "connor.walters@tcu.edu",
     "Economics", "Political Science", "Senior", "Ambivert"),
    ("Sophie Carr", "sophie.carr@tcu.edu", "English",
     "Writing & Rhetoric", "Freshman", "Introvert"),
    ("Jonathan Harper", "jonathan.harper@tcu.edu",
     "History", "Religion", "Sophomore", "Ambivert"),
    ("Sarah Delgado", "sarah.delgado@tcu.edu", "Journalism",
     "Communication Studies", "Junior", "Extrovert"),
    ("Dominic Wade", "dominic.wade@tcu.edu",
     "Communication Studies", "Journalism", "Senior", "Ambivert"),
    ("Madeline Boyd", "madeline.boyd@tcu.edu",
     "Strategic Communication (PR/Advertising)", "Marketing", "Freshman", "Extrovert"),
    ("Evan Parks", "evan.parks@tcu.edu", "Management",
     "Entrepreneurship", "Sophomore", "Ambivert"),
    ("Allison Webb", "allison.webb@tcu.edu",
     "Finance", "Accounting", "Junior", "Introvert"),
    ("Robert Romero", "robert.romero@tcu.edu",
     "Accounting", "Finance", "Senior", "Ambivert"),
    ("Caroline Miles", "caroline.miles@tcu.edu", "Marketing",
     "Business Analytics", "Freshman", "Extrovert"),
    ("Xavier Medina", "xavier.medina@tcu.edu", "Business Information Systems",
     "Computer Science", "Sophomore", "Introvert"),
    ("Julia Kelley", "julia.kelley@tcu.edu", "Nursing", "", "Junior", "Ambivert"),
    ("Brayden Bishop", "brayden.bishop@tcu.edu", "Kinesiology",
     "Nutritional Sciences", "Senior", "Extrovert"),
    ("Mackenzie Gardner", "mackenzie.gardner@tcu.edu",
     "Speech-Language Pathology (Communication Disorders)", "Psychology", "Freshman", "Ambivert"),
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

    placeholders = ", ".join(["?" for _ in VALID_PERSONALITIES])
    conn.execute(
        f"""
        UPDATE users
        SET personality = 'Ambivert'
        WHERE role = 'ambassador'
          AND personality IS NOT NULL
          AND personality != ''
          AND personality NOT IN ({placeholders})
        """,
        tuple(VALID_PERSONALITIES),
    )
    conn.commit()

    sample_ambassadors = _hard_coded_ambassador_rows()

    if not conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
        users = [
            ("Admin Dashboard", "admin@tcu.edu", "", "admin",
             None, None, None, None, "Active", None, 0, 0),
        ]
        users.extend(sample_ambassadors)
        conn.executemany(
            """
            INSERT INTO users (
                name, email, password, role, major, minor, year, personality, status,
                ambassador_since, tours_completed, total_hours
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            users,
        )
    else:
        admin_exists = conn.execute(
            "SELECT COUNT(*) FROM users WHERE lower(email) = lower('admin@tcu.edu') AND role = 'admin'"
        ).fetchone()[0]
        if not admin_exists:
            conn.execute(
                """
                INSERT INTO users (
                    name, email, password, role, major, minor, year, personality, status,
                    ambassador_since, tours_completed, total_hours
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                ("Admin Dashboard", "admin@tcu.edu", "", "admin",
                 None, None, None, None, "Active", None, 0, 0),
            )

        existing_emails = {
            row[0].lower()
            for row in conn.execute(
                "SELECT email FROM users WHERE role = 'ambassador'"
            ).fetchall()
        }
        missing_ambassadors = [
            ambassador
            for ambassador in sample_ambassadors
            if ambassador[1].lower() not in existing_emails
        ]
        if missing_ambassadors:
            conn.executemany(
                """
                INSERT INTO users (
                    name, email, password, role, major, minor, year, personality, status,
                    ambassador_since, tours_completed, total_hours
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                missing_ambassadors,
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

    conn.commit()


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
        "personalities": VALID_PERSONALITIES,
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
            GROUP BY tours.id
            ORDER BY tours.tour_date
            """
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
        tours = [tour for tour in tours if tour["assigned_count"] > 0]
    elif normalized_tour_status == "unassigned":
        tours = [tour for tour in tours if tour["assigned_count"] == 0]

    for tour in tours:
        eligible = [dict(row) for row in conn.execute(
            "SELECT id, name, email, total_hours FROM users WHERE role = 'ambassador' ORDER BY total_hours DESC, name LIMIT 3"
        ).fetchall()]
        tour["eligible"] = eligible

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
    assigned = sum(1 for tour in tours if tour["assigned_count"] > 0)
    unassigned = sum(1 for tour in tours if tour["assigned_count"] == 0)
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
        "stats": {"total_ambassadors": len(ambassadors), "scheduled": scheduled, "assigned": assigned, "unassigned": unassigned},
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


def update_profile(conn: sqlite3.Connection, user_id: int, major: str, minor: str, year: str, personality: str):
    """Update an ambassador profile.

    Inputs:
        conn: Open SQLite connection.
        user_id: Ambassador account id.
        major: Selected major.
        minor: Selected minor.
        year: Undergraduate year.
        personality: Personality type.
    Outputs:
        Tuple of success flag and feedback message.
    """
    if not major or not year:
        return False, "Major and year are required."
    if year not in VALID_YEARS:
        return False, "Choose a valid undergraduate year."
    if personality and personality not in VALID_PERSONALITIES:
        return False, "Choose Introvert, Ambivert, or Extrovert."
    conn.execute(
        "UPDATE users SET major = ?, minor = ?, year = ?, personality = ? WHERE id = ?",
        (major, minor, year, personality, user_id),
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
    if "@" not in email or not email.endswith(".edu"):
        return False, "Ambassador emails must include a valid return address."
    if conn.execute("SELECT COUNT(*) FROM users WHERE lower(email) = lower(?)", (email,)).fetchone()[0]:
        return False, "Only one profile is allowed per ambassador email."
    conn.execute(
        "INSERT INTO users (name, email, password, role, major, minor, year, personality, status, ambassador_since, tours_completed, total_hours) VALUES (?, ?, '', 'ambassador', ?, '', ?, 'Ambivert', 'Active', ?, 0, 0)",
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


def _hard_coded_ambassador_rows() -> list[tuple]:
    """Convert hardcoded ambassador records into user-table rows.

    Inputs:
        None.
    Outputs:
        List of tuples matching the users insert schema.
    """
    rows = []
    for name, email, major, minor, year, personality in HARD_CODED_AMBASSADORS:
        rows.append(
            (
                name,
                email,
                "",
                "ambassador",
                major,
                minor,
                year,
                personality,
                "Active",
                None,
                0,
                0,
            )
        )
    return rows


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
