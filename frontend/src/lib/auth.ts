export function setToken(token: string) {
  if (typeof window !== 'undefined') {
    localStorage.setItem('access_token', token);
  }
}

export function getToken(): string | null {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('access_token');
  }
  return null;
}

export function removeToken() {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('access_token');
  }
}

export async function fetchWithAuth(url: string, options: RequestInit = {}) {
  const token = getToken();
  
  const headers = new Headers(options.headers || {});
  
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  
  const config = {
    ...options,
    headers,
  };
  
  const response = await fetch(url, config);
  
  // If we receive a 401, token might be invalid/expired.
  if (response.status === 401) {
    removeToken();
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  }
  
  return response;
}
