# College Timetable Allocation System
A final-year Software Engineering project for automated, conflict-free college timetable generation. Features a split MVC architecture with a FastAPI backend and a responsive dark-themed glassmorphic Bootstrap 5 frontend client.

---

## 🚀 Tech Stack

* **Frontend**: HTML5, CSS3, JavaScript (ES6 Modules), Bootstrap 5, Chart.js
* **Backend**: FastAPI (Python), SQLAlchemy ORM
* **Database**: MySQL (Production), SQLite (Testing)
* **Libraries**: ReportLab (PDF), Openpyxl (Excel), Pytest (Testing), Bcrypt (Security)

---

## 📂 Project Structure

```
college-timetable-allocation-system/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # REST Endpoint Routers
│   │   ├── auth/            # Hashing and Session Cryptography
│   │   ├── core/            # Configs & DB Sessions
│   │   ├── models/          # SQLAlchemy Database Models
│   │   ├── schemas/         # Pydantic Schemas
│   │   ├── scheduler/       # Backtracking Constraint Solver Engine
│   │   └── services/        # Conflict Checkers
│   └── tests/               # Pytest Testing Suites
├── frontend/
│   ├── public/              # View Templates (Dashboard, Timetables, Reports)
│   └── static/              # CSS Layouts & Page Controller Modules
├── database/                # Raw SQL schemas and seeding
└── docs/                    # Complete Project Documentation & UML diagrams
```

---

## 📖 Complete Documentation Index

Click the links below to view detailed specifications, setup procedures, and system designs:

1. **[Software Requirements Specification (SRS)](file:///C:/Users/saies/.gemini/antigravity/scratch/college-timetable-allocation-system/docs/SRS.md)**: Product scope, user classes, functional and non-functional requirements.
2. **[System Architecture & UML Diagrams](file:///C:/Users/saies/.gemini/antigravity/scratch/college-timetable-allocation-system/docs/UML_Diagrams.md)**: Includes **ER Diagram**, **Data Flow Diagram (DFD)**, **Use Case Diagram**, **Activity Diagram**, **Sequence Diagram**, and **Class Diagram** (rendered via Mermaid.js).
3. **[Installation Guide](file:///C:/Users/saies/.gemini/antigravity/scratch/college-timetable-allocation-system/docs/Installation_Guide.md)**: Setup, MySQL db seeding, Python dependencies installation, and local servers running.
4. **[User Manual](file:///C:/Users/saies/.gemini/antigravity/scratch/college-timetable-allocation-system/docs/User_Manual.md)**: Walking through CRUD panels, using the constraint solver, and exporting PDF/Excel reports.
5. **[Developer Guide](file:///C:/Users/saies/.gemini/antigravity/scratch/college-timetable-allocation-system/docs/Developer_Guide.md)**: Explains code organization, backtracking solver heuristics, and testing setup.
6. **[Deployment Guide](file:///C:/Users/saies/.gemini/antigravity/scratch/college-timetable-allocation-system/docs/Deployment_Guide.md)**: Setting up production Gunicorn daemon service and Nginx reverse proxies with SSL.
7. **[Future Scope](file:///C:/Users/saies/.gemini/antigravity/scratch/college-timetable-allocation-system/docs/Future_Scope.md)**: Artificial intelligence scheduling, calendar integrations, and multi-department upgrades.
8. **[Conclusion](file:///C:/Users/saies/.gemini/antigravity/scratch/college-timetable-allocation-system/docs/Conclusion.md)**: Brief project highlights and technical summary.

---

## ⚡ Quick Start

### 1. Database Seeding
Create `timetable_db` in MySQL and seed using the raw scripts:
* [schema.sql](file:///C:/Users/saies/.gemini/antigravity/scratch/college-timetable-allocation-system/database/schema.sql)
* [seed_data.sql](file:///C:/Users/saies/.gemini/antigravity/scratch/college-timetable-allocation-system/database/seed_data.sql)

### 2. Run Backend API
```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 3. Run Frontend
Open [dashboard.html](file:///C:/Users/saies/.gemini/antigravity/scratch/college-timetable-allocation-system/frontend/public/dashboard.html) in your browser!
