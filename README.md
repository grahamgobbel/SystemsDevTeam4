# SystemsDevTeam4

A beginner-friendly Python + SQLite starter project, ready to open and run
in [GitHub Codespaces](https://github.com/features/codespaces).

---

## Project Structure

```
project-root/
├── app/
│   ├── main.py       # Entry point — run this file to start the project
│   ├── database.py   # SQLite connection helper
│   ├── queries.py    # Database query functions
│   └── utils.py      # General-purpose helper functions
├── data/
│   └── SQLite.db     # Created automatically at runtime (not committed)
├── requirements.txt  # Python dependencies (none needed beyond stdlib)
├── README.md         # This file
└── .devcontainer/
    ├── devcontainer.json   # Codespaces / VS Code Dev Container config
    └── Dockerfile          # Container image definition
```

---

## What Each File Does

| File | Purpose |
|------|---------|
| `app/main.py` | Entry point. Opens the database, seeds sample data, and prints results to stdout. |
| `app/database.py` | Provides `get_connection()` which opens (and auto-creates) `data/SQLite.db`. |
| `app/queries.py` | Contains reusable functions: `create_users_table`, `insert_user`, `get_all_users`, `get_user_by_id`. |
| `app/utils.py` | Helpers: `format_user`, `current_timestamp`, `print_section`. |
| `data/SQLite.db` | SQLite database file, created automatically the first time the project runs. |
| `requirements.txt` | Lists pip dependencies. Only stdlib is used, so this is currently empty. |
| `.devcontainer/devcontainer.json` | Tells Codespaces which Docker image and VS Code extensions to use. |
| `.devcontainer/Dockerfile` | Defines the container: Python 3.12 + any system packages needed. |

---

## How to Run the Project in Codespaces

1. Open the repository on GitHub and click **Code → Open with Codespaces → New codespace**.
2. Wait for the container to build (first launch only — typically 1–2 minutes).
3. In the integrated terminal, run:

```bash
python app/main.py
```

You should see output similar to:

```
----------------------------------------
  SystemsDevTeam4 — Project Startup
----------------------------------------
  Started at: 2025-01-15 09:30:00

----------------------------------------
  Connecting to database
----------------------------------------
  Connected to data/SQLite.db

----------------------------------------
  Seeding sample data
----------------------------------------
  Inserted 2 sample users

----------------------------------------
  All users
----------------------------------------
  [1] Alice Smith <alice@example.com>
  [2] Bob Jones <bob@example.com>

----------------------------------------
  Look up user id=1
----------------------------------------
  [1] Alice Smith <alice@example.com>

----------------------------------------
  Done
----------------------------------------
  Finished at: 2025-01-15 09:30:00
```

---

## Running Locally (without Codespaces)

Requires Python 3.10 or later (no extra packages needed):

```bash
python app/main.py
```

---

## Adding Dependencies

If you add third-party packages, list them in `requirements.txt` and install
them with:

```bash
pip install -r requirements.txt
```
