"""
Application Title: TCU Ambassador Scheduling System
Date: 2026-04-20
Authors: Graham Gobbel
Purpose: Render application pages and reusable HTML fragments for the
scheduling interface.
"""

from datetime import datetime, timedelta
from html import escape
from urllib.parse import quote_plus


def validation_message(message: str) -> str:
    """Encode a feedback message for use in a query string.

    Inputs:
        message: Human-readable status text.
    Outputs:
        URL-encoded string safe for redirects.
    """
    return quote_plus(message)


def redirect_response(handler, location: str, headers: dict | None = None) -> None:
    """Send a redirect response.

    Inputs:
        handler: HTTP request handler.
        location: Redirect target URL.
    Outputs:
        HTTP 303 response written to the client.
    """
    handler.send_response(303)
    handler.send_header("Location", location)
    if headers:
        for key, value in headers.items():
            handler.send_header(key, value)
    handler.end_headers()


def send_html(handler, body: str) -> None:
    """Send an HTML response body.

    Inputs:
        handler: HTTP request handler.
        body: HTML content to send.
    Outputs:
        UTF-8 encoded HTML response.
    """
    content = body.encode("utf-8")
    handler.send_response(200)
    handler.send_header("Content-Type", "text/html; charset=utf-8")
    handler.send_header("Content-Length", str(len(content)))
    handler.end_headers()
    handler.wfile.write(content)


def render_page(page: str, context: dict) -> str:
    """Render the requested application page.

    Inputs:
        page: Logical page name.
        context: Data dictionary for the page.
    Outputs:
        Full HTML page as a string.
    """
    # Lightweight page dispatcher used by request handlers.
    if page == "login":
        return _render_login(context)
    if page == "register":
        return _render_register(context)
    if page == "ambassador_dashboard":
        return _render_ambassador_dashboard(context)
    if page == "availability":
        return _render_availability(context)
    if page == "profile":
        return _render_profile(context)
    if page == "admin":
        return _render_admin(context)
    return "<h1>Unknown page</h1>"


def _render_login(context: dict) -> str:
    """Render the login page.

    Inputs:
        context: Login page state including message and error text.
    Outputs:
        HTML for the login screen.
    """
    # Flash messages are pre-escaped by helper functions.
    error = _flash(context.get("error", ""), "error")
    message = _flash(context.get("message", ""), "success")
    return f"""<!doctype html>
<html lang=\"en\">
<head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>TCU Ambassador Scheduling</title>
    <link rel=\"stylesheet\" href=\"/static/styles.css\">
</head>
<body class=\"login-body\">
    <div class=\"login-card\">
        <div class=\"logo-badge\">TCU</div>
        <h1>Ambassador Scheduling</h1>
        <p class=\"hero-copy\">Sign in with your TCU email and password</p>
        {message}
        {error}
        <form method=\"post\" action=\"/login\" class=\"login-form\">
            <label>Email <span class=\"required\">*</span></label>
            <input type=\"email\" name=\"email\" placeholder=\"john.doe@tcu.edu\" required>

            <label>Password <span class=\"required\">*</span></label>
            <input type=\"password\" name=\"password\" placeholder=\"Enter password\" required>

            <button class=\"primary large\" type=\"submit\">Login</button>
        </form>
        <a href="/register" class="create-account-link">Create Account</a>
        <p class=\"field-help\">Use your assigned account credentials to continue.</p>
    </div>
</body>
</html>"""


def _render_register(context: dict) -> str:
    """Render the create-account page.

    Inputs:
        context: Registration page state including message and error text.
    Outputs:
        HTML for the registration screen.
    """
    error = _flash(context.get("error", ""), "error")
    message = _flash(context.get("message", ""), "success")
    return f"""<!doctype html>
<html lang=\"en\">
<head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>Create Account | TCU Ambassador Scheduling</title>
    <link rel=\"stylesheet\" href=\"/static/styles.css\">
</head>
<body class=\"login-body\">
    <div class=\"login-card\">
        <div class=\"logo-badge\">TCU</div>
        <h1>Create Account</h1>
        <p class=\"hero-copy\">Set up your account using your school email.</p>
        {message}
        {error}
        <form method=\"post\" action=\"/register\" class=\"login-form\">
            <label>Full Name <span class=\"required\">*</span></label>
            <input type=\"text\" name=\"name\" placeholder=\"Jane Doe\" required>

            <label>Email <span class=\"required\">*</span></label>
            <input type=\"email\" name=\"email\" placeholder=\"jane.doe@tcu.edu\" required>

            <label>Account Role <span class=\"required\">*</span></label>
            <label class=\"radio-card\"><input type=\"radio\" name=\"role\" value=\"ambassador\" required> <span>Ambassador</span></label>
            <label class=\"radio-card\"><input type=\"radio\" name=\"role\" value=\"admin\" required> <span>Admin</span></label>

            <label>Password <span class=\"required\">*</span></label>
            <input type=\"password\" name=\"password\" placeholder=\"At least 8 characters\" required>

            <label>Confirm Password <span class=\"required\">*</span></label>
            <input type=\"password\" name=\"confirm_password\" placeholder=\"Re-enter password\" required>

            <button class=\"primary large\" type=\"submit\">Create Account</button>
        </form>
        <p class=\"field-help\"><a href=\"/\">Back to Login</a></p>
    </div>
</body>
</html>"""


