# TCU Ambassador Scheduling System

A role-based scheduling application for TCU Admissions ambassadors and administrators.

## Screens

- Email-based login for admin and ambassador views during development.
- Ambassador dashboard with upcoming assignments and notifications.
- Availability module with a weekly drafting view and dashboard grid.
- Profile management for academic information and personality traits.
- Admin dashboard for tours, assignments, and ambassador roster management.

The application supports a connected workflow for adding records, filtering and searching data, updating ambassador information, and generating a workload report from the same admin and ambassador pages.

## Architecture

The codebase is split into small modules instead of one large file:

- `app/main.py` contains the HTTP server entry point and request handler.
- `app/queries.py` contains database and business-logic helpers.
- `app/utils.py` contains rendering and response helpers.
- `app/database.py` contains the SQLite connection setup.

This structure keeps the user interface separate from the data-handling logic where practical. The main program file has a top-level `main()` function, the application includes a class with methods in the request handler, and the Python code follows standard naming conventions without using `break`, `continue`, or loop `else` statements.

## Run

```bash
python app/main.py
```

Then open `http://127.0.0.1:8000`.