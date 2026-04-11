"""
Rendering helpers for the TCU Ambassador Scheduling System.
"""

from html import escape
from urllib.parse import quote_plus


def validation_message(message: str) -> str:
    return quote_plus(message)


def redirect_response(handler, location: str) -> None:
    handler.send_response(303)
    handler.send_header("Location", location)
    handler.end_headers()


def send_html(handler, body: str) -> None:
    content = body.encode("utf-8")
    handler.send_response(200)
    handler.send_header("Content-Type", "text/html; charset=utf-8")
    handler.send_header("Content-Length", str(len(content)))
    handler.end_headers()
    handler.wfile.write(content)


def render_page(page: str, context: dict) -> str:
    if page == "login":
        return _render_login(context)
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
        <p class=\"hero-copy\">Sign in to manage your schedule and availability</p>
        {message}
        {error}
        <form method=\"post\" action=\"/login\" class=\"login-form\">
            <label>Email Address <span class=\"required\">*</span></label>
            <input type=\"email\" name=\"email\" placeholder=\"john.doe@tcu.edu\" required>
            <p class=\"field-help\">Format: firstname.lastname@tcu.edu</p>

            <label>Password <span class=\"required\">*</span></label>
            <input type=\"password\" name=\"password\" placeholder=\"Enter your password\" required>

            <label>Select Role <span class=\"required\">*</span></label>
            <label class=\"radio-card\"><input type=\"radio\" name=\"role\" value=\"admin\" required> <span>Admin</span></label>
            <label class=\"radio-card\"><input type=\"radio\" name=\"role\" value=\"ambassador\" required checked> <span>Ambassador</span></label>

            <button class=\"primary large\" type=\"submit\">Login</button>
        </form>
        <p class=\"forgot-link\">Forgot Password?</p>
        <div class=\"demo-box\">
            <strong>Demo login</strong>
            <p>Ambassador: graham.gobbel@tcu.edu / frog2026</p>
            <p>Admin: admin@tcu.edu / frog2026</p>
        </div>
    </div>
</body>
</html>"""


def _render_ambassador_dashboard(context: dict) -> str:
    user = context["user"]
    assignments = "".join(_assignment_card(item) for item in context["assignments"])
    notifications = "".join(_notification_card(item) for item in context["notifications"])
    stats = context["stats"]
    content = f"""
    <section class=\"content-main\">
        <div class=\"page-header\">
            <div>
                <h1>Welcome, {escape(user['name'])}!</h1>
                <p>Here's your schedule overview and latest updates</p>
            </div>
            <a class=\"green-button\" href=\"/ambassador/availability?user={user['id']}&role=ambassador&view=weekly\">Submit Availability</a>
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
    user = context["user"]
    view = context["view"]
    tabs = f"""
    <div class=\"availability-tabs\">
        <a class=\"tab-pill {'active' if view == 'dashboard' else ''}\" href=\"/ambassador/availability?user={user['id']}&role=ambassador&view=dashboard\">Dashboard</a>
        <a class=\"tab-pill {'active' if view == 'weekly' else ''}\" href=\"/ambassador/availability?user={user['id']}&role=ambassador&view=weekly\">Weekly Availability</a>
    </div>
    """
    if view == "dashboard":
        main_panel = _availability_grid(context)
    else:
        main_panel = _availability_form(context)
    body = f"""
    <section class=\"content-main\">
        <div class=\"page-header compact\">
            <div>
                <h1>Submit Availability</h1>
                <p>Set up your weekly schedule with preference rankings</p>
            </div>
        </div>
        {_flash(context.get('message', ''), 'success')}
        {_flash(context.get('error', ''), 'error')}
        <div class=\"info-panel\">
            <strong>How it Works</strong>
            <p><b>Weekly Availability:</b> Set your regular weekly schedule that repeats each week.</p>
            <p><b>Preference Rankings:</b> Rank your eagerness to work each time slot (1st, 2nd, 3rd priority, or Low priority).</p>
            <p><b>Dashboard View:</b> See your complete availability schedule at a glance.</p>
        </div>
        <div class=\"purple-banner\"><span class=\"rotate-icon\">?</span><div><span>Weekly Slots</span><strong>{context['slot_count']}</strong></div></div>
        {tabs}
        {main_panel}
    </section>
    """
    return _shell(user, "availability", body, role="ambassador")