def _render_ambassador_dashboard(context: dict) -> str:
    """Render the ambassador dashboard.

    Inputs:
        context: Dashboard data from the query layer.
    Outputs:
        HTML for the ambassador dashboard.
    """
    user = context["user"]
    assignments = "".join(_assignment_card(item)
                          for item in context["assignments"])
    notifications = "".join(_notification_card(item)
                            for item in context["notifications"])
    stats = context["stats"]
    content = f"""
    <section class=\"content-main\">
        <div class=\"page-header\">
            <div>
                <h1>Welcome, {escape(user['name'])}!</h1>
                <p>Here's your schedule overview and latest updates</p>
            </div>
                <a class=\"green-button\" href=\"/ambassador/availability?view=weekly\">Submit Availability</a>
        </div>

        <div class=\"two-column\">
            <div>
                <div class=\"section-title-row\">
                    <h2>Upcoming Assignments</h2>
                    <span class=\"ghost-chip\">View All</span>
                </div>
                <div class=\"stack\">{assignments}</div>
            </div>
            <aside class=\"right-column\">
                <h2>Notifications</h2>
                <div class=\"stack\">{notifications}</div>
                <div class=\"month-card\">
                    <h3>This Month</h3>
                    <div><span>Total Tours</span><strong>{stats['total_tours']}</strong></div>
                    <div><span>Hours Completed</span><strong>{stats['hours_completed']}</strong></div>
                    <div><span>Upcoming Events</span><strong>{stats['upcoming_events']}</strong></div>
                </div>
            </aside>
        </div>
    </section>
    """
    return _shell(user, "home", content, role="ambassador")


def _render_availability(context: dict) -> str:
    """Render the ambassador availability page.

    Inputs:
        context: Availability page data from the query layer.
    Outputs:
        HTML for the availability page.
    """
    user = context["user"]
    view = context["view"]
    tabs = _render_view_tabs(view)
    main_panel = _availability_grid(
        context) if view == "dashboard" else _availability_form(context)
    body = f"""
    <section class=\"content-main\">
        <div class=\"page-header compact\">
            <div>
                <h1>Submit Availability</h1>
                <p>Set up your weekly schedule with preference rankings</p>
            </div>
        </div>
        {_render_flash_messages(context)}
        <div class=\"info-panel\">
            <strong>How it Works</strong>
            <p><b>Weekly Availability:</b> Set your regular weekly schedule that repeats each week.</p>
            <p><b>Preference Rankings:</b> Rank your eagerness to work each time slot (1st, 2nd, 3rd priority, or Low priority).</p>
            <p><b>Dashboard View:</b> See your complete availability schedule at a glance.</p>
        </div>
        {tabs}
        {main_panel}
    </section>
    """
    return _shell(user, "availability", body, role="ambassador")


def _render_profile(context: dict) -> str:
    """Render the ambassador profile page.

    Inputs:
        context: Profile page data from the query layer.
    Outputs:
        HTML for the profile page.
    """
    user = context["user"]
    major_picker = _major_picker(context["major_groups"])
    minor_picker = _minor_picker(context["minors"])
    body = f"""
    <section class=\"content-main\">
        <div class=\"page-header compact\">
            <div>
                <h1>Ambassador Profile</h1>
                <p>Update your information to help us match you with the right tours and events</p>
            </div>
        </div>
        {_render_flash_messages(context)}
        <div class=\"profile-grid\">
            <div class=\"profile-card\">
                <h3>{escape(user['name'])}</h3>
                <p>{escape(user['email'])}</p>
                <div class=\"profile-stats\">
                    <div><span>Tours Completed</span><strong>{context['tours_completed']}</strong></div>
                </div>
            </div>
            <form class=\"settings-card\" method=\"post\" action=\"/ambassador/profile\">
                <input type=\"hidden\" name=\"user\" value=\"{user['id']}\">
                <h3>Academic Information</h3>
                <p>Fields marked with <span class=\"required\">*</span> are required</p>
                <label>Major <span class=\"required\">*</span></label>
                {major_picker}
                <label>Minor (Optional)</label>
                {minor_picker}
                <label>Year <span class=\"required\">*</span></label>
                <select name=\"year\">{_options(context["years"], "", allow_blank_label="Select a year")}</select>
                <label>TCU Involvement Level</label>
                <select name=\"involvement_level\">{_options(context["involvement_levels"], "")}</select>
                <div class=\"form-actions right\"><button class=\"primary\" type=\"submit\">Save Changes</button></div>
            </form>
        </div>
    </section>
    """
    return _shell(user, "profile", body, role="ambassador")


