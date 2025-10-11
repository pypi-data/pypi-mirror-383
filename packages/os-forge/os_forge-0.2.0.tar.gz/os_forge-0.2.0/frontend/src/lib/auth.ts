/**
 * Authentication utilities and types
 */

export interface User {
  email: string;
  device_name?: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials {
  email: string;
  password: string;
  confirmPassword: string;
}

export interface AuthResponse {
  status: string;
  token?: string;
  message?: string;
}

// Token management
export const AUTH_TOKEN_KEY = 'os-forge-auth-token';
export const AUTH_USER_KEY = 'os-forge-auth-user';

export const getStoredToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(AUTH_TOKEN_KEY);
};

export const getStoredUser = (): User | null => {
  if (typeof window === 'undefined') return null;
  const userStr = localStorage.getItem(AUTH_USER_KEY);
  if (!userStr) return null;
  try {
    return JSON.parse(userStr);
  } catch {
    return null;
  }
};

export const setStoredAuth = (token: string, user: User): void => {
  if (typeof window === 'undefined') return;
  localStorage.setItem(AUTH_TOKEN_KEY, token);
  localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
};

export const clearStoredAuth = (): void => {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(AUTH_USER_KEY);
};

// API utilities
export const getAuthHeaders = (token: string | null = null): Record<string, string> => {
  const authToken = token || getStoredToken();
  if (!authToken) return {};
  
  return {
    'Authorization': `Bearer ${authToken}`,
    'Content-Type': 'application/json',
  };
};
