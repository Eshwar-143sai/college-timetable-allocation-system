const API_BASE_URL = "http://127.0.0.1:8000/api/v1/rooms";

const RoomAPI = {
    // CLASSROOMS
    async getClassrooms(building = "", availableOnly = null) {
        let url = `${API_BASE_URL}/classrooms?`;
        if (building) url += `building=${encodeURIComponent(building)}&`;
        if (availableOnly !== null) url += `available_only=${availableOnly}`;
        
        const response = await fetch(url);
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to fetch classrooms");
        }
        return await response.json();
    },

    async getClassroomDetails(classroomId) {
        const response = await fetch(`${API_BASE_URL}/classrooms/${classroomId}`);
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to fetch classroom details");
        }
        return await response.json();
    },

    async createClassroom(data) {
        const response = await fetch(`${API_BASE_URL}/classrooms`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to create classroom");
        }
        return await response.json();
    },

    async updateClassroom(classroomId, data) {
        const response = await fetch(`${API_BASE_URL}/classrooms/${classroomId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to update classroom");
        }
        return await response.json();
    },

    async deleteClassroom(classroomId) {
        const response = await fetch(`${API_BASE_URL}/classrooms/${classroomId}`, {
            method: "DELETE"
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to delete classroom");
        }
        return true;
    },

    // LABORATORIES
    async getLaboratories(building = "", availableOnly = null) {
        let url = `${API_BASE_URL}/laboratories?`;
        if (building) url += `building=${encodeURIComponent(building)}&`;
        if (availableOnly !== null) url += `available_only=${availableOnly}`;
        
        const response = await fetch(url);
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to fetch laboratories");
        }
        return await response.json();
    },

    async getLaboratoryDetails(labId) {
        const response = await fetch(`${API_BASE_URL}/laboratories/${labId}`);
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to fetch laboratory details");
        }
        return await response.json();
    },

    async createLaboratory(data) {
        const response = await fetch(`${API_BASE_URL}/laboratories`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to create laboratory");
        }
        return await response.json();
    },

    async updateLaboratory(labId, data) {
        const response = await fetch(`${API_BASE_URL}/laboratories/${labId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to update laboratory");
        }
        return await response.json();
    },

    async deleteLaboratory(labId) {
        const response = await fetch(`${API_BASE_URL}/laboratories/${labId}`, {
            method: "DELETE"
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to delete laboratory");
        }
        return true;
    }
};
export default RoomAPI;
