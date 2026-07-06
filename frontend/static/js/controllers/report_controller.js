import ReportAPI from "../api/report_api.js";
import { API_ROOT } from "../config.js";

// State
let academicYear = "2025-2026";
let weeklyStatsChart = null;
let roomUtilizationChart = null;

// DOM elements
const workloadTableBody = document.getElementById("workloadTableBody");
const roomTableBody = document.getElementById("roomTableBody");
const totalWeeklyClassesEl = document.getElementById("totalWeeklyClasses");
const projectedMonthlyHoursEl = document.getElementById("projectedMonthlyHours");
const syllabusCoverageEl = document.getElementById("syllabusCoverage");

export async function init() {
    try {
        await refreshReports();
        setupEventListeners();
        showToast("Success", "Workload & Utilization Reports loaded!", "success");
    } catch (err) {
        console.error("Reports loading error:", err);
        showToast("Error", "Failed to retrieve report data", "danger");
    }
}

async function refreshReports() {
    try {
        // Fetch reports data from backend
        const workloads = await ReportAPI.getWorkload(academicYear);
        const utilizations = await ReportAPI.getRoomUtilization(academicYear);
        const weeklyStats = await ReportAPI.getWeeklyStats(academicYear);
        const monthlyStats = await ReportAPI.getMonthlyStats(academicYear);

        // Render tables
        renderWorkloadTable(workloads);
        renderRoomTable(utilizations);

        // Populate card metrics
        if (totalWeeklyClassesEl) totalWeeklyClassesEl.textContent = weeklyStats.total_classes;
        if (projectedMonthlyHoursEl) projectedMonthlyHoursEl.textContent = `${monthlyStats.projected_monthly_contact_hours} hours`;
        if (syllabusCoverageEl) syllabusCoverageEl.textContent = `${monthlyStats.syllabus_coverage_estimate_percentage}% (Est)`;

        // Render chart visualizations
        renderWeeklyBreakdownChart(weeklyStats.breakdown);
        renderRoomUtilizationChart(utilizations);

    } catch (err) {
        showToast("Error", err.message, "danger");
    }
}

function renderWorkloadTable(workloads) {
    if (!workloadTableBody) return;
    
    if (workloads.length === 0) {
        workloadTableBody.innerHTML = `<tr><td colspan="4" class="text-center text-muted">No workloads recorded.</td></tr>`;
        return;
    }

    workloadTableBody.innerHTML = workloads.map(w => {
        const util = w.utilization_percentage;
        let progressColor = "bg-success";
        if (util > 90.0) {
            progressColor = "bg-danger"; // Overloaded
        } else if (util < 40.0) {
            progressColor = "bg-info";   // Underutilized
        }

        return `
            <tr class="align-middle border-bottom border-light-subtle transition-all hover-bg-light">
                <td>
                    <span class="fw-semibold text-white-85 d-block">${w.name}</span>
                    <small class="text-muted">Code: ${w.employee_code}</small>
                </td>
                <td><span class="badge badge-role">${w.designation}</span></td>
                <td><span class="fw-bold text-white-80">${w.scheduled_hours} / ${w.max_hours} hrs</span></td>
                <td style="width: 200px;">
                    <div class="d-flex align-items-center gap-2">
                        <div class="progress w-100" style="height: 8px; background: rgba(255,255,255,0.05);">
                            <div class="progress-bar ${progressColor}" role="progressbar" style="width: ${util}%;" aria-valuenow="${util}" aria-valuemin="0" aria-valuemax="100"></div>
                        </div>
                        <span class="text-white-70 small fw-bold">${util}%</span>
                    </div>
                </td>
            </tr>
        `;
    }).join("");
}

function renderRoomTable(utilizations) {
    if (!roomTableBody) return;

    if (utilizations.length === 0) {
        roomTableBody.innerHTML = `<tr><td colspan="5" class="text-center text-muted">No rooms utilization recorded.</td></tr>`;
        return;
    }

    roomTableBody.innerHTML = utilizations.map(u => {
        const util = u.utilization_percentage;
        let progressColor = "bg-success";
        if (util > 75.0) {
            progressColor = "bg-danger"; // High occupancy
        } else if (util < 25.0) {
            progressColor = "bg-info";   // Empty
        }

        return `
            <tr class="align-middle border-bottom border-light-subtle transition-all hover-bg-light">
                <td><strong class="text-white-85">${u.room_number}</strong></td>
                <td><span class="badge badge-dept">${u.room_type}</span></td>
                <td><span class="badge bg-secondary">${u.building}</span></td>
                <td><span class="text-white-80">${u.capacity} Seats</span></td>
                <td style="width: 180px;">
                    <div class="d-flex align-items-center gap-2">
                        <div class="progress w-100" style="height: 8px; background: rgba(255,255,255,0.05);">
                            <div class="progress-bar ${progressColor}" role="progressbar" style="width: ${util}%;" aria-valuenow="${util}" aria-valuemin="0" aria-valuemax="100"></div>
                        </div>
                        <span class="text-white-70 small fw-bold">${util}%</span>
                    </div>
                </td>
            </tr>
        `;
    }).join("");
}

