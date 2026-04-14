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
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from database import get_connection
from queries import (
    add_ambassador,
    add_availability_slot,
    add_tour,
    assign_ambassador_to_tour,
    build_admin_dashboard,
    build_ambassador_dashboard,
    build_availability_page,
    build_profile_page,
    clear_availability_slots,
    delete_ambassador,
    initialize_database,
    lookup_user,
    publish_tours,
    update_profile,
)
from utils import redirect_response, render_page, send_html, validation_message


STATIC_DIR = Path(__file__).resolve().parent / "static"
HOST = "127.0.0.1"
PORT = 8000


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
            elif parsed.path == "/ambassador/dashboard":
                user_id = self._require_user(params, "ambassador")
                body = render_page("ambassador_dashboard",
                                   build_ambassador_dashboard(conn, user_id))
            elif parsed.path == "/ambassador/availability":
                user_id = self._require_user(params, "ambassador")
                view = params.get("view", ["dashboard"])[0]
                body = render_page("availability", build_availability_page(
                    conn, user_id, view, params.get("message", [""])[0], params.get("error", [""])[0]))
            elif parsed.path == "/ambassador/profile":
                user_id = self._require_user(params, "ambassador")
                body = render_page("profile", build_profile_page(
                    conn, user_id, params.get("message", [""])[0], params.get("error", [""])[0]))
            elif parsed.path == "/admin":
                user_id = self._require_user(params, "admin")
                body = render_page("admin", build_admin_dashboard(
                    conn, user_id, params.get("message", [""])[0], params.get("error", [""])[0]))
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
                redirect = self._handle_login(conn, form)
            elif parsed.path == "/ambassador/availability":
                redirect = self._handle_availability(conn, form)
            elif parsed.path == "/ambassador/profile":
                redirect = self._handle_profile(conn, form)
            elif parsed.path == "/admin":
                redirect = self._handle_admin(conn, form)
            else:
                self.send_error(404, "Page not found")
                return
        finally:
            conn.close()

        redirect_response(self, redirect)

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

    def _require_user(self, params: dict, role: str) -> int:
        """Validate that the request includes the expected user context.

        Inputs:
            params: Parsed query-string values.
            role: Expected role for the page being viewed.
        Outputs:
            The validated user id.
        """
        user_id = int(params.get("user", ["0"])[0])
        expected = params.get("role", [role])[0]
        if user_id <= 0 or expected != role:
            raise PermissionError
        return user_id

    def _handle_login(self, conn, form: dict) -> str:
        """Authenticate a user and build the redirect target.

        Inputs:
            conn: Open database connection.
            form: Submitted login fields.
        Outputs:
            A redirect URL for the matching dashboard or an error page.
        """
        email = form.get("email", "").strip()
        role = form.get("role", "").strip().lower()

        if not email:
            return "/?error=" + validation_message("Enter an email address to continue.")

        user = lookup_user(conn, email, "", role)
        if not user:
            return "/?error=" + validation_message("Unable to open a dashboard for that email address.")

        if user["role"] == "admin":
            return f"/admin?user={user['id']}&role=admin&message=" + validation_message("Welcome back. Tour management is ready.")
        return f"/ambassador/dashboard?user={user['id']}&role=ambassador&message=" + validation_message("Welcome back. Your dashboard is up to date.")

    def _handle_availability(self, conn, form: dict) -> str:
        """Process ambassador availability actions and build a redirect URL.

        Inputs:
            conn: Open database connection.
            form: Submitted availability fields.
        Outputs:
            A redirect URL with success or error feedback.
        """
        user_id = int(form.get("user", "0"))
        action = form.get("action", "")
        role = "ambassador"

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
            return f"/ambassador/availability?user={user_id}&role={role}&view=weekly&{key}=" + validation_message(message)

        if action == "submit_availability":
            return f"/ambassador/availability?user={user_id}&role={role}&view=dashboard&message=" + validation_message("Availability submitted successfully.")

        if action == "clear_all":
            ok, message = clear_availability_slots(conn, user_id)
            key = "message" if ok else "error"
            return f"/ambassador/availability?user={user_id}&role={role}&view=weekly&{key}=" + validation_message(message)

        return f"/ambassador/availability?user={user_id}&role={role}&view=weekly&error=" + validation_message("Unknown availability action.")

    def _handle_profile(self, conn, form: dict) -> str:
        """Process ambassador profile updates and build a redirect URL.

        Inputs:
            conn: Open database connection.
            form: Submitted profile fields.
        Outputs:
            A redirect URL with feedback for the profile page.
        """
        user_id = int(form.get("user", "0"))
        ok, message = update_profile(
            conn,
            user_id,
            form.get("major", ""),
            form.get("minor", ""),
            form.get("year", ""),
            form.get("personality", ""),
        )
        key = "message" if ok else "error"
        return f"/ambassador/profile?user={user_id}&role=ambassador&{key}=" + validation_message(message)

    def _handle_admin(self, conn, form: dict) -> str:
        """Process admin actions and build a redirect URL.

        Inputs:
            conn: Open database connection.
            form: Submitted admin form fields.
        Outputs:
            A redirect URL with success or error feedback.
        """
        user_id = int(form.get("user", "0"))
        action = form.get("action", "")
        base = f"/admin?user={user_id}&role=admin"

        if action == "add_tour":
            ok, message = add_tour(
                conn,
                form.get("tour_type", ""),
                form.get("tour_date", ""),
                form.get("start_time", ""),
                form.get("end_time", ""),
                form.get("location", ""),
                int(form.get("ambassadors_needed", "1") or "1"),
            )
            return base + ("&message=" if ok else "&error=") + validation_message(message)

        if action == "assign_tour":
            ok, message = assign_ambassador_to_tour(
                conn, int(form.get("tour_id", "0")), int(form.get("ambassador_id", "0")))
            return base + ("&message=" if ok else "&error=") + validation_message(message)

        if action == "add_ambassador":
            ok, message = add_ambassador(
                conn,
                form.get("name", ""),
                form.get("email", ""),
                form.get("major", ""),
                form.get("year", ""),
            )
            return base + ("&message=" if ok else "&error=") + validation_message(message)

        if action == "delete_ambassador":
            ok, message = delete_ambassador(
                conn, int(form.get("ambassador_id", "0")))
            return base + ("&message=" if ok else "&error=") + validation_message(message)

        if action == "publish_tours":
            ok, message = publish_tours(conn)
            return base + ("&message=" if ok else "&error=") + validation_message(message)

        return base + "&error=" + validation_message("Unknown admin action.")


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
