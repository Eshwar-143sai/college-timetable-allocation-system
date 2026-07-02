# Installation Guide
## College Timetable Allocation System

Follow these steps to set up, configure, and run the College Timetable Allocation System locally.

---

## 1. Prerequisites

Ensure you have the following installed on your machine:
* **Python 3.10 or 3.11** (Verify with `python --version`)
* **MySQL Server (v8.0+)** (Verify with `mysql --version`)
* **Git** (optional)

---

## 2. Project Directory Setup

Clone or copy the project files to your local directory. The workspace structure looks like this:
```
college-timetable-allocation-system/
├── backend/          # FastAPI REST Backend
├── frontend/         # HTML/CSS/JS Static Client Web Application
├── database/         # SQL Initialization and Seed Files
└── venv/             # Python Virtual Environment
```

---

## 3. Database Setup

1. Open your MySQL Command Line Client or tool (e.g., MySQL Workbench, phpMyAdmin).
2. Create a new database named `timetable_db`:
   ```sql
   CREATE DATABASE timetable_db;
   ```
3. Run the SQL schema and data seed scripts located in the `database/` folder:
   * **Schema Creation**: Open and execute [schema.sql](file:///C:/Users/saies/.gemini/antigravity/scratch/college-timetable-allocation-system/database/schema.sql). This creates the users, departments, faculty, sections, courses, rooms, time slots, and timetable tables.
   * **Data Seeding**: Open and execute [seed_data.sql](file:///C:/Users/saies/.gemini/antigravity/scratch/college-timetable-allocation-system/database/seed_data.sql). This registers standard semesters, 8 sections (A-H), classrooms (8 classrooms, 4 labs), courses, and initial coordinator accounts.

---

## 4. Backend Configuration & Setup

1. Open a PowerShell terminal in the `backend/` directory:
   ```powershell
   cd backend
   ```
2. Create a python virtual environment:
   ```powershell
   python -m venv venv
   ```
3. Activate the virtual environment:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```
4. Install python dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
5. Install optional test and export libraries:
   ```powershell
   pip install reportlab openpyxl pytest httpx bcrypt
   ```
6. Configure environment variables. Rename `.env.example` to `.env` and adjust the MySQL details:
   ```env
   DB_HOST=127.0.0.1
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_NAME=timetable_db
   ```

---

## 5. Starting the Application

### 5.1 Run the Backend API Server
1. From the virtual-env-activated terminal inside `backend/`, start uvicorn:
   ```powershell
   uvicorn app.main:app --reload --port 8000
   ```
2. The interactive API documentation will be available at:
   * Swagger Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   * Redoc Docs: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### 5.2 Run the Frontend UI Client
1. The frontend consists of static files. You can open [frontend/public/dashboard.html](file:///C:/Users/saies/.gemini/antigravity/scratch/college-timetable-allocation-system/frontend/public/dashboard.html) directly in any web browser!
2. To avoid CORS warnings and support full routing, run a local web server in the project directory using python:
   ```powershell
   python -m http.server 8080
   ```
3. Open your browser and navigate to: [http://localhost:8080/frontend/public/dashboard.html](http://localhost:8080/frontend/public/dashboard.html).

---

## 6. Running Automated Tests

Verify that your installation is correct by running the full testing suite:
```powershell
$env:PYTHONPATH="backend"
.\venv\Scripts\pytest backend/tests/
```
All 16 test cases should pass successfully.
