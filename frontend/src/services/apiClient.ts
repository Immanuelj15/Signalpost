/**
 * Signalpost API Client
 * Centralized HTTP client configured with VITE_API_BASE_URL.
 * Automatically delegates to Mock Demo Service when no backend is configured or offline.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

export const isDemoMode = (): boolean => {
  return !API_BASE_URL || API_BASE_URL.trim() === "" || API_BASE_URL === "mock";
};

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  isDemo: boolean;
  status: number;
}

export async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  if (isDemoMode()) {
    return {
      status: 200,
      isDemo: true,
      error: "Backend is currently in Demo Mode. Connect VITE_API_BASE_URL to hit live FastAPI endpoints.",
    };
  }

  try {
    const url = `${API_BASE_URL.replace(/\/$/, "")}/${endpoint.replace(/^\//, "")}`;
    const res = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
        ...options.headers,
      },
    });

    if (!res.ok) {
      const errText = await res.text();
      return {
        status: res.status,
        error: `HTTP ${res.status}: ${errText || res.statusText}`,
        isDemo: false,
      };
    }

    const data = (await res.json()) as T;
    return {
      status: res.status,
      data,
      isDemo: false,
    };
  } catch (err: any) {
    return {
      status: 0,
      error: err.message || "Network request failed. Is the Signalpost API server running?",
      isDemo: false,
    };
  }
}
