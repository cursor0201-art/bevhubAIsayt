const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface RequestOptions extends RequestInit {
  params?: Record<string, string>;
}

export class APIClient {
  private static async getAccessToken(): Promise<string | null> {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('access_token');
  }

  private static async getRefreshToken(): Promise<string | null> {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('refresh_token');
  }

  private static async refreshSession(): Promise<string | null> {
    const refresh = await this.getRefreshToken();
    if (!refresh) return null;

    try {
      const response = await fetch(`${BASE_URL}/api/auth/token/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh }),
      });

      if (!response.ok) throw new Error('Refresh token invalid');
      const data = await response.json();
      
      if (data.access) {
        localStorage.setItem('access_token', data.access);
        if (data.refresh) {
          localStorage.setItem('refresh_token', data.refresh);
        }
        return data.access;
      }
    } catch {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
    return null;
  }

  public static async request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    let url = `${BASE_URL}${endpoint}`;
    
    // Append query params if they exist
    if (options.params) {
      const searchParams = new URLSearchParams(options.params);
      url += `?${searchParams.toString()}`;
    }

    const headers = new Headers(options.headers || {});
    if (!headers.has('Content-Type')) {
      headers.set('Content-Type', 'application/json');
    }

    // Prevent caching on GET requests to ensure real-time status updates are never stale
    if (options.method === 'GET') {
      headers.set('Cache-Control', 'no-cache, no-store, must-revalidate');
      headers.set('Pragma', 'no-cache');
      headers.set('Expires', '0');
    }

    // Attempt to set auth header
    const token = await this.getAccessToken();
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }

    const config: RequestInit = {
      ...options,
      headers,
    };

    let response = await fetch(url, config);

    // If 401 Unauthorized, attempt a single refresh cycle
    if (response.status === 401) {
      const newToken = await this.refreshSession();
      if (newToken) {
        headers.set('Authorization', `Bearer ${newToken}`);
        response = await fetch(url, config);
      } else {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/';
          // Return an unresolved promise to halt execution until the page reloads
          return new Promise(() => {}) as Promise<T>;
        }
        throw new Error('Authentication expired. Please log in again.');
      }
    }

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API Error [${response.status}]: ${errorText || response.statusText}`);
    }

    // Return JSON or fallback to empty object if response body is empty
    const contentType = response.headers.get('Content-Type');
    if (contentType && contentType.includes('application/json')) {
      return response.json() as Promise<T>;
    }
    
    return {} as T;
  }

  public static get<T>(endpoint: string, options?: Omit<RequestOptions, 'method'>): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'GET' });
  }

  public static post<T>(endpoint: string, body?: any, options?: Omit<RequestOptions, 'method' | 'body'>): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  public static put<T>(endpoint: string, body?: any, options?: Omit<RequestOptions, 'method' | 'body'>): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  public static delete<T>(endpoint: string, options?: Omit<RequestOptions, 'method'>): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: 'DELETE' });
  }

  public static patch<T>(endpoint: string, body?: any, options?: Omit<RequestOptions, 'method' | 'body'>): Promise<T> {
    return this.request<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
    });
  }
}

