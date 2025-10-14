// Configuration file for API endpoints
const config = {
    API_URL: 'http://localhost:5000/api',  // Change this to your production URL when deploying
    DEFAULT_HEADERS: {
        'Content-Type': 'application/json'
    },
    FETCH_OPTIONS: {
        credentials: 'include'  // Needed for session cookies
    }
};

// Helper function for API calls
async function callAPI(endpoint, options = {}) {
    try {
        const url = `${config.API_URL}${endpoint}`;
        const defaultOptions = {
            ...config.FETCH_OPTIONS,
            headers: config.DEFAULT_HEADERS
        };
        const response = await fetch(url, { ...defaultOptions, ...options });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}