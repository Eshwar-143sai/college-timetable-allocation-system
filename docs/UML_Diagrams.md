# System Architecture & UML Diagrams
## College Timetable Allocation System

Below is the complete set of system design models, entity relationships, and architectural diagrams rendered using Mermaid.

---

## 1. Entity-Relationship Diagram (ERD)

Shows database schemas, keys, and logical relationships between tables.

```mermaid
erDiagram
    users {
        int user_id PK
        string username
        string email
        string password_hash
        string role
        boolean is_active
    }
    departments {
        int department_id PK
        string department_name
        string department_code
    }
    faculty {
        int faculty_id PK
        int user_id FK
        string employee_code
        string first_name
        string last_name
        int department_id FK
        string designation
        int max_hours_per_week
    }
    sections {
        int section_id PK
        string section_name
        int department_id FK
        int semester
        string academic_year
        int student_strength
    }
    classrooms {
        int classroom_id PK
        string room_number
        string building
        int floor
        int capacity
        boolean has_projector
        boolean is_available
    }
    laboratories {
        int lab_id PK
        string lab_number
        string building
        int floor
        int capacity
        string lab_type
        boolean is_available
    }
    courses {
        int course_id PK
        string course_code
        string course_name
        string course_type
        int semester
        int department_id FK
        int ltpsc_id FK
    }
    ltpsc {
        int ltpsc_id PK
        int lecture_hours
        int tutorial_hours
        int practical_hours
        int self_study_hours
        int credits
    }
    time_slots {
        int slot_id PK
        string day_of_week
        time start_time
        time end_time
        int slot_order
    }
    timetable {
        int timetable_id PK
        int section_id FK
        int course_id FK
        int faculty_id FK
        int slot_id FK
        string academic_year
        int semester
    }
    room_allocations {
        int allocation_id PK
        int timetable_id FK
        string room_type
        int classroom_id FK
        int lab_id FK
    }
    constraints {
        int constraint_id PK
        string constraint_type
        int faculty_id FK
        int classroom_id FK
        int lab_id FK
        int slot_id FK
        string description
        boolean is_active
    }

    users ||--o| faculty : "has profile"
    departments ||--o{ faculty : "employs"
    departments ||--o{ sections : "offers"
    departments ||--o{ courses : "curates"
    courses ||--|| ltpsc : "defines credits"
    timetable ||--|| room_allocations : "reserves space"
    timetable }|--|| sections : "allocated for"
    timetable }|--|| courses : "teaches"
    timetable }|--|| faculty : "scheduled for"
    timetable }|--|| time_slots : "mapped to"
    room_allocations }|--o| classrooms : "classroom allocation"
    room_allocations }|--o| laboratories : "lab allocation"
    constraints }|--o| faculty : "restricts"
    constraints }|--o| classrooms : "restricts"
    constraints }|--o| laboratories : "restricts"
    constraints }|--o| time_slots : "applies during"
```

---

## 2. Data Flow Diagram (DFD) - Level 1

Shows the flow of data between external entities, backend services, and database stores.

```mermaid
graph TD
    User([Admin / Coordinator])
    UI[Frontend HTML/CSS/JS]
    API[FastAPI Router Gateway]
    Checker[Conflict Checker Module]
    Solver[Scheduler Solver Engine]
    DB[(MySQL / SQLite DB)]

    User -->|Input Form Actions| UI
    UI -->|AJAX Fetch Calls| API
    API -->|Fetch Reference Entities| DB
    DB -->|Read Data| API
    API -->|Query Conflicts| Checker
    Checker -->|Read Schedules / Constraints| DB
    DB -->|Active Bookings| Checker
    Checker -->|Validation Results| API
    
    API -->|Trigger Solve Timetable| Solver
    Solver -->|Iterative Solving| Checker
    Checker -->|Conflict Feedback| Solver
    Solver -->|Write Timetable Records| DB
    
    API -->|Generate CSV/Excel/PDF| UI
    UI -->|View Schedules & Reports| User
```

---

## 3. Use Case Diagram

Identifies actor tasks and capabilities in the system.

```mermaid
left_to_right_direction
gc[College Timetable System]
actor Admin as "Admin / HOD Coordinator"

rectangle gc {
    usecase UC1 as "Manage Reference Data (Faculty, Courses, Sections, Rooms)"
    usecase UC2 as "Assign Faculty to Courses"
    usecase UC3 as "Trigger Autogeneration Timetable Solver"
    usecase UC4 as "Review Weekly Schedule Grids"
    usecase UC5 as "Analyze Workloads & Room Utilizations"
    usecase UC6 as "Export reports (CSV, Excel, PDF)"
}

Admin --> UC1
Admin --> UC2
Admin --> UC3
Admin --> UC4
Admin --> UC5
Admin --> UC6
```

---

## 4. Activity Diagram

