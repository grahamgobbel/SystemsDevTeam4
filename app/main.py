"""
Standard-library web entry point for the Neeley School of Business advising dashboard.

Run with:
    python app/main.py
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from database import get_connection
from queries import get_dashboard_payload, initialize_database
from utils import render_dashboard_page


STATIC_DIR = Path(__file__).resolve().parent / "static"
HOST = "127.0.0.1"
PORT = 8000


class AdvisingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/":
            params = parse_qs(parsed.query)
            search_term = params.get("q", [""])[0].strip()
            status_filter = params.get("status", ["all"])[0].strip().lower() or "all"

            conn = get_connection()
            initialize_database(conn)
            dashboard = get_dashboard_payload(conn, search_term, status_filter)
            conn.close()

            body = render_dashboard_page(dashboard, search_term, status_filter)
            self._send_response(body.encode("utf-8"), "text/html; charset=utf-8")
            return

        if parsed.path == "/static/styles.css":
            css_bytes = (STATIC_DIR / "styles.css").read_bytes()
            self._send_response(css_bytes, "text/css; charset=utf-8")
            return

        self.send_error(404, "Page not found")

    def log_message(self, format, *args):
        return

    def _send_response(self, content: bytes, content_type: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), AdvisingHandler)
    print(f"Neeley advising dashboard running at http://{HOST}:{PORT}")
    server.serve_forever()