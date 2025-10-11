/**
 * Authenticated API client
 */

import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { getAuthHeaders } from './auth';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

// Request interceptor to add auth headers
apiClient.interceptors.request.use(
  (config) => {
    const authHeaders = getAuthHeaders();
    config.headers = {
      ...config.headers,
      ...authHeaders,
    };
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth data and redirect to login
      if (typeof window !== 'undefined') {
        localStorage.removeItem('os-forge-auth-token');
        localStorage.removeItem('os-forge-auth-user');
        window.location.href = '/';
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