def _render_profile(context: dict) -> str:
    user = context["user"]
    major_options = _options(context["majors"], user.get("major", ""))
    minor_options = _options(context["minors"], user.get("minor", ""), allow_blank_label="Select your minor")
    year_options = _options(context["years"], user.get("year", ""))
    personality_options = _options(context["personalities"], user.get("personality", ""))
    body = f"""
    <section class=\"content-main\">
        <div class=\"page-header compact\">
            <div>
                <h1>Ambassador Profile</h1>
                <p>Update your information to help us match you with the right tours and events</p>
            </div>
        </div>
        {_flash(context.get('message', ''), 'success')}
        {_flash(context.get('error', ''), 'error')}
        <div class=\"profile-grid\">
            <div class=\"profile-card\">
                <div class=\"avatar-circle\">?</div>
                <h3>{escape(user['name'])}</h3>
                <p>{escape(user['email'])}</p>
                <div class=\"profile-stats\">
                    <div><span>Status</span><strong>{escape(user['status'])}</strong></div>
                    <div><span>Ambassador Since</span><strong>{escape(user.get('ambassador_since') or '')}</strong></div>
                    <div><span>Tours Completed</span><strong>{user['tours_completed']}</strong></div>
                </div>
            </div>
            <form class=\"settings-card\" method=\"post\" action=\"/ambassador/profile\">
                <input type=\"hidden\" name=\"user\" value=\"{user['id']}\">
                <h3>Academic Information</h3>
                <p>Fields marked with <span class=\"required\">*</span> are required</p>
                <label>Major <span class=\"required\">*</span></label>
                <select name=\"major\">{major_options}</select>
                <label>Minor (Optional)</label>
                <select name=\"minor\">{minor_options}</select>
                <label>Year <span class=\"required\">*</span></label>
                <select name=\"year\">{year_options}</select>
                <label>Personality Type</label>
                <select name=\"personality\">{personality_options}</select>
                <div class=\"form-actions right\"><button class=\"primary\" type=\"submit\">Save Changes</button></div>
            </form>
        </div>
    </section>
    """
    return _shell(user, "profile", body, role="ambassador")


def _render_admin(context: dict) -> str:
    user = context["user"]
    stat = context["stats"]
    tours_markup = "".join(_tour_card(item, user['id']) for item in context["tours"])
    ambassadors_markup = "".join(_ambassador_row(item, user['id']) for item in context["ambassadors"])
    body = f"""
    <section class=\"content-main\">
        <div class=\"page-header compact\">
            <div>
                <h1>Admin Dashboard</h1>
                <p>Create tours and assign ambassadors to time slots</p>
            </div>
        </div>
        {_flash(context.get('message', ''), 'success')}
        {_flash(context.get('error', ''), 'error')}
        <div class=\"metric-grid\">
            {_metric_card('Total Ambassadors', stat['total_ambassadors'], 'purple')}
            {_metric_card('Scheduled Tours', stat['scheduled'], 'blue')}
            {_metric_card('Assigned Tours', stat['assigned'], 'green')}
            {_metric_card('Unassigned Tours', stat['unassigned'], 'gold')}
        </div>
        <div class=\"info-panel\"><strong>Tour Management</strong><p>Create available tour slots and assign ambassadors based on their availability. The system shows you which ambassadors are available for each time slot.</p></div>
        <div class=\"admin-section\">
            <div class=\"section-head\">
                <div><h3>Create & Assign Tours</h3><p>Set up tour time slots and assign ambassadors</p></div>
            </div>
            <form method=\"post\" action=\"/admin\" class=\"admin-form-grid\">
                <input type=\"hidden\" name=\"user\" value=\"{user['id']}\">
                <input type=\"hidden\" name=\"action\" value=\"add_tour\">
                <input name=\"tour_type\" placeholder=\"Tour Type\">
                <input name=\"tour_date\" placeholder=\"2026-04-22\">
                <input name=\"start_time\" placeholder=\"11:00 AM\">
                <input name=\"end_time\" placeholder=\"01:00 PM\">
                <input name=\"location\" placeholder=\"Admissions Office\">
                <input name=\"ambassadors_needed\" placeholder=\"2\">
                <button class=\"primary\" type=\"submit\">Add Tour</button>
            </form>
            <div class=\"stack\">{tours_markup}</div>
        </div>
        <div class=\"admin-section\">
            <div class=\"section-head\">
                <div><h3>Ambassador Management</h3><p>Add, remove, and manage ambassador accounts</p></div>
            </div>
            <form method=\"post\" action=\"/admin\" class=\"admin-form-grid\">
                <input type=\"hidden\" name=\"user\" value=\"{user['id']}\">
                <input type=\"hidden\" name=\"action\" value=\"add_ambassador\">
                <input name=\"name\" placeholder=\"Full Name\">
                <input name=\"email\" placeholder=\"name@tcu.edu\">
                <input name=\"major\" placeholder=\"Major\">
                <select name=\"year\"><option value=\"\">Year</option><option>Freshman</option><option>Sophomore</option><option>Junior</option><option>Senior</option></select>
                <button class=\"primary\" type=\"submit\">Add Ambassador</button>
            </form>
            <div class=\"stack\">{ambassadors_markup}</div>
            <form method=\"post\" action=\"/admin\" class=\"footer-actions\">
                <input type=\"hidden\" name=\"user\" value=\"{user['id']}\">
                <input type=\"hidden\" name=\"action\" value=\"publish_tours\">
                <button class=\"secondary\" type=\"button\">Clear All</button>
                <button class=\"green-button\" type=\"submit\">Publish Tours</button>
            </form>
        </div>
    </section>
    """
    return _shell(user, "admin", body, role="admin")