def _render_report_rows(rows: list[dict]) -> str:
    """Render report table body rows.

    Inputs:
        rows: Report row records.
    Outputs:
        HTML table rows with ambassador data.
    """
    row_html = "".join([
        f'<tr><td>{escape(row["name"])}</td><td>{escape(row["email"])}</td><td>{escape(row.get("major") or "-")}</td><td>{escape(row.get("year") or "-")}</td><td>{row["assigned_tours"]}</td><td>{row["total_hours"]}</td></tr>'
        for row in rows
    ])
    return row_html or '<tr><td colspan="6">No ambassadors matched the selected filters.</td></tr>'


def _render_admin(context: dict) -> str:
    """Render the admin dashboard.

    Inputs:
        context: Admin dashboard data from the query layer.
    Outputs:
        HTML for the admin dashboard.
    """
    user = context["user"]
    stat = context["stats"]
    report = context["report"]
    tours_markup = "".join(_tour_card(
        item, user['id']) for item in context["tours"])
    weekly_schedule = context["weekly_schedule"]
    report_rows = _render_report_rows(report["rows"])
    body = f"""
    <section class=\"content-main\">
        <div class=\"page-header compact\">
            <div>
                <h1>Admin Dashboard</h1>
                <p>Manage daily tours and ambassador assignments</p>
            </div>
        </div>
        {_render_flash_messages(context)}
        <div class="metric-grid compact-metrics">
            {_metric_card('Total Ambassadors',
                          stat['total_ambassadors'], 'purple')}
            {_metric_card('Scheduled Tours', stat['scheduled'], 'blue')}
            {_metric_card('Assigned Tours', stat['assigned'], 'green')}
            {_metric_card('Tours In Progress', stat['in_progress'], 'blue')}
            {_metric_card('Unassigned Tours', stat['unassigned'], 'gold')}
        </div>
        <div class=\"info-panel\"><strong>Tour Management</strong><p>Daily tours are pre-scheduled for Monday through Friday at 10:00 AM and 2:00 PM. For each tour, add ambassadors from the available list until the tour is full.</p></div>
        <div class=\"admin-section\">
            <div class=\"section-head\">
                <div><h3>Pre-Scheduled Tours</h3><p>Available ambassadors appear by priority for each tour slot</p></div>
            </div>
            <div class=\"stack tour-stack\">{tours_markup}</div>
        </div>
        <div class=\"admin-section\">
            <div class=\"section-head\">
                <div><h3>Weekly Tour Schedule</h3><p>Assigned names appear below once scheduled</p></div>
            </div>
            {_weekly_schedule_table(weekly_schedule)}
        </div>
        <div class=\"admin-section\">
            <div class=\"section-head\">
                <div><h3>Ambassador Workload Report</h3><p>Generated on {escape(report['generated_on'])} from current records</p></div>
            </div>
            <div class=\"report-table-wrap\">
                <table class=\"report-table\">
                    <thead>
                        <tr><th>Name</th><th>Email</th><th>Major</th><th>Year</th><th>Assigned Tours</th><th>Total Hours</th></tr>
                    </thead>
                    <tbody>{report_rows}</tbody>
                </table>
            </div>
        </div>
    </section>
    """
    return _shell(user, "admin", body, role="admin")


def _weekly_schedule_table(schedule: dict) -> str:
    """Render the fixed weekly tour schedule tables.

    Inputs:
        schedule: Schedule payload from the query layer.
    Outputs:
        HTML for morning and afternoon schedule tables.
    """
    days = schedule["days"]
    morning = _schedule_block(schedule, "morning", "10 AM", days)
    afternoon = _schedule_block(schedule, "afternoon", "2 PM", days)
    return f"""
    <div class="report-table-wrap">
        <h4>Weekly Tour Schedule</h4>
        {morning}
        <br>
        {afternoon}
    </div>
    """


