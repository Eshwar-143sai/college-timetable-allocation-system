const STATS_URL = "http://127.0.0.1:8000/api/v1/timetable/stats";
const TIMETABLE_URL = "http://127.0.0.1:8000/api/v1/timetable";

const DashboardAPI = {
    async getStats(academicYear = "2025-2026") {
        const response = await fetch(`${STATS_URL}?academic_year=${encodeURIComponent(academicYear)}`);
        if (!response.ok) {
            throw new Error("Failed to load dashboard statistics");
        }
        return await response.json();
    },

    async generate(academicYear = "2025-2026") {
        const response = await fetch(`${TIMETABLE_URL}/generate?academic_year=${encodeURIComponent(academicYear)}`, {
            method: "POST"
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to generate timetable");
        }
        return await response.json();
    },

    async clear(academicYear = "2025-2026") {
        const response = await fetch(`${TIMETABLE_URL}/clear?academic_year=${encodeURIComponent(academicYear)}`, {
            method: "DELETE"
        });
        if (!response.ok) {
            throw new Error("Failed to clear timetable database");
        }
        return true;
    }
};
export default DashboardAPI;