def _shell(user: dict, active: str, content: str, role: str) -> str:
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
</body>
</html>"""


def _top_nav(user: dict, active: str, role: str) -> str:
    if role == "admin":
        center = f'<a class="top-link {"active" if active == "admin" else ""}" href="/admin?user={user["id"]}&role=admin">Admin Dashboard</a>'
    else:
        center = "".join([
            f'<a class="top-link {"active" if active == "home" else ""}" href="/ambassador/dashboard?user={user["id"]}&role=ambassador">Home</a>',
            f'<a class="top-link {"active" if active == "availability" else ""}" href="/ambassador/availability?user={user["id"]}&role=ambassador&view=dashboard">Availability</a>',
            f'<a class="top-link {"active" if active == "profile" else ""}" href="/ambassador/profile?user={user["id"]}&role=ambassador">Profile</a>'
        ])
    return f'<div class="top-left"><div class="frog-mark">TCU</div>{center}</div><div class="top-right"><span>Help</span><a class="logout-link" href="/">Logout</a></div>'


def _side_nav(user: dict, active: str, role: str) -> str:
    items = []
    if role == "admin":
        items.append(("Admin Dashboard", f"/admin?user={user['id']}&role=admin", active == "admin"))
    else:
        items.extend([
            ("Dashboard", f"/ambassador/dashboard?user={user['id']}&role=ambassador", active == "home"),
            ("Submit Availability", f"/ambassador/availability?user={user['id']}&role=ambassador&view=weekly", active == "availability"),
            ("Profile Settings", f"/ambassador/profile?user={user['id']}&role=ambassador", active == "profile"),
        ])
    links = "".join([f'<a class="quick-link {"active" if is_active else ""}" href="{href}">{label}</a>' for label, href, is_active in items])
    return f'<p class="quick-title">Quick Actions</p>{links}'


def _assignment_card(item: dict) -> str:
    status_class = "confirmed" if item["status"] == "confirmed" else "pending"
    return f"""
    <article class=\"assignment-card\">
        <div class=\"assignment-head\"><h3>{escape(item['tour_type'])}</h3><span class=\"status-chip {status_class}\">{escape(item['status'])}</span></div>
        <p class=\"muted\">{escape(item['location'])}</p>
        <div class=\"assignment-meta\"><span>{_pretty_date(item['tour_date'])}</span><span>{escape(item['start_time'])} to {escape(item['end_time'])}</span></div>
    </article>
    """


def _notification_card(item: dict) -> str:
    return f'<article class="notice-card {escape(item["kind"])}"><strong>{escape(item["title"])}</strong><p>{escape(item["detail"])}</p><span>{escape(item["age_label"])}</span></article>'


def _availability_grid(context: dict) -> str:
    slots = context["slots"]
    grid_cells = []
    for time_label in context["time_labels"]:
        grid_cells.append(f'<div class="time-col">{time_label}</div>')
        for day in context["days"]:
            slot = next((item for item in slots if item["day"] == day and item["start_time"].startswith(time_label.split(":")[0])), None)
            label = escape(slot["priority"]) if slot else ""
            cls = _priority_class(slot["priority"]) if slot else "not-set"
            grid_cells.append(f'<div class="calendar-cell {cls}">{label}</div>')
    headings = "".join([f'<div class="day-head"><strong>{day[:3]}</strong><span>{num}</span></div>' for day, num in zip(context["days"], ["4/6","4/7","4/8","4/9","4/10","4/11","4/12"])])
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
        <div class=\"empty-footer\"><div class=\"calendar-icon\">¦</div><p>No availability set yet</p><span>Use the Weekly Availability tab to set your schedule</span></div>
    </section>
    """