def _schedule_block(schedule: dict, key: str, label: str, days: list[str]) -> str:
    """Render one schedule block (10 AM or 2 PM).

    Inputs:
        schedule: Schedule payload from the query layer.
        key: Block key in schedule payload.
        label: Display time label.
        days: Ordered weekday labels.
    Outputs:
        HTML table block.
    """
    headers = "".join([f"<th>{escape(day)} - {label}</th>" for day in days])
    columns = "".join(_build_schedule_column(schedule, key, day)
                      for day in days)
    return f"""
    <table class="report-table">
        <thead><tr>{headers}</tr></thead>
        <tbody><tr>{columns}</tr></tbody>
    </table>
    """


def _build_schedule_column(schedule: dict, key: str, day: str) -> str:
    """Build a single schedule table column.

    Inputs:
        schedule: Schedule payload from the query layer.
        key: Block key in schedule payload.
        day: Day label.
    Outputs:
        HTML table column with ambassador names.
    """
    names = schedule[key][day]["names"]
    entries = "".join(
        f"<div>{idx}. {escape(name)}</div>" for idx, name in enumerate(names, start=1))
    return f"<td>{entries}</td>"


def _shell(user: dict, active: str, content: str, role: str) -> str:
    """Wrap page content in the shared application shell.

    Inputs:
        user: Current user record.
        active: Active navigation key.
        content: Main page HTML.
        role: User role string.
    Outputs:
        Complete HTML document.
    """
    nav = _top_nav(user, active, role)
    side = _side_nav(user, active, role)
    return f"""<!doctype html>
<html lang=\"en\">
<head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>TCU Ambassador Scheduling</title>
    <link rel=\"stylesheet\" href=\"/static/styles.css\">
</head>
<body>
    <header class=\"top-nav\">{nav}</header>
    <div class=\"app-frame\">
        <aside class=\"left-rail\">{side}</aside>
        <main class=\"page-shell\">{content}</main>
    </div>
    <script>
        document.addEventListener('click', function (event) {{
            const dropdown = event.target.closest('[data-dropdown]');

            document.querySelectorAll('[data-dropdown]').forEach(function (item) {{
                if (item !== dropdown) {{
                    item.dataset.open = 'false';
                    const trigger = item.querySelector('[data-dropdown-trigger]');
                    if (trigger) {{
                        trigger.setAttribute('aria-expanded', 'false');
                    }}
                }}
            }});

            if (!dropdown) {{
                return;
            }}

            const trigger = event.target.closest('[data-dropdown-trigger]');
            if (trigger) {{
                const isOpen = dropdown.dataset.open === 'true';
                dropdown.dataset.open = isOpen ? 'false' : 'true';
                trigger.setAttribute('aria-expanded', String(!isOpen));
                event.preventDefault();
                return;
            }}

            const option = event.target.closest('[data-dropdown-option]');
            if (!option) {{
                return;
            }}

            const value = option.dataset.value || '';
            const hiddenInput = dropdown.querySelector('input[type="hidden"]');
            const label = dropdown.querySelector('[data-dropdown-label]');
            const dropdownTrigger = dropdown.querySelector('[data-dropdown-trigger]');
            if (hiddenInput) {{
                hiddenInput.value = value;
            }}
            if (label) {{
                label.textContent = value || option.textContent || '';
            }}
            if (dropdownTrigger) {{
                dropdownTrigger.setAttribute('aria-expanded', 'false');
            }}
            dropdown.dataset.open = 'false';
            event.preventDefault();
        }});
    </script>
</body>
</html>"""


def _top_nav(user: dict, active: str, role: str) -> str:
    """Build the top navigation bar.

    Inputs:
        user: Current user record.
        active: Active navigation key.
        role: User role string.
    Outputs:
        HTML for the top navigation.
    """
    if role == "admin":
        center = f'<a class="top-link {"active" if active == "admin" else ""}" href="/admin">Admin Dashboard</a>'
    else:
        center = "".join([
            f'<a class="top-link {"active" if active == "home" else ""}" href="/ambassador/dashboard">Home</a>',
            f'<a class="top-link {"active" if active == "availability" else ""}" href="/ambassador/availability?view=dashboard">Availability</a>',
            f'<a class="top-link {"active" if active == "profile" else ""}" href="/ambassador/profile">Profile</a>'
        ])
    return f'<div class="top-left"><div class="frog-mark">TCU</div>{center}</div><div class="top-right"><a class="logout-link" href="/logout">Logout</a></div>'


def _side_nav(user: dict, active: str, role: str) -> str:
    """Build the side navigation links.

    Inputs:
        user: Current user record.
        active: Active navigation key.
        role: User role string.
    Outputs:
        HTML for the side navigation.
    """
    if role == "admin":
        items = [("Admin Dashboard", "/admin", active == "admin")]
    else:
        items = [
            ("Dashboard", "/ambassador/dashboard", active == "home"),
            ("Submit Availability", "/ambassador/availability?view=weekly",
             active == "availability"),
            ("Profile Settings", "/ambassador/profile", active == "profile"),
        ]
    links = "".join(_render_nav_link(label, href, is_active)
                    for label, href, is_active in items)
    return f'<p class="quick-title">Quick Actions</p>{links}'


