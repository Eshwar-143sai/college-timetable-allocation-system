import TimetableAPI from "../api/timetable_api.js";

// State
let sections = [];
let faculties = [];
let classrooms = [];
let laboratories = [];
let currentAcademicYear = "2025-2026";
let currentViewMode = "section"; // "section" | "faculty" | "classroom" | "laboratory"
let selectedId = null;

// DOM Elements
const selectFilterLabel = document.getElementById("selectFilterLabel");
const targetSelect = document.getElementById("targetSelect");
const toggleSectionBtn = document.getElementById("toggleSectionBtn");
const toggleFacultyBtn = document.getElementById("toggleFacultyBtn");
const toggleClassroomBtn = document.getElementById("toggleClassroomBtn");
const toggleLabBtn = document.getElementById("toggleLabBtn");
const btnGenerate = document.getElementById("btnGenerate");
const btnClear = document.getElementById("btnClear");
const btnPrint = document.getElementById("btnPrint");
const scheduleGridContainer = document.getElementById("scheduleGridContainer");

export async function init() {
    try {
        // Load helpers
        sections = await TimetableAPI.getSections(currentAcademicYear);
        faculties = await TimetableAPI.getFacultyList();
        classrooms = await TimetableAPI.getClassrooms();
        laboratories = await TimetableAPI.getLaboratories();

        // Bind toggles
        setupViewToggles();

        // Populate selects
        populateTargetSelect();

        // Load grid
        await loadScheduleGrid();

        // Event handlers
        setupEventListeners();

        showToast("Success", "Dynamic Weekly Schedule Grid initialized!", "success");
    } catch (err) {
        console.error("Initialization error:", err);
        showToast("Error", "Failed to load scheduling assets", "danger");
    }
}

function setupViewToggles() {
    const buttons = [
        { btn: toggleSectionBtn, mode: "section", label: "Select Section:" },
        { btn: toggleFacultyBtn, mode: "faculty", label: "Select Faculty Member:" },
        { btn: toggleClassroomBtn, mode: "classroom", label: "Select Classroom:" },
        { btn: toggleLabBtn, mode: "laboratory", label: "Select Laboratory:" }
    ];

    buttons.forEach(item => {
        if (!item.btn) return;
        item.btn.addEventListener("click", () => {
            currentViewMode = item.mode;
            
            // Set active class
            buttons.forEach(b => b.btn?.classList.remove("active"));
            item.btn.classList.add("active");
            
            selectFilterLabel.textContent = item.label;
            populateTargetSelect();
            loadScheduleGrid();
        });
    });
}

function populateTargetSelect() {
    if (!targetSelect) return;
    
    if (currentViewMode === "section") {
        targetSelect.innerHTML = sections.map(sec => `
            <option value="${sec.section_id}">${sec.section_name} (Semester ${sec.semester})</option>
        `).join("");
        if (sections.length > 0) targetSelect.value = sections[0].section_id;
    } else if (currentViewMode === "faculty") {
        targetSelect.innerHTML = faculties.map(fac => `
            <option value="${fac.faculty_id}">${fac.first_name} ${fac.last_name} (${fac.employee_code})</option>
        `).join("");
        if (faculties.length > 0) targetSelect.value = faculties[0].faculty_id;
    } else if (currentViewMode === "classroom") {
        targetSelect.innerHTML = classrooms.map(r => `
            <option value="${r.classroom_id}">${r.room_number} (Cap: ${r.capacity})</option>
        `).join("");
        if (classrooms.length > 0) targetSelect.value = classrooms[0].classroom_id;
    } else {
        targetSelect.innerHTML = laboratories.map(l => `
            <option value="${l.lab_id}">${l.lab_number} (${l.lab_type})</option>
        `).join("");
        if (laboratories.length > 0) targetSelect.value = laboratories[0].lab_id;
    }
}

async function loadScheduleGrid() {
    if (!scheduleGridContainer) return;
    
    selectedId = targetSelect.value;
    if (!selectedId) {
        scheduleGridContainer.innerHTML = `
            <div class="text-center py-5 text-muted">
                <i class="bi bi-calendar3 fs-1 d-block mb-3 opacity-50"></i>
                Select a target filter to view schedule.
            </div>
        `;
        return;
    }

    try {
        const filters = { academic_year: currentAcademicYear };
        if (currentViewMode === "section") {
            filters.section_id = selectedId;
        } else if (currentViewMode === "faculty") {
            filters.faculty_id = selectedId;
        } else if (currentViewMode === "classroom") {
            filters.classroom_id = selectedId;
        } else {
            filters.lab_id = selectedId;
        }

        const rawTimetable = await TimetableAPI.get(filters);
        renderWeeklyGrid(rawTimetable);
    } catch (err) {
        showToast("Error", err.message, "danger");
    }
}

