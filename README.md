# AROP: Autonomous Robot Orchestration and Task Management (v1.0 prototype)

A small web app that manages a fleet of **simulated** robots: register robots, create tasks, assign tasks (by hand or automatically), run a simulation, and watch the fleet on a dashboard. No physical robot is used.

## What is built

| Feature | Status |
| --- | --- |
| Admin login and logout | Built |
| Register robots (name only) and remove robots | Built |
| View robots, status, battery, location | Built |
| Create tasks with priority (low, medium, high) | Built |
| Manual task assignment | Built |
| Automatic task allocation | Built |
| Simulation (one step per button click) | Built, simplified (see limits) |
| Battery drain, charging | Built |
| Task completion tracking | Built |
| Activity logs | Built |
| Fleet dashboard | Built |
| Task report | Built |

## What is not built

- Editing a robot or a task after it is created
- Deleting a task
- Robot capabilities in allocation (allocation uses status, battery and priority only)
- Continuous or timed simulation (each click of the button runs one step)
- Real map or coordinates (location is only `Base` or `Task site`)
- Report export (CSV or PDF)
- CSRF protection on forms
- Local time in logs (times are shown in UTC)

## How it works

- Backend: Python, Flask. Database: SQLite (`arop.db`, created locally, not stored in Git).
- Tables: `admin`, `robots`, `tasks`, `activity_logs`.
- Manual assignment and automatic allocation use the same rules: the task must be `pending`, the robot must be `idle`, and the robot battery must be 20% or more.
- Automatic allocation takes pending tasks in order (high, then medium, then low, older first) and gives each one the idle robot with the most battery. It stops when no robot is free.
- Simulation step:
  - an `assigned` task becomes `in_progress`, the robot moves to `Task site`, battery drops 5%
  - an `in_progress` task becomes `completed`, the robot returns to `Base`, battery drops 10%
  - a robot under 20% battery goes to `charging`
  - a charging robot gains 20% per step and becomes `idle` at 50% or more
  - battery stays between 0 and 100

## Run it (Windows)

Tested on Windows 10 with Python 3.11.9. Run these commands one by one:

    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    python seed.py
    python create_admin.py
    python app.py

Then open http://127.0.0.1:5000 and log in.

- `seed.py` adds 3 **sample** robots (Robo-1, Robo-2, Robo-3). They are not real robots.
- `create_admin.py` asks for a username and a password. Only a password hash is stored. Choose a password you use nowhere else.
- Optional: set the environment variable `AROP_SECRET_KEY` to keep logins after a restart. If it is not set, a random key is made at each start, so you must log in again after a restart.
- `app.py` runs in Flask debug mode. This is for local development only.

## Tests

Run this command:

    pytest -q

Result on 10 Nov 2026 (Python 3.11.9, pytest 9.2.0):

    26 passed in 4.06s

The tests use a throwaway database, never `arop.db`. They cover login and logout, the 20% battery limit, manual and automatic assignment, the simulation cycle, low-battery charging, and removing robots.

## Files

- `app.py`: pages and routes for robots and tasks
- `auth.py`: login, logout, page lock
- `simulation.py`: simulation steps
- `dashboard.py`, `reports.py`, `logs.py`: dashboard, report, activity log pages
- `database.py`: database connection and tables
- `seed.py`, `create_admin.py`: setup scripts
- `templates/`: HTML pages
- `tests/`, `pytest.ini`: tests
- `requirements.txt`: pinned packages

## AI assistance

This project was built step by step with an AI assistant (Claude). The code was typed or pasted by the author, run on the author's computer and checked by the tests above.

<!-- end of README -->