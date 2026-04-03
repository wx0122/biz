const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:6007/api";

function getHeaders(): Record<string, string> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const openid = localStorage.getItem("openid") || "guest";
  headers["X-Openid"] = openid;
  return headers;
}

function adminHeaders(): Record<string, string> {
  const headers = getHeaders();
  const token = localStorage.getItem("admin_token");
  if (token) headers["Authorization"] = `Bearer ${token}`;
  return headers;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: getHeaders(),
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || res.statusText);
  }
  return res.json();
}

// ── Hospitals ────────────────────────────────────
export const hospitalApi = {
  list: (params?: { city?: string; search?: string }) => {
    const qs = new URLSearchParams(params as Record<string, string>).toString();
    return request<{ items: any[]; total: number }>(`/hospitals?${qs}`);
  },
  get: (id: number) => request<any>(`/hospitals/${id}`),
};

// ── Escorts ──────────────────────────────────────
export const escortApi = {
  list: (city?: string) => {
    const qs = city ? `?city=${city}` : "";
    return request<{ items: any[]; total: number }>(`/escorts${qs}`);
  },
};

// ── Bookings ─────────────────────────────────────
export const bookingApi = {
  create: (data: any) =>
    request<any>("/bookings", { method: "POST", body: JSON.stringify(data) }),
  list: () => request<{ items: any[]; total: number }>("/bookings"),
  cancel: (id: number) =>
    request<any>(`/bookings/${id}/cancel`, { method: "POST" }),
};

// ── Training ─────────────────────────────────────
export const trainingApi = {
  courses: () => request<{ items: any[] }>("/training/courses"),
  register: (data: any) =>
    request<any>("/training/register", { method: "POST", body: JSON.stringify(data) }),
  registrations: () => request<{ items: any[]; total: number }>("/training/registrations"),
};

// ── Orders ───────────────────────────────────────
export const orderApi = {
  list: (type?: string) => {
    const qs = type && type !== "all" ? `?type=${type}` : "";
    return request<{ items: any[] }>(`/orders${qs}`);
  },
};

// ── Users ────────────────────────────────────────
export const userApi = {
  me: () => request<any>("/users/me"),
  update: (data: any) =>
    request<any>("/users/me", { method: "PUT", body: JSON.stringify(data) }),
  records: () => request<any>("/users/records"),
};

// ── Payments ─────────────────────────────────────
export const paymentApi = {
  create: (data: { order_type: string; order_id: number; method: string }) =>
    request<any>("/payments/create", { method: "POST", body: JSON.stringify(data) }),
  status: (paymentNo: string) => request<any>(`/payments/status/${paymentNo}`),
};

// ── Cities ───────────────────────────────────────
export const cityApi = {
  list: () => request<{ items: any[]; hot: any[] }>("/cities"),
  detect: (lat?: number, lng?: number) => {
    const qs = lat && lng ? `?lat=${lat}&lng=${lng}` : "";
    return request<{ city: string; province: string; detected_by: string }>(`/cities/detect${qs}`);
  },
  search: (q: string) => request<{ items: any[] }>(`/cities/search?q=${q}`),
};

// ── Admin ────────────────────────────────────────
export const adminApi = {
  login: async (username: string, password: string) => {
    const res = await fetch(`${API_BASE}/admin/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) throw new Error("Login failed");
    const data = await res.json();
    localStorage.setItem("admin_token", data.access_token);
    return data;
  },
  me: () =>
    fetch(`${API_BASE}/admin/me`, { headers: adminHeaders() }).then((r) => r.json()),
  dashboard: () =>
    fetch(`${API_BASE}/admin/dashboard`, { headers: adminHeaders() }).then((r) => r.json()),
  logout: () => localStorage.removeItem("admin_token"),
};
