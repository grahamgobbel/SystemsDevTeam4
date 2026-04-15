"""
Rendering helpers for the TCU Ambassador Scheduling System.
"""

from html import escape
from urllib.parse import quote_plus


WEEKDAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
PRIORITY_CLASS = {
    "1st Priority": "first",
    "2nd Priority": "second",
    "3rd Priority": "third",
    "Low Priority": "low",
}


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
        {_flash(context.get('message', ''), 'success')}
        {_flash(context.get('error', ''), 'error')}
        <form method=\"post\" action=\"/login\" class=\"login-form\">
            <label>Email Address <span class=\"required\">*</span></label>
            <input type=\"email\" name=\"email\" placeholder=\"john.doe@tcu.edu\" required>
            <p class=\"field-help\">Format: firstname.lastname@tcu.edu</p>
            <label>Password <span class=\"required\">*</span></label>
            <input type="password" name="password" placeholder="Enter your password (optional for demo)">
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
    assignments_markup = "".join(
        f"""
        <article class=\"assignment-card\">
            <div class=\"assignment-head\">
                <h3>{escape(item['tour_type'])}</h3>
                <span class=\"status-chip {item['status']}\">{escape(item['status'])}</span>
            </div>
            <p class=\"muted\">{escape(item['location'])}</p>
            <p class=\"muted\">{escape(item['tour_date_label'])} at {escape(item['tour_time'])}</p>
        </article>
        """
        for item in context["assignments"]
    ) or '<div class="empty-block">No assignments yet. Add availability to be included in the next schedule refresh.</div>'
    notifications_markup = "".join(
        f'<article class="notice-card {escape(item["kind"])}"><strong>{escape(item["title"])}</strong><p>{escape(item["detail"])}</p><span>{escape(item["age_label"])}</span></article>'
        for item in context["notifications"]
    )
    body = f"""
    <section class=\"content-main\">
        <div class=\"page-header\">
            <div>
                <h1>Welcome, {escape(user['name'])}!</h1>
                <p>Here is your auto-generated Daily Tours schedule and the latest updates.</p>
            </div>
            <a class=\"green-button\" href=\"/ambassador/availability?user={user['id']}&role=ambassador&view=weekly\">Submit Availability</a>
        </div>
        <div class=\"two-column\">
            <div>
                <div class=\"section-title-row\"><h2>Upcoming Assignments</h2></div>
                <div class=\"stack\">{assignments_markup}</div>
            </div>
            <aside class=\"right-column\">
                <h2>Notifications</h2>
                <div class=\"stack\">{notifications_markup}</div>
                <div class=\"month-card\">
                    <h3>This Week</h3>
                    <div><span>Assigned Daily Tours</span><strong>{context['stats']['total_tours']}</strong></div>
                    <div><span>Tours Completed</span><strong>{context['stats']['hours_completed']}</strong></div>
                    <div><span>Upcoming Events</span><strong>{context['stats']['upcoming_events']}</strong></div>
                </div>
            </aside>
        </div>
    </section>
    """
    return _shell(user, "home", body, role="ambassador")


def _render_availability(context: dict) -> str:
    user = context["user"]
    tab_markup = f"""
    <div class=\"availability-tabs\">
        <a class=\"tab-pill {'active' if context['view'] == 'dashboard' else ''}\" href=\"/ambassador/availability?user={user['id']}&role=ambassador&view=dashboard\">Dashboard</a>
        <a class=\"tab-pill {'active' if context['view'] == 'weekly' else ''}\" href=\"/ambassador/availability?user={user['id']}&role=ambassador&view=weekly\">Weekly Availability</a>
    </div>
    """
    panel = _availability_dashboard(
        context) if context["view"] == "dashboard" else _availability_form(context)
    body = f"""
    <section class=\"content-main\">
        <div class=\"page-header compact\">
            <div>
                <h1>Submit Availability</h1>
                <p>Daily Tours only run Monday through Friday at 10:00 AM and 2:00 PM.</p>
            </div>
        </div>
        {_flash(context.get('message', ''), 'success')}
        {_flash(context.get('error', ''), 'error')}
        <div class=\"info-panel\">
            <strong>How it Works</strong>
            <p><b>Weekly Availability:</b> Add repeating weekly time blocks that cover the fixed Daily Tour times.</p>
            <p><b>Preference Rankings:</b> The auto-assignment engine prefers 1st Priority slots first, then spreads work evenly.</p>
            <p><b>Automatic Schedule:</b> Admin scheduling uses the availability you submit here.</p>
        </div>
        <div class=\"purple-banner\"><div><span>Weekly Slots</span><strong>{context['slot_count']}</strong></div></div>
        {tab_markup}
        {panel}
    </section>
    """
    return _shell(user, "availability", body, role="ambassador")