def _render_nav_link(label: str, href: str, is_active: bool) -> str:
    """Render a single navigation link.

    Inputs:
        label: Link text.
        href: Link URL.
        is_active: Whether the link is currently active.
    Outputs:
        HTML for one navigation link.
    """
    active_class = "active" if is_active else ""
    return f'<a class="quick-link {active_class}" href="{href}">{label}</a>'


def _pretty_date(date_text: str) -> str:
    """Format a YYYY-MM-DD date for display.

    Inputs:
        date_text: ISO-style date string.
    Outputs:
        Human-readable date string, or the original text if parsing fails.
    """
    try:
        return datetime.strptime(date_text, "%Y-%m-%d").strftime("%b %d, %Y")
    except ValueError:
        return date_text


def _weekday_name(date_text: str) -> str:
    """Format a YYYY-MM-DD date as its weekday name.

    Inputs:
        date_text: ISO-style date string.
    Outputs:
        Weekday label, or the original text if parsing fails.
    """
    try:
        return datetime.strptime(date_text, "%Y-%m-%d").strftime("%A")
    except ValueError:
        return date_text


def _assignment_card(item: dict) -> str:
    """Render one assignment card.

    Inputs:
        item: Assignment record.
    Outputs:
        HTML for the assignment card.
    """
    status_class = "confirmed" if item["status"] == "confirmed" else "pending"
    time_label = _tour_time_label(item["start_time"])
    return f"""
    <article class=\"assignment-card\">
        <div class=\"assignment-head\"><h3>{escape(item['tour_type'])}</h3><span class=\"status-chip {status_class}\">{escape(item['status'])}</span></div>
        <p class=\"muted\">{escape(item['location'])}</p>
        <div class=\"assignment-meta\"><span>{_pretty_date(item['tour_date'])}</span><span>{escape(time_label)}</span></div>
    </article>
    """


def _notification_card(item: dict) -> str:
    """Render one notification card.

    Inputs:
        item: Notification record.
    Outputs:
        HTML for the notification card.
    """
    return f'<article class="notice-card {escape(item["kind"])}"><strong>{escape(item["title"])}</strong><p>{escape(item["detail"])}</p><span>{escape(item["age_label"])}</span></article>'


def _availability_grid(context: dict) -> str:
    """Render the availability dashboard grid.

    Inputs:
        context: Availability page data.
    Outputs:
        HTML for the grid view.
    """
    slots = context["slots"]
    grid_cells = []
    for time_label in context["time_labels"]:
        grid_cells.append(f'<div class="time-col">{time_label}</div>')
        for day in context["days"]:
            slot = _slot_for_day_and_time(slots, day, time_label)
            label = escape(slot["priority"]) if slot else ""
            cls = _priority_class(slot["priority"]) if slot else "not-set"
            grid_cells.append(
                f'<div class="calendar-cell {cls}">{label}</div>')
    headings = "".join([f'<div class="day-head"><strong>{day[:3]}</strong><span>{num}</span></div>' for day, num in zip(
        context["days"], ["4/6", "4/7", "4/8", "4/9", "4/10", "4/11", "4/12"])])
    footer = "" if slots else '<div class="empty-footer"><div class="calendar-icon">¦</div><p>No availability set yet</p><span>Use the Weekly Availability tab to set your schedule</span></div>'
    return f"""
    <section class=\"dashboard-panel\">
        <div class=\"panel-header\"><div><h3>Availability Dashboard</h3><p>Visual overview of your availability across weeks</p></div><div class=\"calendar-controls\"><span class=\"ghost-chip\">Today</span></div></div>
        <h2 class=\"center-title\">{escape(context['week_label'])}</h2>
        <div class=\"legend\">
            <span class=\"legend-item first\">1st Priority</span>
            <span class=\"legend-item second\">2nd Priority</span>
            <span class=\"legend-item third\">3rd Priority</span>
            <span class=\"legend-item low\">Low Priority</span>
            <span class=\"legend-item unset\">Not Set</span>
        </div>
        <div class=\"calendar-grid\"><div class=\"time-head\">Time</div>{headings}{''.join(grid_cells)}</div>
        {footer}
    </section>
    """


