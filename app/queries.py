"""
Database queries and dashboard shaping for the advising tool.
"""

import sqlite3


def initialize_database(conn: sqlite3.Connection) -> None:
    """Create tables and seed demo data the first time the app runs."""
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            major TEXT NOT NULL,
            catalog_year TEXT NOT NULL,
            advisor TEXT NOT NULL,
            concentration TEXT NOT NULL,
            classification TEXT NOT NULL,
            email TEXT NOT NULL,
            gpa REAL NOT NULL,
            credits_completed INTEGER NOT NULL,
            credits_required INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS progression_terms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            term_label TEXT NOT NULL,
            term_order INTEGER NOT NULL,
            total_hours INTEGER NOT NULL,
            focus_note TEXT NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id)
        );

        CREATE TABLE IF NOT EXISTS planned_courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term_id INTEGER NOT NULL,
            course_code TEXT NOT NULL,
            title TEXT NOT NULL,
            hours INTEGER NOT NULL,
            course_status TEXT NOT NULL,
            category TEXT NOT NULL,
            prerequisite_note TEXT NOT NULL,
            FOREIGN KEY(term_id) REFERENCES progression_terms(id)
        );

        CREATE TABLE IF NOT EXISTS advising_resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            shortcut_label TEXT NOT NULL,
            action_text TEXT NOT NULL
        );
        """
    )
    conn.commit()

    student_count = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    if student_count:
        return

    conn.execute(
        """
        INSERT INTO students (
            name, major, catalog_year, advisor, concentration, classification,
            email, gpa, credits_completed, credits_required
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "Jordan Lee",
            "BBA in Business Information Systems",
            "2025-2026",
            "Dr. Harper Collins",
            "Business Analytics",
            "Sophomore",
            "jordan.lee@tcu.edu",
            3.54,
            54,
            120,
        ),
    )
    student_id = conn.execute("SELECT id FROM students LIMIT 1").fetchone()[0]

    terms = [
        ("Fall 2026", 1, 15, "Build analytics and accounting depth before upper-level capstone work."),
        ("Spring 2027", 2, 15, "Complete operations and finance core with one guided elective."),
        ("Fall 2027", 3, 12, "Advance toward strategic systems design and internship readiness."),
        ("Spring 2028", 4, 12, "Finish capstone, polish portfolio, and confirm graduation clearance."),
    ]
    term_ids = []
    for term in terms:
        cursor = conn.execute(
            """
            INSERT INTO progression_terms (student_id, term_label, term_order, total_hours, focus_note)
            VALUES (?, ?, ?, ?, ?)
            """,
            (student_id, *term),
        )
        term_ids.append(cursor.lastrowid)

    planned_courses = [
        (term_ids[0], "ACCT 30153", "Financial Reporting", 3, "completed", "Neeley Core", "Ready to enroll"),
        (term_ids[0], "INSC 30313", "Database Applications", 3, "in-progress", "Major Core", "Requires sophomore standing"),
        (term_ids[0], "ECON 30223", "Business Statistics II", 3, "completed", "Analytical Foundation", "Prerequisite met"),
        (term_ids[0], "BUSI 30123", "Professional Communication", 3, "planned", "Professional Skills", "Recommended before internship search"),
        (term_ids[0], "UNIV 20213", "Diversity Elective", 3, "planned", "University Core", "Advisor approved options available"),
        (term_ids[1], "FINA 30153", "Managerial Finance", 3, "planned", "Neeley Core", "Take after Accounting"),
        (term_ids[1], "MANA 40123", "Operations Strategy", 3, "planned", "Neeley Core", "Junior-level standing required"),
        (term_ids[1], "INSC 40533", "Business Intelligence", 3, "planned", "Major Core", "Database Applications recommended"),
        (term_ids[1], "MARK 30153", "Marketing Concepts", 3, "planned", "Neeley Core", "No additional prerequisite"),
        (term_ids[1], "BLAW 20213", "Legal Environment of Business", 3, "planned", "Neeley Core", "No additional prerequisite"),
        (term_ids[2], "INSC 40970", "Internship Practicum", 3, "planned", "Experiential Learning", "Requires advisor approval"),
        (term_ids[2], "INSC 40963", "Systems Analysis", 3, "planned", "Major Core", "Business Intelligence recommended"),
        (term_ids[2], "MANA 30313", "Business Ethics", 3, "planned", "Professional Skills", "Junior-level standing required"),
        (term_ids[2], "Elective", "Neeley Major Elective", 3, "planned", "Elective", "Choose from approved analytics list"),
        (term_ids[3], "INSC 40983", "Capstone in Business Systems", 3, "planned", "Capstone", "Final-semester course"),
        (term_ids[3], "Elective", "Advanced Business Analytics Elective", 3, "planned", "Elective", "Select with advisor"),
        (term_ids[3], "MANA 40950", "Strategic Management", 3, "planned", "Capstone", "Senior standing required"),
        (term_ids[3], "GEN ED", "Upper-Level Core Requirement", 3, "planned", "University Core", "Verify final core audit"),
    ]
    conn.executemany(
        """
        INSERT INTO planned_courses (
            term_id, course_code, title, hours, course_status, category, prerequisite_note
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        planned_courses,
    )

    resources = [
        ("Advising Notes", "Open the latest advisor summary and semester planning notes.", "Alt + N", "Open notes"),
        ("Registration Help", "Review holds, time tickets, and registration troubleshooting guidance.", "F1", "View help"),
        ("Degree Audit", "See completed hours, unmet requirements, and catalog-year rules.", "Ctrl + D", "Launch audit"),
    ]
    conn.executemany(
        """
        INSERT INTO advising_resources (title, description, shortcut_label, action_text)
        VALUES (?, ?, ?, ?)
        """,
        resources,
    )
    conn.commit()


def get_dashboard_payload(
    conn: sqlite3.Connection,
    search_term: str = "",
    status_filter: str = "all",
) -> dict:
    """Return all data needed to render the dashboard."""
    student = dict(conn.execute("SELECT * FROM students LIMIT 1").fetchone())
    terms = conn.execute(
        """
        SELECT id, term_label, term_order, total_hours, focus_note
        FROM progression_terms
        ORDER BY term_order
        """
    ).fetchall()
    all_courses = conn.execute(
        """
        SELECT
            planned_courses.id,
            planned_courses.term_id,
            planned_courses.course_code,
            planned_courses.title,
            planned_courses.hours,
            planned_courses.course_status,
            planned_courses.category,
            planned_courses.prerequisite_note
        FROM planned_courses
        ORDER BY term_id, id
        """
    ).fetchall()
    resources = [
        dict(row)
        for row in conn.execute(
            "SELECT title, description, shortcut_label, action_text FROM advising_resources ORDER BY id"
        ).fetchall()
    ]

    normalized_search = search_term.lower()
    filtered_courses = []
    for row in all_courses:
        course = dict(row)
        matches_search = not normalized_search or normalized_search in (
            f"{course['course_code']} {course['title']} {course['category']}".lower()
        )
        matches_status = status_filter == "all" or course["course_status"] == status_filter
        if matches_search and matches_status:
            filtered_courses.append(course)

    courses_by_term = {}
    for course in filtered_courses:
        courses_by_term.setdefault(course["term_id"], []).append(course)

    visible_terms = []
    for term_row in terms:
        term = dict(term_row)
        term_courses = courses_by_term.get(term["id"], [])
        term["courses"] = term_courses
        term["visible_hours"] = sum(course["hours"] for course in term_courses)
        term["course_count"] = len(term_courses)
        visible_terms.append(term)

    status_counts = {"completed": 0, "in-progress": 0, "planned": 0}
    category_totals = {}
    for row in all_courses:
        course = dict(row)
        status_counts[course["course_status"]] = status_counts.get(course["course_status"], 0) + 1
        category_totals.setdefault(course["category"], {"total": 0, "done": 0})
        category_totals[course["category"]]["total"] += course["hours"]
        if course["course_status"] == "completed":
            category_totals[course["category"]]["done"] += course["hours"]

    requirement_summary = []
    for category, totals in sorted(category_totals.items()):
        progress = round((totals["done"] / totals["total"]) * 100) if totals["total"] else 0
        requirement_summary.append(
            {
                "category": category,
                "completed_hours": totals["done"],
                "total_hours": totals["total"],
                "progress": progress,
            }
        )

    completion_percent = round(
        (student["credits_completed"] / student["credits_required"]) * 100
    )
    alerts = [
        "Advisor hold review recommended before Fall 2026 registration opens.",
        "Capstone and Strategic Management should remain in the final academic year.",
        "Search results update the plan instantly so students can isolate one requirement area.",
    ]

    return {
        "student": student,
        "terms": visible_terms,
        "status_counts": status_counts,
        "requirement_summary": requirement_summary,
        "resources": resources,
        "completion_percent": completion_percent,
        "alerts": alerts,
        "result_count": len(filtered_courses),
    }