def _render_profile(context: dict) -> str:
    user = context["user"]
    body = f"""
    <section class=\"content-main\">
        <div class=\"page-header compact\">
            <div>
                <h1>Ambassador Profile</h1>
                <p>Update your information to keep your ambassador record current.</p>
            </div>
        </div>
        {_flash(context.get('message', ''), 'success')}
        {_flash(context.get('error', ''), 'error')}
        <div class=\"profile-grid\">
            <div class=\"profile-card\">
                <div class=\"avatar-circle\">A</div>
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
                <p>Fields marked with <span class=\"required\">*</span> are required.</p>
                <label>Major <span class=\"required\">*</span></label>
                <select name=\"major\">{_options(context['majors'], user.get('major', ''))}</select>
                <label>Minor</label>
                <select name=\"minor\">{_options(context['minors'], user.get('minor', ''), 'Select your minor')}</select>
                <label>Year <span class=\"required\">*</span></label>
                <select name=\"year\">{_options(context['years'], user.get('year', ''))}</select>
                <label>Personality Type</label>
                <select name=\"personality\">{_options(context['personalities'], user.get('personality', ''), 'Select personality')}</select>
                <div class=\"form-actions right\"><button class=\"primary\" type=\"submit\">Save Changes</button></div>
            </form>
        </div>
    </section>
    """
    return _shell(user, "profile", body, role="ambassador")


def _render_admin(context: dict) -> str:
    user = context["user"]
    schedule = context["schedule"]
    morning_columns = _schedule_columns(schedule['slots_by_time']["10:00 AM"])
    afternoon_columns = _schedule_columns(schedule['slots_by_time']["2:00 PM"])
    ambassadors_markup = "".join(
        f"""
        <article class=\"ambassador-row\">
            <div class=\"avatar-small\">{escape(item['name'][0])}</div>
            <div class=\"ambassador-copy\">
                <strong>{escape(item['name'])}</strong>
                <p>{escape(item['email'])}</p>
            </div>
            <span class=\"hour-chip\">{item['tours_completed']} tours</span>
            <form method=\"post\" action=\"/admin\">
                <input type=\"hidden\" name=\"user\" value=\"{user['id']}\">
                <input type=\"hidden\" name=\"action\" value=\"delete_ambassador\">
                <input type=\"hidden\" name=\"ambassador_id\" value=\"{item['id']}\">
                <button class=\"secondary\" type=\"submit\">Remove</button>
            </form>
        </article>
        """
        for item in context['ambassadors']
    )
    body = f"""
    <section class=\"content-main\">
        <div class=\"page-header compact\">
            <div>
                <h1>Admin Dashboard</h1>
                <p>Daily Tours are automatically assigned from ambassador availability.</p>
            </div>
        </div>
        {_flash(context.get('message', ''), 'success')}
        {_flash(context.get('error', ''), 'error')}
        <div class=\"metric-grid\">
            {_metric_card('Total Ambassadors', context['stats']['total_ambassadors'])}
            {_metric_card('Weekly Tour Slots', context['stats']['tour_slots'])}
            {_metric_card('Filled Slots', context['stats']['filled_slots'])}
            {_metric_card('Open Positions', context['stats']['unfilled_positions'])}
        </div>
        <div class=\"info-panel\">
            <strong>Automatic Assignment Rules</strong>
            <p>The app only schedules Daily Tours on Monday through Friday at 10:00 AM and 2:00 PM. Assignments are generated from submitted availability and ranked by priority.</p>
        </div>
        <section class=\"schedule-section\">
            <h2>Weekly Tour Schedule</h2>
            <div class=\"schedule-block\">
                <h3>10:00 AM Daily Tours</h3>
                <div class=\"schedule-grid\">{morning_columns}</div>
            </div>
            <div class=\"schedule-block\">
                <h3>2:00 PM Daily Tours</h3>
                <div class=\"schedule-grid\">{afternoon_columns}</div>
            </div>
        </section>
        <section class=\"admin-section\">
            <div class=\"section-head\">
                <div>
                    <h3>Ambassador Management</h3>
                    <p>Add, remove, and manage ambassador accounts.</p>
                </div>
            </div>
            <form method=\"post\" action=\"/admin\" class=\"admin-form-grid\">
                <input type=\"hidden\" name=\"user\" value=\"{user['id']}\">
                <input type=\"hidden\" name=\"action\" value=\"add_ambassador\">
                <input name=\"name\" placeholder=\"Full Name\">
                <input name=\"email\" placeholder=\"name@tcu.edu\">
                <input name=\"major\" placeholder=\"Major\">
                <select name=\"year\">
                    <option value=\"\">Year</option>
                    <option>Freshman</option>
                    <option>Sophomore</option>
                    <option>Junior</option>
                    <option>Senior</option>
                </select>
                <button class=\"primary\" type=\"submit\">Add Ambassador</button>
            </form>
            <div class=\"stack\">{ambassadors_markup}</div>
        </section>
    </section>
    """
    return _shell(user, "admin", body, role="admin")


