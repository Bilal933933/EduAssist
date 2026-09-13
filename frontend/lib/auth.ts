import { API_BASE_URL } from "./config";

const TOKEN_KEY = "rt_token";

export interface AuthUser {
  id: number;
  email: string;
  name: string | null;
}

export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function saveToken(token: string): void {
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken(): void {
  window.localStorage.removeItem(TOKEN_KEY);
}

export function authHeader(): Record<string, string> {
  const token = getAuthToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request(
  path: string,
  body: Record<string, unknown>,
): Promise<AuthUser> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    throw new Error("تعذر الاتصال بخدمة المصادقة.");
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = Array.isArray(data?.message)
      ? data.message.join(" - ")
      : data?.message;
    throw new Error(msg || "فشلت العملية.");
  }
  saveToken(data.token as string);
  return data.user as AuthUser;
}

export function login(email: string, password: string): Promise<AuthUser> {
  return request("/auth/login", { email, password });
}

export function register(
  email: string,
  password: string,
  name?: string,
): Promise<AuthUser> {
  return request("/auth/register", { email, password, name });
}
