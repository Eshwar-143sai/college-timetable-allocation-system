const API_BASE_URL = "http://127.0.0.1:8000/api/v1/faculty";

const FacultyAPI = {
    async getAll(search = "", departmentId = "") {
        let url = `${API_BASE_URL}/?`;
        if (search) url += `search=${encodeURIComponent(search)}&`;
        if (departmentId) url += `department_id=${encodeURIComponent(departmentId)}`;
        
        const response = await fetch(url);
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to fetch faculty list");
        }
        return await response.json();
    },

    async getDetails(facultyId) {
        const response = await fetch(`${API_BASE_URL}/${facultyId}`);
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to fetch faculty details");
        }
        return await response.json();
    },

    async create(data) {
        const response = await fetch(`${API_BASE_URL}/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to create faculty");
        }
        return await response.json();
    },

    async update(facultyId, data) {
        const response = await fetch(`${API_BASE_URL}/${facultyId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to update faculty");
        }
        return await response.json();
    },

    async delete(facultyId) {
        const response = await fetch(`${API_BASE_URL}/${facultyId}`, {
            method: "DELETE"
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to delete faculty");
        }
        return true;
    },

    async assignSubject(facultyId, courseId, academicYear) {
        const response = await fetch(`${API_BASE_URL}/${facultyId}/assign-subject`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ course_id: parseInt(courseId), academic_year: academicYear })
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to assign subject");
        }
        return await response.json();
    },

    async unassignSubject(facultyId, courseId, academicYear) {
        const response = await fetch(`${API_BASE_URL}/${facultyId}/unassign-subject/${courseId}?academic_year=${encodeURIComponent(academicYear)}`, {
            method: "DELETE"
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to unassign subject");
        }
        return true;
    },

    async getDepartments() {
        const response = await fetch(`${API_BASE_URL}/helper/departments`);
        if (!response.ok) {
            throw new Error("Failed to load departments");
        }
        return await response.json();
    },

    async getCourses() {
        const response = await fetch(`${API_BASE_URL}/helper/courses`);
        if (!response.ok) {
            throw new Error("Failed to load courses");
        }
        return await response.json();
    }
};
export default FacultyAPI;
