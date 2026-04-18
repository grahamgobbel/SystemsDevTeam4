"""
Application Title: TCU Ambassador Scheduling System
Date: 2026-04-14
Authors: SystemsDevTeam4
Purpose: Run the HTTP server that serves the scheduling application and
routes form submissions to the business-logic helpers.

Run with:
    python app/main.py
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from http.cookies import SimpleCookie
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from database import get_connection
from queries import (
    add_ambassador,
    add_availability_slot,
    auto_assign_daily_tours,
    assign_ambassador_to_tour,
    build_admin_dashboard,
    build_ambassador_dashboard,
    build_availability_page,
    build_profile_page,
    clear_availability_slots,
    create_session,
    delete_session,
    delete_ambassador,
    get_user_by_session_token,
    initialize_database,
    lookup_user,
    create_account,
    seed_sample_student_database,
    update_profile,
)
from utils import redirect_response, render_page, send_html, validation_message


STATIC_DIR = Path(__file__).resolve().parent / "static"
HOST = "127.0.0.1"
PORT = 8000
SESSION_COOKIE_NAME = "tcu_session"
SESSION_TTL_SECONDS = 60 * 60 * 8


class SchedulingHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the scheduling application.

    Inputs:
        HTTP requests from the browser, including path, query parameters, and
        form body data.
    Outputs:
        HTML pages for GET requests and redirect responses for POST requests.
    """

    def do_GET(self):
        """Handle GET requests and render the requested page.

        Inputs:
            The current request path and query parameters.
        Outputs:
            Writes an HTML or static-file response to the client.
        """
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path == "/static/styles.css":
            self._send_static("styles.css", "text/css; charset=utf-8")
            return

        conn = get_connection()
        initialize_database(conn)

        try:
            if parsed.path == "/":
                body = render_page("login", {"message": params.get("message", [""])[
                                   0], "error": params.get("error", [""])[0]})
            elif parsed.path == "/register":
                body = render_page("register", {"message": params.get("message", [""])[
                                   0], "error": params.get("error", [""])[0]})
            elif parsed.path == "/logout":
                self._logout_session(conn)
                redirect_response(
                    self,
                    "/?message=" +
                    validation_message("You have been logged out."),
                    headers={"Set-Cookie": self._expired_session_cookie_header()},
                )
                return
            elif parsed.path == "/ambassador/dashboard":
                user_id = self._require_user(conn, "ambassador")
                body = render_page("ambassador_dashboard",
                                   build_ambassador_dashboard(conn, user_id))
            elif parsed.path == "/ambassador/availability":
                user_id = self._require_user(conn, "ambassador")
                view = params.get("view", ["dashboard"])[0]
                body = render_page("availability", build_availability_page(
                    conn, user_id, view, params.get("message", [""])[0], params.get("error", [""])[0]))
            elif parsed.path == "/ambassador/profile":
                user_id = self._require_user(conn, "ambassador")
                body = render_page("profile", build_profile_page(
                    conn, user_id, params.get("message", [""])[0], params.get("error", [""])[0]))
            elif parsed.path == "/admin":
                user_id = self._require_user(conn, "admin")
                body = render_page("admin", build_admin_dashboard(
                    conn,
                    user_id,
                    params.get("message", [""])[0],
                    params.get("error", [""])[0],
                    params.get("search", [""])[0],
                    params.get("tour_status", ["all"])[0],
                ))
            else:
                self.send_error(404, "Page not found")
                return
        except PermissionError:
            body = render_page("login", {
                               "error": "Please log in with the correct role to continue.", "message": ""})
        finally:
            conn.close()

        send_html(self, body)

    def do_POST(self):
        """Handle POST requests from the application forms.

        Inputs:
            The current request path and submitted form fields.
        Outputs:
            Writes a redirect response after processing the action.
        """
        parsed = urlparse(self.path)
        form = self._read_form()

        conn = get_connection()
        initialize_database(conn)

        try:
            if parsed.path == "/login":
                redirect, headers = self._handle_login(conn, form)
            elif parsed.path == "/register":
                redirect, headers = self._handle_register(conn, form)
            elif parsed.path == "/ambassador/availability":
                redirect, headers = self._handle_availability(conn, form)
            elif parsed.path == "/ambassador/profile":
                redirect, headers = self._handle_profile(conn, form)
            elif parsed.path == "/admin":
                redirect, headers = self._handle_admin(conn, form)
            else:
                self.send_error(404, "Page not found")
                return
        except PermissionError:
            redirect = "/?error=" + \
                validation_message("Please log in to continue.")
            headers = {"Set-Cookie": self._expired_session_cookie_header()}
        finally:
            conn.close()

        redirect_response(self, redirect, headers=headers)

    def log_message(self, format, *args):
        """Suppress default server logging.

        Inputs:
            Logging format string and arguments from the base handler.
        Outputs:
            None.
        """
        return

    def _send_static(self, filename: str, content_type: str) -> None:
        """Write a static asset to the response body.

        Inputs:
            filename: File name inside the app/static directory.
            content_type: MIME type for the response.
        Outputs:
            Sends the file bytes to the browser.
        """
        file_bytes = (STATIC_DIR / filename).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(file_bytes)))
        self.end_headers()
        self.wfile.write(file_bytes)

    def _read_form(self) -> dict:
        """Parse URL-encoded POST data into a dictionary.

        Inputs:
            The request body and Content-Length header.
        Outputs:
            A mapping of submitted field names to their first value.
        """
        length = int(self.headers.get("Content-Length", 0))
        raw_data = self.rfile.read(length).decode("utf-8")
        return {key: values[0] for key, values in parse_qs(raw_data).items()}

    def _require_user(self, conn, role: str) -> int:
        """Validate session user context for the requested role.

        Inputs:
            conn: Open database connection.
            role: Expected role for the page being viewed.
        Outputs:
            The validated session user id.
        """
        token = self._session_token()
        user = get_user_by_session_token(conn, token)
        if not user or user.get("role") != role:
            raise PermissionError
        return int(user["id"])

    def _session_token(self) -> str:
        """Extract session token from cookie header.

        Inputs:
            None.
        Outputs:
            Raw session token or empty string.
        """
        cookie_header = self.headers.get("Cookie", "")
        if not cookie_header:
            return ""
        cookie = SimpleCookie()
        cookie.load(cookie_header)
        morsel = cookie.get(SESSION_COOKIE_NAME)
        return morsel.value if morsel else ""

    def _session_cookie_header(self, token: str) -> str:
        """Build Set-Cookie value for an active session token."""
        return f"{SESSION_COOKIE_NAME}={token}; Max-Age={SESSION_TTL_SECONDS}; Path=/; HttpOnly; SameSite=Lax"

    def _expired_session_cookie_header(self) -> str:
        """Build Set-Cookie value that expires the session cookie."""
        return f"{SESSION_COOKIE_NAME}=; Max-Age=0; Path=/; HttpOnly; SameSite=Lax"

    def _logout_session(self, conn) -> None:
        """Delete current session token from storage if present."""
        delete_session(conn, self._session_token())

    def _handle_login(self, conn, form: dict) -> tuple[str, dict]:
        """Authenticate a user and build the redirect target.

        Inputs:
            conn: Open database connection.
            form: Submitted login fields.
        Outputs:
            A redirect URL for the matching dashboard or an error page.
        """
        email = form.get("email", "").strip()
        password = form.get("password", "")

        if not email:
            return "/?error=" + validation_message("Enter an email address to continue."), {}
        if not password:
            return "/?error=" + validation_message("Enter your password to continue."), {}

        user = lookup_user(conn, email, password)
        if not user:
            return "/?error=" + validation_message("Invalid email or password."), {}

        token = create_session(conn, int(user["id"]), SESSION_TTL_SECONDS)
        headers = {"Set-Cookie": self._session_cookie_header(token)}

        if user["role"] == "admin":
            return "/admin?message=" + validation_message("Welcome back. Tour management is ready."), headers
        return "/ambassador/dashboard?message=" + validation_message("Welcome back. Your dashboard is up to date."), headers

    def _handle_register(self, conn, form: dict) -> tuple[str, dict]:
        """Create an account and redirect to login with feedback.

        Inputs:
            conn: Open database connection.
            form: Submitted registration fields.
        Outputs:
            Redirect URL with success or error feedback.
        """
        ok, message = create_account(
            conn,
            form.get("name", ""),
            form.get("email", ""),
            form.get("password", ""),
            form.get("confirm_password", ""),
            form.get("role", "ambassador"),
        )
        if ok:
            return "/?message=" + validation_message(message), {}
        return "/register?error=" + validation_message(message), {}

    def _handle_availability(self, conn, form: dict) -> tuple[str, dict]:
        """Process ambassador availability actions and build a redirect URL.

        Inputs:
            conn: Open database connection.
            form: Submitted availability fields.
        Outputs:
            A redirect URL with success or error feedback.
        """
        user_id = self._require_user(conn, "ambassador")
        action = form.get("action", "")

        if action == "add_slot":
            ok, message = add_availability_slot(
                conn,
                user_id,
                form.get("day", ""),
                form.get("start_time", ""),
                form.get("end_time", ""),
                form.get("priority", ""),
            )
            key = "message" if ok else "error"
            return f"/ambassador/availability?view=weekly&{key}=" + validation_message(message), {}

        if action == "submit_availability":
            return "/ambassador/availability?view=dashboard&message=" + validation_message("Availability submitted successfully."), {}

        if action == "clear_all":
            ok, message = clear_availability_slots(conn, user_id)
            key = "message" if ok else "error"
            return f"/ambassador/availability?view=weekly&{key}=" + validation_message(message), {}

        return "/ambassador/availability?view=weekly&error=" + validation_message("Unknown availability action."), {}

    def _handle_profile(self, conn, form: dict) -> tuple[str, dict]:
        """Process ambassador profile updates and build a redirect URL.

        Inputs:
            conn: Open database connection.
            form: Submitted profile fields.
        Outputs:
            A redirect URL with feedback for the profile page.
        """
        user_id = self._require_user(conn, "ambassador")
        ok, message = update_profile(
            conn,
            user_id,
            form.get("major", ""),
            form.get("minor", ""),
            form.get("year", ""),
            form.get("involvement_level", ""),
        )
        key = "message" if ok else "error"
        return f"/ambassador/profile?{key}=" + validation_message(message), {}

    def _handle_admin(self, conn, form: dict) -> tuple[str, dict]:
        """Process admin actions and build a redirect URL.

        Inputs:
            conn: Open database connection.
            form: Submitted admin form fields.
        Outputs:
            A redirect URL with success or error feedback.
        """
        user_id = self._require_user(conn, "admin")
        action = form.get("action", "")
        base = "/admin"

        if action == "auto_assign_daily_tours":
            ok, message = auto_assign_daily_tours(conn)
            return base + ("?message=" if ok else "?error=") + validation_message(message), {}

        if action == "seed_sample_student_database":
            ok, message = seed_sample_student_database(conn)
            return base + ("?message=" if ok else "?error=") + validation_message(message), {}

        if action == "assign_tour":
            ok, message = assign_ambassador_to_tour(
                conn,
                int(form.get("tour_id", "0") or "0"),
                int(form.get("ambassador_id", "0") or "0"),
            )
            return base + ("?message=" if ok else "?error=") + validation_message(message), {}

        if action == "add_ambassador":
            ok, message = add_ambassador(
                conn,
                form.get("name", ""),
                form.get("email", ""),
                form.get("major", ""),
                form.get("year", ""),
            )
            return base + ("?message=" if ok else "?error=") + validation_message(message), {}

        if action == "delete_ambassador":
            ok, message = delete_ambassador(
                conn, int(form.get("ambassador_id", "0")))
            return base + ("?message=" if ok else "?error=") + validation_message(message), {}

        return base + "?error=" + validation_message("Unknown admin action."), {}


def main() -> None:
    """Start the HTTP server for the scheduling application.

    Inputs:
        None.
    Outputs:
        Runs the server until it is stopped.
    """
    server = HTTPServer((HOST, PORT), SchedulingHandler)
    print(f"TCU Ambassador Scheduling System running at http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
