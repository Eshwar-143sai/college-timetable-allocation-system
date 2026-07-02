# Software Requirements Specification (SRS)
## College Timetable Allocation System

---

## 1. Introduction

### 1.1 Purpose
This document specifies the Software Requirements Specification (SRS) for the **College Timetable Allocation System**. This system is an automated, web-based platform designed to dynamically schedule section timetables, resolve teacher-room allocations, and prevent structural conflicts using a Constraint Satisfaction solver.

### 1.2 Document Conventions
All requirements follow standard IEEE SRS guidelines:
* **MUST / SHALL**: Mandatory requirement.
* **SHOULD**: Highly recommended/expected feature.
* **MAY**: Optional or future-scope enhancement.

### 1.3 Intended Audience
This document is prepared for course coordinators, system administrators, developers, testers, and academic evaluators of this software engineering final-year project.

---

## 2. Overall Description

### 2.1 Product Perspective
The system operates on a modern split MVC architecture:
* **Frontend**: HTML5, CSS3 (Glassmorphism theme), Bootstrap 5, Javascript (ES6 modules).
* **Backend**: FastAPI REST framework.
* **Database**: MySQL relational database accessed via SQLAlchemy ORM.

```
+------------------+      REST APIs (HTTP)     +--------------------+
|  HTML5/CSS3/JS   | <=======================> |  FastAPI Backend   |
|   Frontend UI    |                           | (Python Services)  |
+------------------+                           +--------------------+
                                                         ||
                                                  SQLAlchemy ORM
                                                         ||
                                                         \/
                                               +--------------------+
                                               |   MySQL Database   |
                                               +--------------------+
```

### 2.2 Product Features
1. **Faculty Management**: CRUD operations, designation workload validation (Professor=12, Associate=14, Assistant=16, Lecturer=18 hours/week).
2. **Course Management**: CRUD operations, L-T-P-S-C credit hour allocations, and course type filters.
3. **Section Management**: CRUD operations for 8 sections (A-H), department tracks, and student count limits.
4. **Classroom Management**: Capacity tracking and type allocation checks (4 Laboratories, 8 Classrooms).
5. **Conflict Checker**: Evaluation rules for double bookings, capacity, course-type matches, and weekly workloads.
6. **Timetable Solver Engine**: Backtracking search with MRV (Minimum Remaining Values) heuristics.
7. **Reports & Exports**: Export metrics in CSV, Excel, and PDF formats, along with custom print stylesheets.

### 2.3 User Classes and Characteristics
* **System Administrator**: Can adjust reference system records (Classrooms, Slots, Users, Constraints) and force generate timetables.
* **HOD / Department Coordinator**: Can register courses, assign courses to faculty members, edit section details, and review workloads.
* **Faculty Members**: Can view their schedule, check scheduled hours, and download PDF rosters.

### 2.4 Design and Implementation Constraints
* **SQLite / MySQL Dialects**: The system must support MySQL in production and standard SQLite database engines for unit/integration testing.
* **Design Theme**: UI must be responsive, modern, and follow custom dark glassmorphic design rules.

---

## 3. System Requirements

### 3.1 Functional Requirements

#### FR-1: Faculty Scheduling Workload Limits
* The backend **MUST** restrict weekly workloads based on designation:
  * Professor: Maximum 12 hours.
  * Associate Professor: Maximum 14 hours.
  * Assistant Professor: Maximum 16 hours.
  * Lecturer: Maximum 18 hours.

#### FR-2: Class Allocation Type Checking
* Theory classes **MUST** be scheduled only in Rooms of type `Classroom`.
* Practical / Lab sessions **MUST** be scheduled only in Rooms of type `Laboratory`.

#### FR-3: Capacity Violations
* The system **SHALL** prevent scheduling a section in a room whose capacity is lower than the section's student strength.

#### FR-4: Double Booking Checks
* A faculty member, classroom, laboratory, or student section **MUST NOT** be scheduled for more than one class during any given time slot.

#### FR-5: Timetable solver engine
* The engine **MUST** dynamically generate conflict-free schedules using backtracking search with priority queue heuristics. It **SHALL NOT** use hardcoded timetables.

#### FR-6: CSV/Excel/PDF Exports
* The system **SHALL** provide downloads for generated tables in CSV, Excel (.xlsx), and PDF formats.

---

## 4. Non-Functional Requirements

### 4.1 Performance Requirements
* Timetable generation for 8 sections with 20+ courses **SHALL** complete within 5.0 seconds.
* API responses for report data **SHALL** resolve within 500ms.

### 4.2 Security Requirements
* Sensitive API endpoints (Wipe, Solve) **SHOULD** require user role authorization verification.
* Password credentials **MUST** be encrypted using bcrypt.

### 4.3 Portability & Compatibility
* The frontend UI **MUST** compile and layout consistently on Google Chrome, Mozilla Firefox, Safari, and Microsoft Edge.
* The system layout **MUST** remain responsive on mobile, tablet, and desktop formats.
