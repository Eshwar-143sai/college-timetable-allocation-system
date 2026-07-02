# User Manual
## College Timetable Allocation System

Welcome to the User Manual for the **College Timetable Allocation System**. This guide walkthrough describes all modules, user interfaces, generation processes, and downloads.

---

## 1. Landing on the Admin Dashboard

When you open the application, you are greeted by the **Admin Dashboard**:
* **Summary Cards**:
  * *Faculty Count*: Displays total registered faculty members.
  * *Course Count*: Shows active courses in the curriculum.
  * *Section Count*: Total student cohorts (A-H).
  * *Today's Classes*: Scheduled contact sessions occurring today.
* **Syllabus Coverage Progress Bar**: Estimated semester contact progression.
* **Quick Action Controls**:
  * **Generate Timetable**: Solves the scheduling engine.
  * **Print Timetable**: Triggers print preview.
  * **Clear Engine**: Deletes active timetable assignments.
* **Weekly Allocation Chart**: Breakdown of Theory, Practical/Lab, and Tutorial sessions.
* **Faculty Workload Status List**: Shows current teaching hours for each coordinator.

---

## 2. Managing References (CRUD Modules)

Use the Sidebar links to navigate to reference management panels:

### 2.1 Faculty Management
* View all registered staff with designations, department tracks, and maximum allowed workload limits.
* **Add Faculty**: Click the "+ Add Faculty" button, fill in employee code, name, designation, and department to save.
* **Assign Subjects**: Link courses to teachers to tell the scheduler who is qualified to teach which course.

### 2.2 Course Management
* Setup courses with individual Lecture (L), Tutorial (T), Practical (P), and Self Study (S) hour splits.
* The system automatically computes credits as `Credits = L + T + (P / 2)`.

### 2.3 Section Management
* Manage 8 sections (A-H) detailing target semesters, student count capacities, and advisors.

### 2.4 Classrooms & Labs
* Register rooms specifying capacity limits (e.g. 70 seats) and type (`Classroom` or `Laboratory`).

---

## 3. Dynamic Scheduler Engine

1. Navigate to the **Timetable** section in the sidebar.
2. Filter the grid by **Section**, **Faculty**, or **Classroom/Lab**.
3. If no timetable exists, click **Solve Schedule**:
   * The backend will run the constraint backtracking algorithm.
   * If a solution is found, the page is populated with color-coded cards (Blue for Theory lectures, Emerald for Labs, and Purple for Tutorials).
   * If conflicts occur (e.g., too many courses for the available rooms), an error toast is displayed listing the violation details.
4. **Wipe Timetable**: Clears the schedules to re-allocate from scratch.

---

## 4. Reports, Analytics & Exports

1. Navigate to **Workload Reports** in the sidebar.
2. Review the aggregated widgets:
   * **Faculty Workloads Tracking Table**: Color-coded indicators indicating overload status (Red for >90% load, Green for target, Blue for under-load).
   * **Classroom & Lab Occupancy Rates**: Shows how busy each room is compared to the 40 slots/week capacity limit.
3. **Downloads**:
   * Export section timetables to CSV, Excel, or PDF.
   * Export overall workload report lists.
   * Export room occupancy lists.
   * Click **Print Reports** to output clean, print-friendly copies directly to paper.
