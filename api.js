// API endpoints configuration
const API_BASE_URL = 'http://localhost:5000/api';

const defaultHeaders = {
    'Content-Type': 'application/json'
};

const defaultOptions = {
    credentials: 'include',
    headers: defaultHeaders
};

// Generic API call function
async function callAPI(endpoint, options = {}) {
    try {
        const url = `${API_BASE_URL}${endpoint}`;
        const response = await fetch(url, {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultHeaders,
                ...options.headers
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Auth API functions
export const authAPI = {
    login: async (username, password) => {
        return callAPI('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
    },
    logout: async () => {
        return callAPI('/auth/logout', { method: 'POST' });
    },
    checkStatus: async () => {
        return callAPI('/auth/status');
    }
};

// Student API functions
export const studentAPI = {
    getInfo: async () => {
        return callAPI('/student/info');
    },
    getDashboard: async () => {
        return callAPI('/student/dashboard');
    },
    submitAnswer: async (questionId, answer) => {
        return callAPI('/student/submit-answer', {
            method: 'POST',
            body: JSON.stringify({ questionId, answer })
        });
    },
    updateProgress: async (progress) => {
        return callAPI('/student/progress', {
            method: 'POST',
            body: JSON.stringify(progress)
        });
    },
    getQuestions: async (topic) => {
        return callAPI(`/student/questions?topic=${encodeURIComponent(topic)}`);
    },
    saveNote: async (topic, content) => {
        return callAPI('/student/notes', {
            method: 'POST',
            body: JSON.stringify({ topic, content })
        });
    },
    getNotes: async () => {
        return callAPI('/student/notes');
    },
    deleteNote: async (noteId) => {
        return callAPI(`/student/notes/${noteId}`, {
            method: 'DELETE'
        });
    },
    saveStudyEvent: async (event) => {
        return callAPI('/student/study-plan', {
            method: 'POST',
            body: JSON.stringify(event)
        });
    },
    getStudyPlan: async () => {
        return callAPI('/student/study-plan');
    },
    deleteStudyEvent: async (eventId) => {
        return callAPI(`/student/study-plan/${eventId}`, {
            method: 'DELETE'
        });
    },
    submitQuiz: async (answers) => {
        return callAPI('/student/quiz', {
            method: 'POST',
            body: JSON.stringify({ answers })
        });
    },
    submitFinalTest: async (answers) => {
        return callAPI('/student/final-test', {
            method: 'POST',
            body: JSON.stringify({ answers })
        });
    },
    getAchievements: async () => {
        return callAPI('/student/achievements');
    },
    getLeaderboard: async () => {
        return callAPI('/student/leaderboard');
    },
    getQuizBank: async () => {
        return callAPI('/student/quiz-bank');
    }
};

export default {
    auth: authAPI,
    student: studentAPI
};