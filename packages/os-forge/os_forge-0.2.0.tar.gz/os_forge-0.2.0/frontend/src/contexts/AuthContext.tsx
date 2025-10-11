'use client';

import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { User, AuthState, LoginCredentials, RegisterCredentials, AuthResponse, getStoredToken, getStoredUser, setStoredAuth, clearStoredAuth, getAuthHeaders } from '@/lib/auth';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

// Auth actions
type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'AUTH_FAILURE'; payload: string }
  | { type: 'AUTH_LOGOUT' }
  | { type: 'AUTH_LOADING'; payload: boolean };

// Auth reducer
const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'AUTH_START':
      return { ...state, isLoading: true };
    case 'AUTH_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        isLoading: false,
      };
    case 'AUTH_FAILURE':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      };
    case 'AUTH_LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        isLoading: false,
      };
    case 'AUTH_LOADING':
      return { ...state, isLoading: action.payload };
    default:
      return state;
  }
};

// Initial state
const initialState: AuthState = {
  user: null,
  token: null,
  isAuthenticated: false,
  isLoading: true,
};

// Auth context
interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (credentials: RegisterCredentials) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Auth provider
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Check authentication on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = getStoredToken();
    const user = getStoredUser();

    if (!token || !user) {
      dispatch({ type: 'AUTH_LOGOUT' });
      return;
    }

    try {
      // Verify token is still valid by making a test request
      const response = await axios.get(`${API_BASE}/reports`, {
        headers: getAuthHeaders(token),
      });
      
      if (response.status === 200) {
        dispatch({ type: 'AUTH_SUCCESS', payload: { user, token } });
      } else {
        throw new Error('Invalid token');
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      clearStoredAuth();
      dispatch({ type: 'AUTH_LOGOUT' });
    }
  };

  const login = async (credentials: LoginCredentials) => {
    dispatch({ type: 'AUTH_START' });
    
    try {
      const response = await axios.post<AuthResponse>(`${API_BASE}/web/login`, {
        email: credentials.email,
        password: credentials.password,
      });

      if (response.data.status === 'success' && response.data.token) {
        const user: User = { email: credentials.email };
        setStoredAuth(response.data.token, user);
        dispatch({ type: 'AUTH_SUCCESS', payload: { user, token: response.data.token } });
      } else {
        throw new Error(response.data.message || 'Login failed');
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Login failed';
      dispatch({ type: 'AUTH_FAILURE', payload: errorMessage });
      throw new Error(errorMessage);
    }
  };

  const register = async (credentials: RegisterCredentials) => {
    if (credentials.password !== credentials.confirmPassword) {
      throw new Error('Passwords do not match');
    }

    dispatch({ type: 'AUTH_START' });
    
    try {
      const response = await axios.post<AuthResponse>(`${API_BASE}/web/register`, {
        email: credentials.email,
        password: credentials.password,
      });

      if (response.data.status === 'success') {
        // Auto-login after successful registration
        await login({ email: credentials.email, password: credentials.password });
      } else {
        throw new Error(response.data.message || 'Registration failed');
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Registration failed';
      dispatch({ type: 'AUTH_FAILURE', payload: errorMessage });
      throw new Error(errorMessage);
    }
  };

  const logout = () => {
    clearStoredAuth();
    dispatch({ type: 'AUTH_LOGOUT' });
  };

  const value: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    checkAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// Auth hook
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