def _availability_form(context: dict) -> str:
    """Render the weekly availability form.

    Inputs:
        context: Availability page data.
    Outputs:
        HTML for the form view.
    """
    user = context["user"]
    rows = "".join([
        f'<div class="slot-row"><span>{escape(item["day"])}</span><span>{escape(item["start_time"])} - {escape(item["end_time"])}</span><span>{escape(item["priority"])}</span></div>'
        for item in context["slots"]
    ]) or '<div class="empty-state-large"><div class="calendar-icon">?</div><p>No weekly slots added yet</p><span>Click "Add Weekly Slot" to set up your recurring availability</span></div>'
    day_opts = _options(context["days"], "")
    pri_opts = _options(context["priorities"], "")
    time_opts = _options(context["time_labels"], "")
    return f"""
    <section class=\"dashboard-panel\">
        <div class=\"section-head\">
            <div><h3>Set Weekly Schedule</h3><p>Define your regular availability that repeats every week</p></div>
        </div>
        <form class=\"slot-form availability-form\" method=\"post\" action=\"/ambassador/availability\">
                <input type=\"hidden\" name=\"user\" value=\"{user['id']}\">
                <input type=\"hidden\" name=\"action\" value=\"add_slot\">
                <div class=\"slot-field\">
                    <label for=\"avail-day\">Day</label>
                    <select id=\"avail-day\" name=\"day\">{day_opts}</select>
                </div>
                <div class=\"slot-field\">
                    <label for=\"avail-start\">Start Time</label>
                    <select id=\"avail-start\" name=\"start_time\">{time_opts}</select>
                </div>
                <div class=\"slot-field\">
                    <label for=\"avail-end\">End Time</label>
                    <select id=\"avail-end\" name=\"end_time\">{time_opts}</select>
                </div>
                <div class=\"slot-field\">
                    <label for=\"avail-priority\">Priority</label>
                    <select id=\"avail-priority\" name=\"priority\">{pri_opts}</select>
                </div>
                <button class=\"primary\" type=\"submit\">Add Weekly Slot</button>
        </form>
        <div class=\"draft-box\">{rows}</div>
        <form method=\"post\" action=\"/ambassador/availability\" class=\"footer-actions\">
            <input type=\"hidden\" name=\"user\" value=\"{user['id']}\">
                <button class=\"secondary\" type=\"submit\" name=\"action\" value=\"clear_all\">Clear All</button>
                <button class=\"green-button\" type=\"submit\" name=\"action\" value=\"submit_availability\">Submit Availability</button>
        </form>
    </section>
    """


def _tour_card(tour: dict, admin_user_id: int) -> str:
    """Render one tour management card.

    Inputs:
        tour: Tour record.
        admin_user_id: Admin user id.
    Outputs:
        HTML for the tour card.
    """
    assign_forms = "".join([
        f'''<form method="post" action="/admin" class="candidate-card {_priority_class(candidate['priority'])}"><input type="hidden" name="user" value="{admin_user_id}"><input type="hidden" name="action" value="assign_tour"><input type="hidden" name="tour_id" value="{tour['id']}"><input type="hidden" name="ambassador_id" value="{candidate['id']}"><div><strong>{escape(candidate['name'])}</strong><p>{escape(candidate['email'])}</p><span class="priority-chip {_priority_class(candidate['priority'])}">{escape(candidate['priority'])}</span></div><button class="secondary small" type="submit">Add</button></form>'''
        for candidate in tour["eligible"]
    ])
    assigned_names = "".join(
        [f'<li>{escape(name)}</li>' for name in tour.get("assigned_names", [])]
    ) or "<li>No one assigned yet.</li>"
    status = "published" if tour["published"] else "draft"
    day_label = _weekday_name(tour["tour_date"])
    time_label = _tour_time_label(tour["start_time"])
    remaining = tour.get("remaining_slots", 0)
    capacity_note = f"Assigned {tour['assigned_count']} of {tour['ambassadors_needed']} ambassadors"
    if remaining == 0:
        capacity_note += " (Full)"
    available_markup = assign_forms if remaining > 0 and assign_forms else "<p class=\"muted\">No additional available ambassadors for this slot.</p>"
    return f"""
    <article class=\"tour-card\">
        <div class=\"tour-card-head\"><div><h4>{escape(tour['tour_type'])}</h4><p>{escape(day_label)} | {escape(time_label)} | {escape(tour['location'])}</p></div><span class=\"status-chip {status}\">{status}</span></div>
        <p class=\"muted\">{capacity_note}</p>
        <div class=\"tour-card-columns\">
            <div>
                <h5>Assigned</h5>
                <ol class=\"assigned-list\">{assigned_names}</ol>
            </div>
            <div>
                <h5>Available Ambassadors</h5>
                <div class=\"candidate-stack\">{available_markup}</div>
            </div>
        </div>
    </article>
    """


