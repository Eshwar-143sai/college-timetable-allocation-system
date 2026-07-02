# Developer Guide
## College Timetable Allocation System

This guide explains the code structure, database models, scheduling solver engine, conflict detection, and testing suites.

---

## 1. Directory Structure

The project code is divided into a clean separation of concerns:
```
college-timetable-allocation-system/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # REST Endpoint Routers (faculty, courses, sections, rooms, timetable, reports, exports)
│   │   ├── auth/            # Cryptography & user session helpers (native bcrypt)
│   │   ├── core/            # Database and environment configurations
│   │   ├── database/        # Session and model registration initializers
│   │   ├── models/          # SQLAlchemy SQL models
│   │   ├── schemas/         # Pydantic validation schemas
│   │   ├── scheduler/       # Backtracking solver engine (constraint_solver.py)
│   │   └── services/        # Conflict evaluation checkers (conflict_checker.py)
│   │   └── main.py          # FastAPI application initialization entrypoint
│   └── tests/               # Pytest testing suites (test_auth, test_reports, test_scheduler, test_timetable)
└── frontend/
    ├── public/              # HTML layout documents
    └── static/              # CSS layouts & Vanilla JavaScript controllers/API clients
```

---

## 2. Database Models & Schema

The relational database is constructed in MySQL/SQLite via [Base](file:///C:/Users/saies/.gemini/antigravity/scratch/college-timetable-allocation-system/backend/app/database/base_class.py). Relational mapping models:
* **`User`**: Admin/HOD account records.
* **`Department`**: Branches (e.g. CSE).
* **`Faculty`**: Details employee code, name, designation, and links to the associated User.
* **`Section`**: Cohort tracking naming, strength size, and target semesters.
* **`Classroom` / `Laboratory`**: Location details, floor, building, and seat capacities.
* **`Course`**: Subject data linking to L-T-P splits.
* **`FacultySubject`**: Reference mapping connecting teachers to courses they are qualified to teach.
* **`TimeSlot`**: Days of the week (Monday-Friday) and orders (1-8).
* **`Timetable`**: Saved scheduled assignments mapping section, course, faculty, slot, and links to **`RoomAllocation`** (classroom or lab).

---

## 3. Conflict Detection Engine

The evaluation logic is defined in [conflict_checker.py](file:///C:/Users/saies/.gemini/antigravity/scratch/college-timetable-allocation-system/backend/app/services/conflict_checker.py):
* **`check_faculty_conflict`**: Queries if a teacher is double booked or is marked as unavailable during the slot.
* **`check_room_conflict`**: Checks if the classroom/lab is already booked in that period.
* **`check_section_conflict`**: Assures that a section isn't attending two lectures concurrently.
* **`check_daily_workload_violation`**: Restricts a teacher's total periods per day (default 6).
* **`check_weekly_workload_violation`**: Counts existing allocations for the faculty member in the timetable to verify their designation workload cap (Professor=12, Associate=14, Assistant=16, Lecturer=18 hours/week).
* **`check_lab_clash`**: Verifies that section strength is <= room capacity. It also checks type matching (Theory courses only in Classrooms, Practical/Lab courses only in Laboratories).
* **`check_credit_violation`**: Validates that a course is not scheduled for more hours than its combined L+T+P contact hours.

---

## 4. Backtracking Solver Algorithm

The core scheduling solver lies in [constraint_solver.py](file:///C:/Users/saies/.gemini/antigravity/backend/app/scheduler/constraint_solver.py):
* It compiles courses and sections that require scheduling.
* Unrolls the L-T-P hour requirements into individual sessions to schedule.
* **MRV Heuristic**: Prioritizes scheduling sessions with the fewest available slots first (e.g., Labs require laboratory rooms and double-period blocks, making them highly constrained).
* **Backtracking**: Assigns a session to a slot/room, checks for conflicts using the conflict checkers, and recurses. If a conflict occurs, it rolls back (backtracks) and tries the next candidate.

---

## 5. Running and Extending Tests

Automated tests are located in `backend/tests/`:
* **`test_auth.py`**: Verifies Native bcrypt hashing.
* **`test_timetable.py`**: Evaluates individual conflict checker methods (double bookings, workloads, type matching, capacity limits) in isolation.
* **`test_scheduler.py`**: Tests integration of the backtracking solver engine.
* **`test_reports.py`**: Tests FastAPI TestClient responses on analytics, report tables, and solver endpoints.
* **Running command**:
  ```powershell
  $env:PYTHONPATH="backend"
  .\venv\Scripts\pytest backend/tests/
  ```
