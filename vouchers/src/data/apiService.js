import axios from 'axios';

// Create axios instance with base configuration
const apiService = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

// Request interceptor for adding auth tokens, etc.
apiService.interceptors.request.use(
  config => {
    // Add any request modifiers here (e.g., auth tokens)
    return config;
  },
  error => Promise.reject(error)
);

// Response interceptor for handling errors
apiService.interceptors.response.use(
  response => response,
  error => {
    // Handle API errors globally
    console.error('API Error:', error.response);
    return Promise.reject(error);
  }
);

// Main API methods
export default {
  /**
   * Send a POST request
   * @param {string} url - API endpoint
   * @param {Object} data - Request payload
   * @returns {Promise} Axios response
   */
  post(url, data) {
    return apiService.post(url, data);
  },

  /**
   * Send a GET request
   * @param {string} url - API endpoint
   * @param {Object} params - Query parameters
   * @returns {Promise} Axios response
   */
  get(url, params = {}) {
    return apiService.get(url, { params });
  },

  // Add other methods as needed (put, delete, etc.)
};