def _availability_form(context: dict) -> str:
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
            <form class=\"slot-form\" method=\"post\" action=\"/ambassador/availability\">
                <input type=\"hidden\" name=\"user\" value=\"{user['id']}\">
                <input type=\"hidden\" name=\"action\" value=\"add_slot\">
                <select name=\"day\">{day_opts}</select>
                <select name=\"start_time\">{time_opts}</select>
                <select name=\"end_time\">{time_opts}</select>
                <select name=\"priority\">{pri_opts}</select>
                <button class=\"primary\" type=\"submit\">Add Weekly Slot</button>
            </form>
        </div>
        <div class=\"draft-box\">{rows}</div>
        <form method=\"post\" action=\"/ambassador/availability\" class=\"footer-actions\">
            <input type=\"hidden\" name=\"user\" value=\"{user['id']}\">
            <input type=\"hidden\" name=\"action\" value=\"submit_availability\">
            <button class=\"secondary\" type=\"button\">Clear All</button>
            <button class=\"green-button\" type=\"submit\">Submit Availability</button>
        </form>
    </section>
    """


def _tour_card(tour: dict, admin_user_id: int) -> str:
    assign_forms = "".join([
        f'''<form method="post" action="/admin" class="inline-form"><input type="hidden" name="user" value="{admin_user_id}"><input type="hidden" name="action" value="assign_tour"><input type="hidden" name="tour_id" value="{tour['id']}"><input type="hidden" name="ambassador_id" value="{candidate['id']}"><span>{escape(candidate['name'])}</span><button class="secondary small" type="submit">Add</button></form>'''
        for candidate in tour["eligible"]
    ])
    status = "published" if tour["published"] else "draft"
    return f"""
    <article class=\"tour-card\">
        <div class=\"tour-card-head\"><div><h4>{escape(tour['tour_type'])}</h4><p>{_pretty_date(tour['tour_date'])} | {escape(tour['start_time'])} to {escape(tour['end_time'])} | {escape(tour['location'])}</p></div><span class=\"status-chip {status}\">{status}</span></div>
        <p class=\"muted\">Assigned {tour['assigned_count']} of {tour['ambassadors_needed']} ambassadors</p>
        <div class=\"candidate-stack\">{assign_forms}</div>
    </article>
    """


def _ambassador_row(item: dict, admin_user_id: int) -> str:
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
    return f'<div class="metric-card {tone}"><span>{label}</span><strong>{value}</strong></div>'


def _flash(message: str, tone: str) -> str:
    if not message:
        return ""
    return f'<div class="flash {tone}">{escape(message)}</div>'


def _options(options: list[str], current: str, allow_blank_label: str = "Select") -> str:
    html = []
    if allow_blank_label is not None:
        selected = " selected" if not current else ""
        html.append(f'<option value=""{selected}>{allow_blank_label}</option>')
    for option in options:
        selected = " selected" if option == current else ""
        html.append(f'<option value="{escape(option)}"{selected}>{escape(option or allow_blank_label)}</option>')
    return "".join(html)


def _pretty_date(date_value: str) -> str:
    parts = date_value.split("-")
    if len(parts) != 3:
        return escape(date_value)
    year, month, day = parts
    month_names = {"04": "Apr.", "05": "May", "06": "Jun."}
    return f"{month_names.get(month, month) } {int(day)}, {year}".replace("  ", " ")


def _priority_class(priority: str) -> str:
    mapping = {
        "1st Priority": "first",
        "2nd Priority": "second",
        "3rd Priority": "third",
        "Low Priority": "low",
    }
    return mapping.get(priority, "not-set")
