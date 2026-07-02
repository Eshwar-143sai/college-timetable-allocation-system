import DashboardAPI from "../api/dashboard_api.js";

// State
let currentAcademicYear = "2025-2026";
let myChart = null;

// DOM Elements
const facultyCountEl = document.getElementById("facultyCount");
const courseCountEl = document.getElementById("courseCount");
const sectionCountEl = document.getElementById("sectionCount");
const todayClassesEl = document.getElementById("todayClasses");
const todayDayEl = document.getElementById("todayDay");

const btnGenerate = document.getElementById("btnGenerate");
const btnClear = document.getElementById("btnClear");
const btnExportPdf = document.getElementById("btnExportPdf");
const btnExportExcel = document.getElementById("btnExportExcel");

export async function init() {
    try {
        await refreshDashboard();
        setupEventListeners();
        showToast("Success", "Dashboard loaded successfully!", "success");
    } catch (err) {
        console.error("Dashboard init error:", err);
        showToast("Error", "Failed to load dashboard metrics", "danger");
    }
}

async function refreshDashboard() {
    try {
        const stats = await DashboardAPI.getStats(currentAcademicYear);
        
        // Populate stats cards
        if (facultyCountEl) facultyCountEl.textContent = stats.faculty_count;
        if (courseCountEl) courseCountEl.textContent = stats.course_count;
        if (sectionCountEl) sectionCountEl.textContent = stats.section_count;
        if (todayClassesEl) todayClassesEl.textContent = stats.today_classes_count;
        if (todayDayEl) todayDayEl.textContent = `Today: ${stats.today_day_name}`;
        
        // Render or Update Department Distribution Chart
        renderChart(stats.dept_distribution);
    } catch (err) {
        showToast("Error", err.message, "danger");
    }
}

function renderChart(distribution) {
    const ctx = document.getElementById("deptChart");
    if (!ctx) return;

    // Convert map to labels and values
    // Mapped labels: 1 -> CSE, 2 -> ECE, 3 -> ME, etc.
    const deptLabels = {
        "1": "Computer Science (CSE)",
        "2": "Electronics (ECE)",
        "3": "Mechanical Eng (ME)",
        "4": "Civil Eng (CE)"
    };
    
    const labels = Object.keys(distribution).map(key => deptLabels[key] || `Dept ID ${key}`);
    const data = Object.values(distribution);

    if (myChart) {
        myChart.destroy();
    }

    // Chart.js Configuration
    myChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Registered Sections count",
                data: data,
                backgroundColor: [
                    "rgba(99, 102, 241, 0.6)", // Indigo
                    "rgba(139, 92, 246, 0.6)", // Violet
                    "rgba(236, 72, 153, 0.6)", // Pink
                    "rgba(20, 184, 166, 0.6)"   // Teal
                ],
                borderColor: [
                    "rgb(99, 102, 241)",
                    "rgb(139, 92, 246)",
                    "rgb(236, 72, 153)",
                    "rgb(20, 184, 166)"
                ],
                borderWidth: 1.5,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    grid: {
                        color: "rgba(255, 255, 255, 0.05)"
                    },
                    ticks: {
                        color: "#94a3b8"
                    }
                },
                y: {
                    grid: {
                        color: "rgba(255, 255, 255, 0.05)"
                    },
                    ticks: {
                        color: "#94a3b8",
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function setupEventListeners() {
    // Generate Timetable button trigger
    if (btnGenerate) {
        btnGenerate.addEventListener("click", async () => {
            const originalHtml = btnGenerate.innerHTML;
            btnGenerate.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Running Engine...`;
            btnGenerate.disabled = true;

            try {
                const res = await DashboardAPI.generate(currentAcademicYear);
                showToast("Success", res.message, "success");
                await refreshDashboard();
            } catch (err) {
                showToast("Constraint Violation", err.message, "danger");
            } finally {
                btnGenerate.innerHTML = originalHtml;
                btnGenerate.disabled = false;
            }
        });
    }

    // Clear Timetable database
    if (btnClear) {
        btnClear.addEventListener("click", async () => {
            if (!confirm("Wipe all timetable assignments? This cannot be undone.")) return;
            try {
                await DashboardAPI.clear(currentAcademicYear);
                showToast("Cleared", "Timetable wiped successfully.", "success");
                await refreshDashboard();
            } catch (err) {
                showToast("Error", err.message, "danger");
            }
        });
    }

    // Export PDF trigger
    if (btnExportPdf) {
        btnExportPdf.addEventListener("click", () => {
            showToast("Report Export", "Preparing PDF schedule report export...", "info");
            setTimeout(() => {
                window.location.href = "reports.html";
            }, 1000);
        });
    }

    // Export Excel trigger
    if (btnExportExcel) {
        btnExportExcel.addEventListener("click", () => {
            showToast("Report Export", "Preparing Excel utilization sheet export...", "info");
            setTimeout(() => {
                window.location.href = "reports.html";
            }, 1000);
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