def _availability_dashboard(context: dict) -> str:
    header = ''.join(
        f'<div class="day-head"><strong>{day[:3]}</strong><span>{day}</span></div>' for day in WEEKDAY_ORDER
    )
    cells = []
    for time_label in context['time_labels']:
        cells.append(f'<div class="time-col">{time_label}</div>')
        for day in WEEKDAY_ORDER:
            priority = context['grid'][day][time_label]
            class_name = PRIORITY_CLASS.get(priority, 'unset')
            cells.append(
                f'<div class="calendar-cell {class_name}">{escape(priority)}</div>')
    return f"""
    <section class=\"dashboard-panel\">
        <div class=\"panel-header\">
            <div>
                <h3>Availability Dashboard</h3>
                <p>Visual overview of your recurring weekly availability.</p>
            </div>
        </div>
        <div class=\"legend\">
            <span class=\"legend-item first\">1st Priority</span>
            <span class=\"legend-item second\">2nd Priority</span>
            <span class=\"legend-item third\">3rd Priority</span>
            <span class=\"legend-item low\">Low Priority</span>
            <span class=\"legend-item unset\">Not Set</span>
        </div>
        <div class=\"calendar-grid\"><div class=\"time-head\">Time</div>{header}{''.join(cells)}</div>
    </section>
    """


def _availability_form(context: dict) -> str:
    user = context['user']
    rows = ''.join(
        f'<div class="slot-row"><span>{escape(item["day"])}</span><span>{escape(item["start_time"])} - {escape(item["end_time"])} </span><span>{escape(item["priority"])}</span></div>'
        for item in context['slots']
    ) or '<div class="empty-block">No weekly slots added yet.</div>'
    return f"""
    <section class=\"dashboard-panel\">
        <div class=\"section-head\">
            <div>
                <h3>Set Weekly Schedule</h3>
                <p>Define your regular availability that repeats every week.</p>
            </div>
        </div>
        <form class=\"slot-form\" method=\"post\" action=\"/ambassador/availability\">
            <input type=\"hidden\" name=\"user\" value=\"{user['id']}\">
            <input type=\"hidden\" name=\"action\" value=\"add_slot\">
            <select name=\"day\">{_options(context['days'], '', 'Select day')}</select>
            <select name=\"start_time\">{_options(context['time_labels'], '', 'Start time')}</select>
            <select name=\"end_time\">{_options(context['time_labels'], '', 'End time')}</select>
            <select name=\"priority\">{_options(context['priorities'], '', 'Priority')}</select>
            <button class=\"primary\" type=\"submit\">Add Weekly Slot</button>
        </form>
        <div class=\"draft-box\">{rows}</div>
        <form method=\"post\" action=\"/ambassador/availability\" class=\"footer-actions\">
            <input type=\"hidden\" name=\"user\" value=\"{user['id']}\">
            <input type=\"hidden\" name=\"action\" value=\"submit_availability\">
            <button class=\"green-button\" type=\"submit\">Submit Availability</button>
        </form>
    </section>
    """