function renderWeeklyGrid(entries) {
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
    const maxPeriods = 8;

    // Group entries by day and slot order
    const gridMap = {};
    entries.forEach(entry => {
        const key = `${entry.day_of_week}_${entry.slot_order}`;
        gridMap[key] = entry;
    });

    // Time slot order display text mapping
    const slotTimes = {
        1: "09:00 - 10:00",
        2: "10:00 - 11:00",
        3: "11:00 - 12:00",
        4: "12:00 - 01:00",
        5: "02:00 - 03:00",
        6: "03:00 - 04:00",
        7: "04:00 - 05:00",
        8: "05:00 - 06:00"
    };

    let gridHtml = `
        <div class="table-responsive printable-table-container">
            <table class="table table-bordered table-dark align-middle text-center" style="border-color: rgba(255,255,255,0.08); font-size: 0.85rem;">
                <thead>
                    <tr class="table-dark-header">
                        <th style="width: 110px;">Day</th>
                        ${[1, 2, 3, 4].map(idx => `
                            <th>P${idx}<br><small class="text-white-50">${slotTimes[idx]}</small></th>
                        `).join("")}
                        <th style="background: rgba(255, 255, 255, 0.02); width: 50px;" class="lunch-break-header">Lunch Break<br><small class="text-white-50">1h</small></th>
                        ${[5, 6, 7, 8].map(idx => `
                            <th>P${idx}<br><small class="text-white-50">${slotTimes[idx]}</small></th>
                        `).join("")}
                    </tr>
                </thead>
                <tbody>
    `;

    days.forEach(day => {
        gridHtml += `<tr>`;
        gridHtml += `<td class="fw-bold text-indigo bg-dark-day py-4" style="font-size: 0.9rem;">${day}</td>`;

        for (let order = 1; order <= maxPeriods; order++) {
            // Render lunch break column after period 4
            if (order === 5) {
                gridHtml += `<td class="bg-break text-muted fw-bold align-middle vertical-text py-3 opacity-50" style="letter-spacing: 2px;">LUNCH</td>`;
            }

            const entry = gridMap[`${day}_${order}`];
            if (entry) {
                // Determine color coding based on course type
                let colorClass = "timetable-theory";
                if (entry.course_type === "Lab") {
                    colorClass = "timetable-lab";
                } else if (entry.course_type === "Tutorial") {
                    colorClass = "timetable-tutorial";
                }

                const roomNum = entry.room ? entry.room.room_number : "TBD";
                
                // Construct labels depending on view mode
                let detailLine = "";
                if (currentViewMode === "section") {
                    detailLine = `<small class="text-white-50 d-block">${entry.faculty_name}</small>`;
                } else if (currentViewMode === "faculty") {
                    detailLine = `<small class="text-white-50 d-block">Sec: ${entry.section_name}</small>`;
                } else {
                    detailLine = `<small class="text-white-50 d-block">Sec: ${entry.section_name} | ${entry.faculty_name}</small>`;
                }

                gridHtml += `
                    <td class="p-1" style="min-width: 110px;">
                        <div class="card ${colorClass} p-2 h-100 text-start border-0 shadow-sm">
                            <span class="fw-bold text-white mb-0" style="font-size: 0.85rem;">${entry.course_code}</span>
                            <span class="text-white-70 truncate d-block mb-1" style="font-size: 0.75rem;" title="${entry.course_name}">${entry.course_name}</span>
                            ${detailLine}
                            <span class="badge bg-dark-subtle text-white-70 mt-1 d-inline-block w-fit" style="font-size: 0.7rem;">
                                <i class="bi bi-geo-alt-fill me-1"></i>${roomNum}
                            </span>
                        </div>
                    </td>
                `;
            } else {
                gridHtml += `<td class="text-white-30 py-4 fw-light opacity-20 small">No Class</td>`;
            }
        }
        gridHtml += `</tr>`;
    });

    gridHtml += `
                </tbody>
            </table>
        </div>
    `;

    scheduleGridContainer.innerHTML = gridHtml;
}

function setupEventListeners() {
    targetSelect.addEventListener("change", () => loadScheduleGrid());

    if (btnGenerate) {
        btnGenerate.addEventListener("click", async () => {
            const originalHtml = btnGenerate.innerHTML;
            btnGenerate.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Running Engine...`;
            btnGenerate.disabled = true;

            try {
                const res = await TimetableAPI.generate(currentAcademicYear);
                showToast("Success", res.message, "success");
                await refreshFilters();
                await loadScheduleGrid();
            } catch (err) {
                showToast("Constraint Violation", err.message, "danger");
            } finally {
                btnGenerate.innerHTML = originalHtml;
                btnGenerate.disabled = false;
            }
        });
    }

    if (btnClear) {
        btnClear.addEventListener("click", async () => {
            if (!confirm("Are you sure you want to delete all entries?")) return;
            try {
                await TimetableAPI.clear(currentAcademicYear);
                showToast("Success", "Timetable cleared", "success");
                await loadScheduleGrid();
            } catch (err) {
                showToast("Error", err.message, "danger");
            }
        });
    }

    // Trigger Browser Print Dialog
    if (btnPrint) {
        btnPrint.addEventListener("click", () => {
            window.print();
        });
    }
}

async function refreshFilters() {
    sections = await TimetableAPI.getSections(currentAcademicYear);
    faculties = await TimetableAPI.getFacultyList();
    classrooms = await TimetableAPI.getClassrooms();
    laboratories = await TimetableAPI.getLaboratories();
    populateTargetSelect();
}

function showToast(title, message, type = "info") {
    let container = document.getElementById("toastContainer");
    if (!container) {
        container = document.createElement("div");
        container.id = "toastContainer";
        container.className = "toast-container position-fixed bottom-0 end-0 p-3";
        document.body.appendChild(container);
    }

    const toastHtml = `
        <div class="toast align-items-center text-white bg-${type} border-0 shadow-lg show" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <strong class="d-block">${title}</strong>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;

    const tempDiv = document.createElement("div");
    tempDiv.innerHTML = toastHtml.trim();
    const toastEl = tempDiv.firstChild;
    container.appendChild(toastEl);

    setTimeout(() => {
        toastEl.remove();
    }, 4000);
}
