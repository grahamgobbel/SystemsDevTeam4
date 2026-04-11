# SystemsDevTeam4

Neeley School of Business academic advising dashboard built with Python and SQLite.

## What the app does

- Shows a student advising dashboard with a semester-by-semester major progression.
- Lets users search courses and filter by completion status.
- Displays requirement progress, alerts, shortcuts, and help content in one layout.
- Seeds demo advising data automatically the first time the app runs.

## Project Structure

- `app/main.py`: Standard-library web server and route handling.
- `app/database.py`: SQLite connection helper for `data/SQLite.db`.
- `app/queries.py`: Database schema creation, demo seed data, and dashboard queries.
- `app/utils.py`: HTML rendering helpers for the dashboard.
- `app/static/styles.css`: Styling for the Figma-inspired interface.
- `data/`: Stores the SQLite database file created at runtime.
- `requirements.txt`: Kept minimal because the project uses the Python standard library.

## Run Locally

1. Start the app:
   `python app/main.py`
2. Open `http://127.0.0.1:8000` in your browser.

## Notes

- The current data is sample data for a Neeley advising use case.
- The visual design is intentionally similar to a Figma dashboard layout, but the repo is now focused on a working application rather than a direct Figma export.