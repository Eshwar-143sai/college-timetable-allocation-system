const API_BASE_URL = "http://127.0.0.1:8000/api/v1/reports";

const ReportAPI = {
    async getWorkload(academicYear = "2025-2026") {
        const response = await fetch(`${API_BASE_URL}/workload?academic_year=${encodeURIComponent(academicYear)}`);
        if (!response.ok) {
            throw new Error("Failed to fetch faculty workload reports");
        }
        return await response.json();
    },

    async getRoomUtilization(academicYear = "2025-2026") {
        const response = await fetch(`${API_BASE_URL}/utilization?academic_year=${encodeURIComponent(academicYear)}`);
        if (!response.ok) {
            throw new Error("Failed to fetch room utilization reports");
        }
        return await response.json();
    },

    async getWeeklyStats(academicYear = "2025-2026") {
        const response = await fetch(`${API_BASE_URL}/weekly-stats?academic_year=${encodeURIComponent(academicYear)}`);
        if (!response.ok) {
            throw new Error("Failed to fetch weekly statistics");
        }
        return await response.json();
    },

    async getMonthlyStats(academicYear = "2025-2026") {
        const response = await fetch(`${API_BASE_URL}/monthly-stats?academic_year=${encodeURIComponent(academicYear)}`);
        if (!response.ok) {
            throw new Error("Failed to fetch monthly projections");
        }
        return await response.json();
    }
};
export default ReportAPI;