Visualizes the step-by-step workflow of generating a timetable.

```mermaid
stateDiagram-v2
    [*] --> LoadAssets : Click 'Solve Schedule'
    LoadAssets --> FetchEntities : Retrieve Active Sections, Courses, Faculty, Rooms, Slots
    FetchEntities --> PrepareQueue : Construct session blocks queue (Labs first, then Tutorials, then Theory)
    
    state SolverLoop {
        [*] --> SelectSession : Get next constrained session
        SelectSession --> FindSlotRoom : Identify candidate Slot and Room
        FindSlotRoom --> VerifyConstraints : Run Conflict Checker (Faculty, Section, Room, Workload, capacity)
        
        state Choice <<choice>>
        VerifyConstraints --> Choice
        Choice --> AssignCandidate : No Conflicts (Valid)
        Choice --> TryNextCandidate : Conflict Found (Invalid)
        
        AssignCandidate --> CheckMoreSessions : Save temp assignment
        TryNextCandidate --> CheckAlternative : Try next Room/Slot
        
        state BacktrackChoice <<choice>>
        CheckAlternative --> BacktrackChoice
        BacktrackChoice --> SelectSession : Alternate candidate found
        BacktrackChoice --> Rollback : No options left (Backtrack)
        
        Rollback --> SelectSession : Revert last assignment
    }
    
    CheckMoreSessions --> PersistToDB : All sessions allocated successfully
    PersistToDB --> UpdateWorkloads : Recalculate workloads and occupancy
    UpdateWorkloads --> [*] : Render complete weekly grid
```

---

## 5. Sequence Diagram

Illustrates message interactions for a timetable solving request.

```mermaid
sequenceDiagram
    autonumber
    actor Admin as Admin Coordinator
    participant UI as Browser UI (JS)
    participant API as FastAPI Backend
    participant Solver as TimetableScheduler
    participant Checker as ConflictChecker
    participant DB as SQL Database

    Admin->>UI: Click "Solve Schedule"
    UI->>API: POST /api/v1/timetable/generate
    activate API
    API->>Solver: Initialize (db, academic_year)
    activate Solver
    Solver->>DB: Fetch Courses, Sections, Rooms, Slots
    DB-->>Solver: Return entities
    Solver->>Solver: Build priority sessions queue
    
    loop For each session in queue
        Solver->>Solver: Select candidate Slot & Room
        Solver->>Checker: validate_timetable_entry(candidate_info)
        activate Checker
        Checker->>DB: Query double-bookings & constraints
        DB-->>Checker: Active assignments
        Checker-->>Solver: Return conflicts list (e.g. empty)
        deactivate Checker
    end
    
    Solver->>DB: save_timetable() (Bulk insert)
    DB-->>Solver: Confirm write
    Solver-->>API: Return Success (True)
    deactivate Solver
    API-->>UI: JSON Response { "message": "Timetable generated successfully!" }
    deactivate API
    UI->>UI: Refresh schedule grids and trigger Success Toast
    UI-->>Admin: Render color-coded weekly schedule grid
```

---

## 6. Class Diagram

Exposes the structure of system entities and scheduler classes.

```mermaid
classDiagram
    class Base {
        +metadata
    }
    class User {
        +int user_id
        +string username
        +string email
        +string password_hash
        +string role
    }
    class Faculty {
        +int faculty_id
        +string employee_code
        +string first_name
        +string last_name
        +string designation
        +int max_hours_per_week
    }
    class Course {
        +int course_id
        +string course_code
        +string course_name
        +string course_type
        +int semester
    }
    class Classroom {
        +int classroom_id
        +string room_number
        +int capacity
        +boolean is_available
    }
    class Laboratory {
        +int lab_id
        +string lab_number
        +int capacity
        +string lab_type
    }
    class TimeSlot {
        +int slot_id
        +string day_of_week
        +time start_time
        +time end_time
        +int slot_order
    }
    class Timetable {
        +int timetable_id
        +int section_id
        +int course_id
        +int faculty_id
        +int slot_id
        +string academic_year
    }
    class RoomAllocation {
        +int allocation_id
        +int timetable_id
        +string room_type
        +int classroom_id
        +int lab_id
    }
    class TimetableScheduler {
        +Session db
        +string academic_year
        +list sessions_to_schedule
        +list assignments
        +solve() boolean
        +save_timetable() void
    }

    Base <|-- User
    Base <|-- Faculty
    Base <|-- Course
    Base <|-- Classroom
    Base <|-- Laboratory
    Base <|-- TimeSlot
    Base <|-- Timetable
    Base <|-- RoomAllocation
    
    User "1" -- "1" Faculty : profile link
    Timetable "1" -- "1" RoomAllocation : locates in
    TimetableScheduler ..> Timetable : generates
    TimetableScheduler ..> RoomAllocation : allocates
```