def _schedule_columns(slots: list[dict]) -> str:
    markup = []
    for slot in slots:
        names = ''.join(
            f'<li>{escape(item["name"])}</li>' for item in slot['assigned'])
        if slot['open_positions'] > 0:
            names += f'<li class="open-row">Open positions: {slot["open_positions"]}</li>'
        markup.append(
            f"""
            <div class=\"schedule-column\">
                <div class=\"schedule-column-head\">{escape(slot['label'])}</div>
                <ul>{names}</ul>
            </div>
            """
        )
    return ''.join(markup)


def _shell(user: dict, active: str, content: str, role: str) -> str:
    return f"""<!doctype html>
<html lang=\"en\">
<head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>TCU Ambassador Scheduling</title>
    <link rel=\"stylesheet\" href=\"/static/styles.css\">
</head>
<body>
    <header class=\"top-nav\">{_top_nav(user, active, role)}</header>
    <div class=\"app-frame\">
        <aside class=\"left-rail\">{_side_nav(user, active, role)}</aside>
        <main class=\"page-shell\">{content}</main>
    </div>
</body>
</html>"""


def _top_nav(user: dict, active: str, role: str) -> str:
    if role == 'admin':
        center = f'<a class="top-link active" href="/admin?user={user["id"]}&role=admin">Admin Dashboard</a>'
    else:
        center = ''.join([
            f'<a class="top-link {"active" if active == "home" else ""}" href="/ambassador/dashboard?user={user["id"]}&role=ambassador">Home</a>',
            f'<a class="top-link {"active" if active == "availability" else ""}" href="/ambassador/availability?user={user["id"]}&role=ambassador&view=dashboard">Availability</a>',
            f'<a class="top-link {"active" if active == "profile" else ""}" href="/ambassador/profile?user={user["id"]}&role=ambassador">Profile</a>',
        ])
    return f'<div class="top-left"><div class="frog-mark">TCU</div>{center}</div><div class="top-right"><span>Help</span><a class="logout-link" href="/">Logout</a></div>'


def _side_nav(user: dict, active: str, role: str) -> str:
    if role == 'admin':
        items = [
            ("Auto Schedule", f'/admin?user={user["id"]}&role=admin', True)]
    else:
        items = [
            ("Dashboard",
             f'/ambassador/dashboard?user={user["id"]}&role=ambassador', active == 'home'),
            ("Submit Availability",
             f'/ambassador/availability?user={user["id"]}&role=ambassador&view=weekly', active == 'availability'),
            ("Profile Settings",
             f'/ambassador/profile?user={user["id"]}&role=ambassador', active == 'profile'),
        ]
    links = ''.join(
        f'<a class="quick-link {"active" if is_active else ""}" href="{href}">{label}</a>'
        for label, href, is_active in items
    )
    return f'<p class="quick-title">Quick Actions</p>{links}'


def _metric_card(label: str, value: int) -> str:
    return f'<div class="metric-card"><span>{label}</span><strong>{value}</strong></div>'


def _flash(message: str, tone: str) -> str:
    if not message:
        return ''
    return f'<div class="flash {tone}">{escape(message)}</div>'


def _options(options: list[str], current: str, blank_label: str = 'Select') -> str:
    html = []
    selected = ' selected' if not current else ''
    html.append(f'<option value=""{selected}>{blank_label}</option>')
    for option in options:
        selected = ' selected' if option == current else ''
        html.append(
            f'<option value="{escape(option)}"{selected}>{escape(option)}</option>')
    return ''.join(html)