def _ambassador_row(item: dict, admin_user_id: int) -> str:
    """Render one ambassador management row.

    Inputs:
        item: Ambassador record.
        admin_user_id: Admin user id.
    Outputs:
        HTML for the ambassador row.
    """
    initial = escape(item['name'][0].upper()) if item['name'] else 'A'
    return f"""
    <article class=\"ambassador-row\">
        <div class=\"avatar-small\">{initial}</div>
        <div class=\"ambassador-copy\"><strong>{escape(item['name'])}</strong><p>{escape(item['email'])}</p></div>
        <span class=\"hour-chip\">{item['total_hours']} hrs</span>
        <form method=\"post\" action=\"/admin\">
            <input type=\"hidden\" name=\"user\" value=\"{admin_user_id}\">
            <input type=\"hidden\" name=\"action\" value=\"delete_ambassador\">
            <input type=\"hidden\" name=\"ambassador_id\" value=\"{item['id']}\">
            <button class=\"icon-button\" type=\"submit\">Delete</button>
        </form>
    </article>
    """


def _metric_card(label: str, value: int, tone: str) -> str:
    """Render a summary metric card.

    Inputs:
        label: Metric label.
        value: Metric value.
        tone: Visual style key.
    Outputs:
        HTML for the metric card.
    """
    return f'<div class="metric-card {tone}"><span>{label}</span><strong>{value}</strong></div>'


def _flash(message: str, tone: str) -> str:
    """Render a flash message if one is present.

    Inputs:
        message: Message text.
        tone: Visual style key.
    Outputs:
        HTML for the flash message, or an empty string.
    """
    if not message:
        return ""
    return f'<div class="flash {tone}">{escape(message)}</div>'


def _options(options: list[str], current: str, allow_blank_label: str = "Select") -> str:
    """Build a list of HTML option elements.

    Inputs:
        options: Available option values.
        current: Currently selected value.
        allow_blank_label: Label for the blank option, if allowed.
    Outputs:
        Concatenated option HTML.
    """
    html = []
    if allow_blank_label is not None:
        selected = " selected" if not current else ""
        html.append(f'<option value=""{selected}>{allow_blank_label}</option>')
    for option in options:
        selected = " selected" if option == current else ""
        html.append(
            f'<option value="{escape(option)}"{selected}>{escape(option or allow_blank_label)}</option>')
    return "".join(html)


def _major_picker(groups: list[tuple[str, list[str]]]) -> str:
    """Render the major picker dropdown.

    Inputs:
        groups: Major group labels and options.
    Outputs:
        HTML for the major picker.
    """
    items = []
    for group_label, options in groups:
        option_buttons = "".join(
            f'<button type="button" class="dropdown-option" data-dropdown-option data-value="{escape(option)}">{escape(option)}</button>'
            for option in options
        )
        items.append(
            f'''
            <div class="dropdown-group">
                <div class="dropdown-group-label">{escape(group_label)}</div>
                <div class="dropdown-group-options">{option_buttons}</div>
            </div>
            '''
        )
    return _dropdown_shell("major", "Select a major", "major", "Select a major", "".join(items))


def _minor_picker(options: list[str]) -> str:
    """Render the minor picker dropdown.

    Inputs:
        options: Minor option values.
    Outputs:
        HTML for the minor picker.
    """
    option_buttons = "".join(
        f'<button type="button" class="dropdown-option" data-dropdown-option data-value="{escape(option)}">{escape(option)}</button>'
        for option in options
    )
    return _dropdown_shell("minor", "Select your minor", "minor", "Select your minor", option_buttons)


def _dropdown_shell(name: str, placeholder: str, input_name: str, button_label: str, menu_html: str) -> str:
    """Render the shared dropdown wrapper.

    Inputs:
        name: Dropdown name key.
        placeholder: Placeholder text.
        input_name: Hidden input name.
        button_label: Button label text.
        menu_html: Inner menu HTML.
    Outputs:
        HTML for the dropdown wrapper.
    """
    return f'''
    <div class="dropdown-field" data-dropdown>
        <input type="hidden" name="{input_name}" value="">
        <button class="dropdown-trigger" type="button" data-dropdown-trigger aria-expanded="false">
            <span data-dropdown-label>{escape(button_label)}</span>
            <span class="dropdown-caret">▾</span>
        </button>
        <div class="dropdown-menu" role="listbox" aria-label="{escape(placeholder)}">
            <button type="button" class="dropdown-option placeholder" data-dropdown-option data-value="">{escape(placeholder)}</button>
            {menu_html}
        </div>
    </div>
    '''


