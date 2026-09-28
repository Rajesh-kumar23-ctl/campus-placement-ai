/**
 * Central API Client for AI Placement Coach
 * All network requests routes through this unified module.
 */

// Dynamically determine backend API base URL
const API_BASE_URL = (() => {
    // If running on port 8000 (FastAPI static mount), use relative path
    if (window.location.port === "8000") {
        return "";
    }
    // Otherwise fallback to localhost:8000 default
    return "http://localhost:8000";
})();

class APIClient {
    constructor() {
        this.baseUrl = API_BASE_URL;
    }

    _getToken() {
        return localStorage.getItem("token");
    }

    async _request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const headers = options.headers || {};

        const token = this._getToken();
        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }

        // Only set Content-Type JSON if not FormData
        if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
            headers["Content-Type"] = "application/json";
        }

        const config = {
            ...options,
            headers
        };

        try {
            const response = await fetch(url, config);

            // Handle Unauthorized globally
            if (response.status === 401) {
                // If not already on login or register, redirect
                const path = window.location.pathname;
                if (!path.includes("login.html") && !path.includes("register.html") && path !== "/" && !path.endsWith("index.html")) {
                    localStorage.removeItem("token");
                    localStorage.removeItem("user");
                    window.location.href = "/pages/login.html?expired=1";
                }
            }

            const data = await response.json().catch(() => null);

            if (!response.ok) {
                const errorMsg = data?.detail || `Request failed with status ${response.status}`;
                throw new Error(errorMsg);
            }

            return data;
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    }

    // --- Authentication ---
    async register(userData) {
        return this._request("/api/auth/register", {
            method: "POST",
            body: JSON.stringify(userData)
        });
    }

    async login(credentials) {
        return this._request("/api/auth/login", {
            method: "POST",
            body: JSON.stringify(credentials)
        });
    }

    async getProfile() {
        return this._request("/api/auth/me", { method: "GET" });
    }

    async updateProfile(profileData) {
        return this._request("/api/auth/profile", {
            method: "PUT",
            body: JSON.stringify(profileData)
        });
    }

    async logout() {
        try {
            await this._request("/api/auth/logout", { method: "POST" });
        } catch (e) {
            // Ignore
        }
        localStorage.removeItem("token");
        localStorage.removeItem("user");
    }

    // --- Dashboard ---
    async getDashboard() {
        return this._request("/api/dashboard", { method: "GET" });
    }

    async getAiStatus() {
        return this._request("/api/dashboard/ai-status", { method: "GET" });
    }

    // --- Aptitude ---
    async getAptitudeCategories() {
        return this._request("/api/aptitude/categories", { method: "GET" });
    }

    async startAptitude(params) {
        return this._request("/api/aptitude/start", {
            method: "POST",
            body: JSON.stringify(params)
        });
    }

    async submitAptitude(submissionData) {
        return this._request("/api/aptitude/submit", {
            method: "POST",
            body: JSON.stringify(submissionData)
        });
    }

    async getAptitudeResult(attemptId) {
        return this._request(`/api/aptitude/results/${attemptId}`, { method: "GET" });
    }

    async getAptitudeHistory() {
        return this._request("/api/aptitude/history", { method: "GET" });
    }

    // --- Group Discussion ---
    async getGDTopics(search = null, category = null) {
        const queryParams = new URLSearchParams();
        if (search) queryParams.append("search", search);
        if (category) queryParams.append("category", category);
        const query = queryParams.toString() ? `?${queryParams.toString()}` : "";
        return this._request(`/api/gd/topics${query}`, { method: "GET" });
    }

    async getGDTopic(topicId) {
        return this._request(`/api/gd/topics/${topicId}`, { method: "GET" });
    }

    async generateGD(data) {
        return this._request("/api/gd/generate", {
            method: "POST",
            body: JSON.stringify(data)
        });
    }

    async startGD(data) {
        return this._request("/api/gd/start", {
            method: "POST",
            body: JSON.stringify(data)
        });
    }

    async submitGDResponse(data) {
        return this._request("/api/gd/respond", {
            method: "POST",
            body: JSON.stringify(data)
        });
    }

    async evaluateGD(sessionId) {
        return this._request("/api/gd/evaluate", {
            method: "POST",
            body: JSON.stringify({ session_id: sessionId })
        });
    }

    // --- AI Mock Interview ---
    async startInterview(data) {
        return this._request("/api/interview/start", {
            method: "POST",
            body: JSON.stringify(data)
        });
    }

    async submitInterviewAnswer(data) {
        return this._request("/api/interview/answer", {
            method: "POST",
            body: JSON.stringify(data)
        });
    }

    async endInterview(sessionId) {
        return this._request("/api/interview/end", {
            method: "POST",
            body: JSON.stringify({ session_id: sessionId })
        });
    }

    async getInterviewSession(sessionId) {
        return this._request(`/api/interview/${sessionId}`, { method: "GET" });
    }

    async getInterviewHistory() {
        return this._request("/api/interview/history", { method: "GET" });
    }

    // --- Resume AI ---
    async uploadResume(formData) {
        return this._request("/api/resume/upload", {
            method: "POST",
            body: formData
        });
    }

    async getLatestResume() {
        return this._request("/api/resume/latest", { method: "GET" });
    }

    async getResume(resumeId) {
        return this._request(`/api/resume/${resumeId}`, { method: "GET" });
    }

    async generateResumeQuestions(data) {
        return this._request("/api/resume/questions", {
            method: "POST",
            body: JSON.stringify(data)
        });
    }

    // --- Companies ---
    async getCompanies(search = null) {
        const query = search ? `?search=${encodeURIComponent(search)}` : "";
        return this._request(`/api/companies${query}`, { method: "GET" });
    }

    async getCompany(companyId) {
        return this._request(`/api/companies/${companyId}`, { method: "GET" });
    }

    // --- Progress & Analytics ---
    async getProgress() {
        return this._request("/api/progress", { method: "GET" });
    }

    // --- Full Placement Simulation ---
    async startSimulation(data) {
        return this._request("/api/simulation/start", {
            method: "POST",
            body: JSON.stringify(data)
        });
    }

    async completeSimulationRound(data) {
        return this._request("/api/simulation/complete-round", {
            method: "POST",
            body: JSON.stringify(data)
        });
    }

    async getSimulationReport(simulationId) {
        return this._request(`/api/simulation/${simulationId}`, { method: "GET" });
    }
}

// Export single shared instance globally
window.api = new APIClient();
