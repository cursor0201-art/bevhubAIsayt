import { APIClient } from './apiClient';

export interface UserProfile {
  username: string;
  email: string;
  role: string;
}

export interface AuthResponse {
  user: UserProfile;
  tokens: {
    access: string;
    refresh: string;
  };
}

export class AuthService {
  public static async register(username: string, email: string, password: string, companyName = ""): Promise<AuthResponse> {
    const res = await APIClient.post<AuthResponse>('/api/auth/register/', {
      username,
      email,
      password,
      company_name: companyName,
    });
    if (res.tokens) {
      localStorage.setItem('access_token', res.tokens.access);
      localStorage.setItem('refresh_token', res.tokens.refresh);
      localStorage.setItem('user', JSON.stringify(res.user));
    }
    return res;
  }

  public static async login(username: string, password: string): Promise<any> {
    const res = await APIClient.post<any>('/api/auth/token/', {
      username,
      password,
    });
    if (res.access) {
      localStorage.setItem('access_token', res.access);
      localStorage.setItem('refresh_token', res.refresh);
      if (res.user) {
        localStorage.setItem('user', JSON.stringify(res.user));
      }
    }
    return res;
  }

  public static logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  }

  public static isAuthenticated(): boolean {
    if (typeof window === 'undefined') return false;
    return !!localStorage.getItem('access_token');
  }

  public static getCurrentUser(): UserProfile | null {
    if (typeof window === 'undefined') return null;
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }
}