def _slot_for_day_and_time(slots: list[dict], day: str, time_label: str):
    """Find the availability slot that overlaps one day/time cell.

    Inputs:
        slots: Availability slot records.
        day: Day label.
        time_label: Hour label.
    Outputs:
        Matching slot dictionary or None.
    """
    hour_start = datetime.strptime(time_label, "%I:%M %p")
    hour_end = hour_start + timedelta(hours=1)
    matching_slots = [slot for slot in slots if slot["day"] ==
                      day and _slot_overlaps_hour(slot, hour_start, hour_end)]
    if not matching_slots:
        return None
    return min(matching_slots, key=_priority_rank)


def _tour_time_label(start_time: str) -> str:
    """Convert a stored start time into a compact slot label.

    Inputs:
        start_time: Stored time text such as "10:00 AM".
    Outputs:
        Compact label like "10am" or "2pm".
    """
    try:
        return datetime.strptime(start_time, "%I:%M %p").strftime("%I%p").lstrip("0").lower()
    except ValueError:
        return start_time


def _slot_overlaps_hour(slot: dict, hour_start: datetime, hour_end: datetime) -> bool:
    """Check whether a slot overlaps a one-hour interval.

    Inputs:
        slot: Availability slot record.
        hour_start: Start of the hour interval.
        hour_end: End of the hour interval.
    Outputs:
        True when the slot overlaps the interval.
    """
    slot_start = datetime.strptime(slot["start_time"], "%I:%M %p")
    slot_end = datetime.strptime(slot["end_time"], "%I:%M %p")
    return slot_start < hour_end and slot_end > hour_start


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


def _priority_class(priority: str) -> str:
    """Map a priority label to a CSS class.

    Inputs:
        priority: Priority label.
    Outputs:
        CSS class name for the priority.
    """
    mapping = {
        "1st Priority": "first",
        "2nd Priority": "second",
        "3rd Priority": "third",
        "Low Priority": "low",
    }
    return mapping.get(priority, "not-set")


def _render_flash_messages(context: dict) -> str:
    """Render flash messages from context.

    Inputs:
        context: Page context dictionary.
    Outputs:
        HTML for flash messages or empty string.
    """
    success = _flash(context.get('message', ''), 'success')
    error = _flash(context.get('error', ''), 'error')
    return f"{success}{error}"


def _render_view_tabs(view: str) -> str:
    """Render view tabs for availability page.

    Inputs:
        view: Currently active view name.
    Outputs:
        HTML for the view tabs.
    """
    return f"""
    <div class=\"availability-tabs\">
        <a class=\"tab-pill {'active' if view == 'dashboard' else ''}\" href=\"/ambassador/availability?view=dashboard\">Dashboard</a>
        <a class=\"tab-pill {'active' if view == 'weekly' else ''}\" href=\"/ambassador/availability?view=weekly\">Weekly Availability</a>
    </div>
    """


def _render_report_rows(rows: list[dict]) -> str:
    """Render report table body rows.

    Inputs:
        rows: Report row records.
    Outputs:
        HTML table rows with ambassador data.
    """
    row_html = "".join([
        f'<tr><td>{escape(row["name"])}</td><td>{escape(row["email"])}</td><td>{escape(row.get("major") or "-")}</td><td>{escape(row.get("year") or "-")}</td><td>{row["assigned_tours"]}</td><td>{row["total_hours"]}</td></tr>'
        for row in rows
    ])
    return row_html or '<tr><td colspan="6">No ambassadors matched the selected filters.</td></tr>'


def _render_nav_link(label: str, href: str, is_active: bool) -> str:
    """Render a single navigation link.

    Inputs:
        label: Link text.
        href: Link URL.
        is_active: Whether the link is currently active.
    Outputs:
        HTML for one navigation link.
    """
    active_class = "active" if is_active else ""
    return f'<a class="quick-link {active_class}" href="{href}">{label}</a>'


def _build_schedule_column(schedule: dict, key: str, day: str) -> str:
    """Build a single schedule table column.

    Inputs:
        schedule: Schedule payload from the query layer.
        key: Block key in schedule payload.
        day: Day label.
    Outputs:
        HTML table column with ambassador names.
    """
    names = schedule[key][day]["names"]
    entries = "".join(
        f"<div>{idx}. {escape(name)}</div>" for idx, name in enumerate(names, start=1))
    return f"<td>{entries}</td>"


def _render_flash_messages(context: dict) -> str:
    """Render flash messages from context.

    Inputs:
        context: Page context dictionary.
    Outputs:
        HTML for flash messages or empty string.
    """
    success = _flash(context.get('message', ''), 'success')
    error = _flash(context.get('error', ''), 'error')
    return f"{success}{error}"
