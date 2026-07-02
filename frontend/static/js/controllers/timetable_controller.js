import TimetableAPI from "../api/timetable_api.js";

// State
let sections = [];
let faculties = [];
let currentAcademicYear = "2025-2026";
let currentViewMode = "section"; // "section" or "faculty"
let selectedId = null;

// DOM Elements
const selectFilterLabel = document.getElementById("selectFilterLabel");
const targetSelect = document.getElementById("targetSelect");
const toggleSectionBtn = document.getElementById("toggleSectionBtn");
const toggleFacultyBtn = document.getElementById("toggleFacultyBtn");
const btnGenerate = document.getElementById("btnGenerate");
const btnClear = document.getElementById("btnClear");
const scheduleGridContainer = document.getElementById("scheduleGridContainer");

export async function init() {
    try {
        // Load options lists
        sections = await TimetableAPI.getSections(currentAcademicYear);
        faculties = await TimetableAPI.getFacultyList();

        // Bind toggle buttons
        setupViewToggles();

        // Populate dynamic select filter
        populateTargetSelect();

        // Load schedule grid
        await loadScheduleGrid();

        // Setup event handlers
        setupEventListeners();

        showToast("Success", "Timetable view initialized successfully!", "success");
    } catch (err) {
        console.error("Initialization error:", err);
        showToast("Error", "Failed to load scheduling helpers", "danger");
    }
}

function setupViewToggles() {
    if (!toggleSectionBtn || !toggleFacultyBtn) return;
    
    toggleSectionBtn.addEventListener("click", () => {
        currentViewMode = "section";
        toggleSectionBtn.classList.add("active");
        toggleFacultyBtn.classList.remove("active");
        selectFilterLabel.textContent = "Select Section:";
        populateTargetSelect();
        loadScheduleGrid();
    });

    toggleFacultyBtn.addEventListener("click", () => {
        currentViewMode = "faculty";
        toggleFacultyBtn.classList.add("active");
        toggleSectionBtn.classList.remove("active");
        selectFilterLabel.textContent = "Select Faculty Member:";
        populateTargetSelect();
        loadScheduleGrid();
    });
}

function populateTargetSelect() {
    if (!targetSelect) return;
    
    if (currentViewMode === "section") {
        targetSelect.innerHTML = sections.map(sec => `
            <option value="${sec.section_id}">${sec.section_name} (Sem ${sec.semester})</option>
        `).join("");
        if (sections.length > 0) {
            targetSelect.value = sections[0].section_id;
        }
    } else {
        targetSelect.innerHTML = faculties.map(fac => `
            <option value="${fac.faculty_id}">${fac.first_name} ${fac.last_name} (${fac.employee_code})</option>
        `).join("");
        if (faculties.length > 0) {
            targetSelect.value = faculties[0].faculty_id;
        }
    }
}

async function loadScheduleGrid() {
    if (!scheduleGridContainer) return;
    
    selectedId = targetSelect.value;
    if (!selectedId) {
        scheduleGridContainer.innerHTML = `
            <div class="text-center py-5 text-muted">
                <i class="bi bi-calendar3 fs-1 d-block mb-3 opacity-50"></i>
                Please select a section or faculty member to view timetable.
            </div>
        `;
        return;
    }

    try {
        const filters = { academic_year: currentAcademicYear };
        if (currentViewMode === "section") {
            filters.section_id = selectedId;
        } else {
            filters.faculty_id = selectedId;
        }

        const rawTimetable = await TimetableAPI.get(filters);
        renderWeeklyGrid(rawTimetable);
    } catch (err) {
        showToast("Error", err.message, "danger");
    }
}

function renderWeeklyGrid(entries) {
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const maxPeriods = 4; // Display 4 periods as mapped in sample data

    // Group entries by day and slot order
    const gridMap = {};
    entries.forEach(entry => {
        const key = `${entry.day_of_week}_${entry.slot_order}`;
        gridMap[key] = entry;
    });

    let gridHtml = `
        <div class="table-responsive">
            <table class="table table-bordered table-dark align-middle text-center" style="border-color: rgba(255,255,255,0.08);">
                <thead>
                    <tr class="table-dark-header">
                        <th style="width: 120px;">Day</th>
                        <th>Period 1<br><small class="text-muted">09:00 - 10:00</small></th>
                        <th>Period 2<br><small class="text-muted">10:00 - 11:00</small></th>
                        <th style="background: rgba(255,255,255,0.02); width: 60px;">Break<br><small class="text-muted">15m</small></th>
                        <th>Period 3<br><small class="text-muted">11:15 - 12:15</small></th>
                        <th>Period 4<br><small class="text-muted">12:15 - 01:15</small></th>
                    </tr>
                </thead>
                <tbody>
    `;

    days.forEach(day => {
        gridHtml += `<tr>`;
        gridHtml += `<td class="fw-bold text-indigo bg-dark-day">${day}</td>`;

        for (let order = 1; order <= maxPeriods; order++) {
            // Add lunch break column after period 2
            if (order === 3) {
                gridHtml += `<td class="bg-break text-muted fw-light">Break</td>`;
            }

            const entry = gridMap[`${day}_${order}`];
            if (entry) {
                const roomInfo = entry.room 
                    ? `<span class="badge bg-secondary mt-1">${entry.room.room_number}</span>`
                    : "";
                    
                const subtitle = currentViewMode === "section"
                    ? `<small class="text-muted d-block">${entry.faculty_name}</small>`
                    : `<small class="text-muted d-block">Sec: ${entry.section_name}</small>`;

                gridHtml += `
                    <td class="p-3">
                        <div class="card card-glass p-2 border-light-subtle shadow-sm transition-all hover-scale-sm">
                            <span class="fw-bold text-white-85">${entry.course_code}</span>
                            <small class="text-white-70">${entry.course_name}</small>
                            ${subtitle}
                            ${roomInfo}
                        </div>
                    </td>
                `;
            } else {
                gridHtml += `<td class="text-muted py-4 fw-light opacity-25">Free Period</td>`;
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
    // Select filter changes
    targetSelect.addEventListener("change", () => loadScheduleGrid());

    // Generate Timetable button click
    if (btnGenerate) {
        btnGenerate.addEventListener("click", async () => {
            // Show loading animation on button
            const originalHtml = btnGenerate.innerHTML;
            btnGenerate.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Solving CSP...`;
            btnGenerate.disabled = true;

            try {
                const res = await TimetableAPI.generate(currentAcademicYear);
                showToast("Success", res.message, "success");
                await refreshSectionsAndFaculty();
                await loadScheduleGrid();
            } catch (err) {
                showToast("Constraint Conflict", err.message, "danger");
            } finally {
                btnGenerate.innerHTML = originalHtml;
                btnGenerate.disabled = false;
            }
        });
    }

    // Clear Timetable button click
    if (btnClear) {
        btnClear.addEventListener("click", async () => {
            if (!confirm("Are you sure you want to clear the entire timetable? All allocations will be lost.")) return;
            try {
                await TimetableAPI.clear(currentAcademicYear);
                showToast("Success", "Timetable cleared successfully", "success");
                await loadScheduleGrid();
            } catch (err) {
                showToast("Error", err.message, "danger");
            }
        });
    }
}

async function refreshSectionsAndFaculty() {
    sections = await TimetableAPI.getSections(currentAcademicYear);
    faculties = await TimetableAPI.getFacultyList();
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
    }, 5000);
}