function renderWeeklyBreakdownChart(breakdown) {
    const ctx = document.getElementById("weeklyBreakdownChart");
    if (!ctx) return;

    if (weeklyStatsChart) weeklyStatsChart.destroy();

    weeklyStatsChart = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Theory", "Practical/Lab", "Tutorial"],
            datasets: [{
                data: [breakdown.Theory, breakdown.Lab, breakdown.Tutorial],
                backgroundColor: [
                    "rgba(59, 130, 246, 0.6)", // Theory - Blue
                    "rgba(16, 185, 129, 0.6)", // Lab - Emerald
                    "rgba(139, 92, 246, 0.6)"  // Tutorial - Purple
                ],
                borderColor: [
                    "rgb(59, 130, 246)",
                    "rgb(16, 185, 129)",
                    "rgb(139, 92, 246)"
                ],
                borderWidth: 1.5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: { color: "#94a3b8", boxWidth: 12 }
                }
            }
        }
    });
}

function renderRoomUtilizationChart(rooms) {
    const ctx = document.getElementById("roomUtilizationChart");
    if (!ctx) return;

    if (roomUtilizationChart) roomUtilizationChart.destroy();

    // Sort rooms by occupancy percentage and get top 5
    const topRooms = [...rooms].sort((a, b) => b.utilization_percentage - a.utilization_percentage).slice(0, 5);
    const labels = topRooms.map(r => r.room_number);
    const data = topRooms.map(r => r.utilization_percentage);

    roomUtilizationChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Occupancy Percentage",
                data: data,
                backgroundColor: "rgba(20, 184, 166, 0.6)", // Teal
                borderColor: "rgb(20, 184, 166)",
                borderWidth: 1.5,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { color: "rgba(255, 255, 255, 0.05)" },
                    ticks: { color: "#94a3b8" }
                },
                y: {
                    grid: { color: "rgba(255, 255, 255, 0.05)" },
                    ticks: { color: "#94a3b8" }
                }
            }
        }
    });
}

function setupEventListeners() {
    const btnPrintReport = document.getElementById("btnPrintReport");
    if (btnPrintReport) {
        btnPrintReport.addEventListener("click", () => {
            window.print();
        });
    }

    // Faculty workload exports
    const fCSV = document.getElementById("btnFacultyExportCSV");
    const fExcel = document.getElementById("btnFacultyExportExcel");
    const fPDF = document.getElementById("btnFacultyExportPDF");

    if (fCSV) {
        fCSV.addEventListener("click", (e) => {
            e.preventDefault();
            window.location.href = `${API_ROOT}/api/v1/export/faculty/csv?academic_year=${encodeURIComponent(academicYear)}`;
        });
    }
    if (fExcel) {
        fExcel.addEventListener("click", (e) => {
            e.preventDefault();
            window.location.href = `${API_ROOT}/api/v1/export/faculty/excel?academic_year=${encodeURIComponent(academicYear)}`;
        });
    }
    if (fPDF) {
        fPDF.addEventListener("click", (e) => {
            e.preventDefault();
            window.location.href = `${API_ROOT}/api/v1/export/faculty/pdf?academic_year=${encodeURIComponent(academicYear)}`;
        });
    }

    // Room utilization exports
    const rCSV = document.getElementById("btnRoomExportCSV");
    const rExcel = document.getElementById("btnRoomExportExcel");
    const rPDF = document.getElementById("btnRoomExportPDF");

    if (rCSV) {
        rCSV.addEventListener("click", (e) => {
            e.preventDefault();
            window.location.href = `${API_ROOT}/api/v1/export/rooms/csv?academic_year=${encodeURIComponent(academicYear)}`;
        });
    }
    if (rExcel) {
        rExcel.addEventListener("click", (e) => {
            e.preventDefault();
            window.location.href = `${API_ROOT}/api/v1/export/rooms/excel?academic_year=${encodeURIComponent(academicYear)}`;
        });
    }
    if (rPDF) {
        rPDF.addEventListener("click", (e) => {
            e.preventDefault();
            window.location.href = `${API_ROOT}/api/v1/export/rooms/pdf?academic_year=${encodeURIComponent(academicYear)}`;
        });
    }
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
