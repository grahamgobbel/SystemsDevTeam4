"""
Helpers for rendering the advising dashboard HTML.
"""

from html import escape
from urllib.parse import urlencode


def _option(value: str, label: str, current_value: str) -> str:
    selected = " selected" if value == current_value else ""
    return f'<option value="{value}"{selected}>{label}</option>'


def _pill_class(status: str) -> str:
    return status.replace("-", "")


def render_dashboard_page(dashboard: dict, search_term: str, status_filter: str) -> str:
    student = dashboard["student"]

    term_cards = []
    for term in dashboard["terms"]:
        if term["courses"]:
            courses = []
            for course in term["courses"]:
                courses.append(
                    f"""
                    <li class=\"course-item\">
                        <div>
                            <p class=\"course-code\">{escape(course['course_code'])}</p>
                            <h5>{escape(course['title'])}</h5>
                            <p class=\"course-meta\">{escape(course['category'])} | {course['hours']} credit hours</p>
                            <p class=\"course-note\">{escape(course['prerequisite_note'])}</p>
                        </div>
                        <span class=\"pill {_pill_class(course['course_status'])}\">{escape(course['course_status'])}</span>
                    </li>
                    """
                )
            course_markup = f"<ul class=\"course-list\">{''.join(courses)}</ul>"
        else:
            course_markup = """
            <div class=\"empty-state\">
                <p>No courses match the current search or filter.</p>
                <p class=\"small-text\">Try clearing filters to view the full recommended term.</p>
            </div>
            """

        term_cards.append(
            f"""
            <article class=\"term-card\">
                <div class=\"term-header\">
                    <div>
                        <h4>{escape(term['term_label'])}</h4>
                        <p>{escape(term['focus_note'])}</p>
                    </div>
                    <span class=\"term-hours\">{term['visible_hours'] or term['total_hours']} hrs</span>
                </div>
                {course_markup}
            </article>
            """
        )

    requirements_markup = "".join(
        f"""
        <li>
            <div class=\"requirement-row\">
                <span>{escape(item['category'])}</span>
                <span>{item['completed_hours']}/{item['total_hours']} hrs</span>
            </div>
            <div class=\"progress-track slim\">
                <span style=\"width: {item['progress']}%;\"></span>
            </div>
        </li>
        """
        for item in dashboard["requirement_summary"]
    )

    alerts_markup = "".join(f"<li>{escape(alert)}</li>" for alert in dashboard["alerts"])

    resources_markup = "".join(
        f"""
        <li>
            <div>
                <strong>{escape(resource['title'])}</strong>
                <p>{escape(resource['description'])}</p>
            </div>
            <div class=\"resource-actions\">
                <span>{escape(resource['shortcut_label'])}</span>
                <button type=\"button\">{escape(resource['action_text'])}</button>
            </div>
        </li>
        """
        for resource in dashboard["resources"]
    )

    clear_query = urlencode({})

    return f"""<!doctype html>
<html lang=\"en\">
<head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>Neeley Advising Dashboard</title>
    <link rel=\"stylesheet\" href=\"/static/styles.css\">
</head>
<body>
    <div class=\"app-shell\">
        <aside class=\"sidebar\">
            <div class=\"brand-block\">
                <div class=\"brand-mark\">NSB</div>
                <div>
                    <p class=\"eyebrow\">Neeley School of Business</p>
                    <h1>Major Progression</h1>
                </div>
            </div>

            <nav class=\"side-nav\" aria-label=\"Primary\">
                <button class=\"nav-item active\" type=\"button\">Dashboard</button>
                <button class=\"nav-item\" type=\"button\">Degree Audit</button>
                <button class=\"nav-item\" type=\"button\">Registration</button>
                <button class=\"nav-item\" type=\"button\">Help Center</button>
            </nav>

            <section class=\"help-card\">
                <h2>Quick Help</h2>
                <p>Use search to find courses or requirement areas. Filter by status to isolate completed, in-progress, or planned work.</p>
                <p class=\"small-text\">Context help is always shown in the same panel for easier navigation.</p>
            </section>
        </aside>

        <main class=\"workspace\">
            <header class=\"topbar\">
                <div>
                    <p class=\"eyebrow\">Academic Advising Tool</p>
                    <h2>{escape(student['name'])}</h2>
                    <p class=\"subtitle\">{escape(student['major'])} | {escape(student['classification'])} | Advisor: {escape(student['advisor'])}</p>
                </div>
                <div class=\"toolbar\" aria-label=\"Command menu\">
                    <button type=\"button\">File</button>
                    <button type=\"button\">Edit</button>
                    <button type=\"button\">Help</button>
                    <button type=\"button\" disabled>Submit Plan</button>
                </div>
            </header>

            <section class=\"panel filters-panel\">
                <form class=\"filters-grid\" method=\"get\">
                    <label class=\"field\">
                        <span>Search Courses</span>
                        <input type=\"search\" name=\"q\" placeholder=\"Example: INSC 30313 or analytics\" value=\"{escape(search_term)}\">
                    </label>

                    <label class=\"field\">
                        <span>Status Filter</span>
                        <select name=\"status\">
                            {_option('all', 'All statuses', status_filter)}
                            {_option('completed', 'Completed', status_filter)}
                            {_option('in-progress', 'In progress', status_filter)}
                            {_option('planned', 'Planned', status_filter)}
                        </select>
                    </label>

                    <label class=\"field checkbox-field\">
                        <span>Input Guidance</span>
                        <div class=\"checkbox-row\">
                            <input id=\"next-term\" type=\"checkbox\" checked>
                            <label for=\"next-term\">Show advisor-recommended next term first</label>
                        </div>
                    </label>

                    <div class=\"action-row\">
                        <button class=\"primary-button\" type=\"submit\">Apply Filters</button>
                        <a class=\"secondary-button\" href=\"/?{clear_query}\">Clear</a>
                    </div>
                </form>
                <p class=\"hint-text\">Displayed courses: {dashboard['result_count']}. Disabled commands stay visible so users can see what options exist.</p>
            </section>

            <section class=\"summary-grid\">
                <article class=\"panel summary-card\">
                    <p class=\"eyebrow\">Student Summary</p>
                    <div class=\"summary-lines\">
                        <p><strong>Catalog Year:</strong> {escape(student['catalog_year'])}</p>
                        <p><strong>Concentration:</strong> {escape(student['concentration'])}</p>
                        <p><strong>Email:</strong> {escape(student['email'])}</p>
                    </div>
                </article>

                <article class=\"panel summary-card\">
                    <p class=\"eyebrow\">Academic Progress</p>
                    <div class=\"metric-row\">
                        <div>
                            <h3>{student['credits_completed']}/{student['credits_required']}</h3>
                            <p>credits completed</p>
                        </div>
                        <div>
                            <h3>{student['gpa']}</h3>
                            <p>current GPA</p>
                        </div>
                    </div>
                    <div class=\"progress-track\" aria-label=\"Degree progress\">
                        <span style=\"width: {dashboard['completion_percent']}%;\"></span>
                    </div>
                    <p class=\"small-text\">{dashboard['completion_percent']}% of degree requirements completed.</p>
                </article>

                <article class=\"panel summary-card status-card\">
                    <p class=\"eyebrow\">Status Snapshot</p>
                    <div class=\"status-pills\">
                        <span class=\"pill completed\">Completed {dashboard['status_counts']['completed']}</span>
                        <span class=\"pill progress\">In Progress {dashboard['status_counts']['in-progress']}</span>
                        <span class=\"pill planned\">Planned {dashboard['status_counts']['planned']}</span>
                    </div>
                </article>
            </section>

            <section class=\"content-grid\">
                <section class=\"panel progression-panel\">
                    <div class=\"panel-heading\">
                        <div>
                            <p class=\"eyebrow\">Semester-by-Semester Plan</p>
                            <h3>Recommended major progression</h3>
                        </div>
                        <p class=\"small-text\">Each card groups related advising actions into a familiar semester workflow.</p>
                    </div>

                    <div class=\"term-grid\">{''.join(term_cards)}</div>
                </section>

                <aside class=\"right-rail\">
                    <section class=\"panel\">
                        <p class=\"eyebrow\">Requirement Checklist</p>
                        <h3>Progress by area</h3>
                        <ul class=\"requirements-list\">{requirements_markup}</ul>
                    </section>

                    <section class=\"panel\">
                        <p class=\"eyebrow\">Alerts and Feedback</p>
                        <h3>What needs attention</h3>
                        <ul class=\"alerts-list\">{alerts_markup}</ul>
                    </section>

                    <section class=\"panel\">
                        <p class=\"eyebrow\">Shortcuts and Resources</p>
                        <h3>User help</h3>
                        <ul class=\"resource-list\">{resources_markup}</ul>
                    </section>
                </aside>
            </section>
        </main>
    </div>
</body>
</html>"""