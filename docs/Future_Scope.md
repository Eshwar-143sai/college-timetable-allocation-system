# Future Scope & Extensions
## College Timetable Allocation System

The current system lays down a solid architectural base for automated scheduling. Below are targeted enhancements for future releases.

---

## 1. Advanced AI/ML Heuristics
* **Genetic Algorithms (GA)**: Transitioning or hybridizing the current backtracking engine with Genetic Algorithms. GA excels in optimizing soft-constraints (e.g., minimizing teachers' idle hours between classes, or balancing morning vs. afternoon lectures) across very large search spaces.
* **Reinforcement Learning (RL)**: Using RL agents to evaluate historical schedules and learn optimal scheduling pathways based on student-faculty feedback ratings.

---

## 2. Elective Courses & Student-Wise Tracking
* **Multicast Electives Scheduling**: Currently, sections schedule core courses together. Future releases will support elective slots where a single time slot schedules multiple different subjects across multiple classrooms, tracking individual student enrollment selections to prevent clashes.
* **Personalized Student Timetables**: Providing students with personalized calendar feeds (i.e. iCal/Google Calendar exports) showing their elective track classrooms.

---

## 3. Real-time Notifications & Calendar Integrations
* **Slack / WhatsApp Integrations**: Automatically pushing alerts to teachers and sections when temporary schedule changes occur.
* **Google Calendar API**: Synchronizing generation results directly into coordinators' college Google Workspace calendar slots.

---

## 4. Multi-Department Scalability & Load Balancing
* **Cross-Departmental Faculty Sharing**: Enhancing conflict detection to handle faculty members teaching across different departments (e.g., Physics department staff teaching first-year CSE students).
* **Enterprise Distributed Solver**: Deploying the constraint engine as a separate serverless worker task queue (e.g. Celery + Redis) to handle university-scale generates.
