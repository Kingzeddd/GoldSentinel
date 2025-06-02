import axios from 'axios';
import { API_URL } from '../config';

// Types
interface Authority {
  name: string;
  status: boolean;
}

interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  job_title: string;
  institution: string;
  authorized_region: string;
  authorities: Authority[];
  primary_authority?: string;
}

interface LoginResponse {
  access: string;
  refresh: string;
  user: User;
}

// Service
const TOKEN_KEY = 'auth_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

class AuthService {
  async login(email: string, password: string): Promise<LoginResponse> {
    try {
      const response = await axios.post(`${API_URL}/auth/login/`, {
        email,
        password,
      });

      const { access, refresh, user } = response.data;
      this.setTokens(access, refresh);
      return response.data;
    } catch (error: any) {
      if (error.response?.status === 401) {
        throw new Error('Identifiants incorrects');
      }
      throw new Error('Erreur de connexion');
    }
  }

  logout(): void {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  }

  setTokens(access: string, refresh: string): void {
    localStorage.setItem(TOKEN_KEY, access);
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
  }

  getAccessToken(): string | null {
    return localStorage.getItem(TOKEN_KEY);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  }

  isAuthenticated(): boolean {
    return !!this.getAccessToken();
  }

  async refreshToken(): Promise<string> {
    try {
      const refresh = this.getRefreshToken();
      if (!refresh) {
        throw new Error('Pas de token de rafraîchissement');
      }

      const response = await axios.post(`${API_URL}/auth/token/refresh/`, {
        refresh,
      });

      const { access } = response.data;
      localStorage.setItem(TOKEN_KEY, access);
      return access;
    } catch (error) {
      this.logout();
      throw new Error('Session expirée');
    }
  }

  async getUserProfile(): Promise<User> {
    try {
      const response = await axios.get(`${API_URL}/account/profile/`, {
        headers: {
          Authorization: `Bearer ${this.getAccessToken()}`,
        },
      });
      return response.data;
    } catch (error) {
      throw new Error('Erreur récupération profil');
    }
  }
}

export const authService = new AuthService();
export type { User, LoginResponse };