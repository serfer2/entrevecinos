import "server-only";

import type { ApiError } from "./errors";

export type ApiResult<T> =
  | { ok: true; status: number; data: T }
  | { ok: false; error: ApiError };

type ApiFetchOptions = {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  /** Objeto JSON o `FormData` (multipart; el `Content-Type` lo pone `fetch`). */
  body?: unknown;
  token?: string;
};

function apiUrl(path: string): string {
  const baseUrl = process.env.API_INTERNAL_URL;
  if (!baseUrl) throw new Error("API_INTERNAL_URL no está definida");
  return `${baseUrl}${path}`;
}

/** Llama a la API desde el servidor de Next. Nunca lanza: los fallos llegan como `ok: false`. */
export async function apiFetch<T>(
  path: string,
  { method = "GET", body, token }: ApiFetchOptions = {},
): Promise<ApiResult<T>> {
  const isForm = body instanceof FormData;
  const headers: Record<string, string> = { Accept: "application/json" };
  if (body !== undefined && !isForm) headers["Content-Type"] = "application/json";
  if (token) headers.Authorization = `Bearer ${token}`;

  let response: Response;
  try {
    response = await fetch(apiUrl(path), {
      method,
      headers,
      body: body === undefined ? undefined : isForm ? body : JSON.stringify(body),
      cache: "no-store",
    });
  } catch {
    return { ok: false, error: { status: 0, detail: null } };
  }

  const payload = response.status === 204 ? null : await response.json().catch(() => null);
  if (response.ok) return { ok: true, status: response.status, data: payload as T };
  return {
    ok: false,
    error: { status: response.status, detail: payload?.detail ?? null, payload },
  };
}

/**
 * Pide a la API una redirección sin seguirla (p. ej. `GET /media/{id}` → URL prefirmada).
 * Devuelve el estado y el `Location`, o `status: 0` si la API no responde.
 */
export async function apiRedirect(
  path: string,
  token: string,
): Promise<{ status: number; location: string | null }> {
  try {
    const response = await fetch(apiUrl(path), {
      headers: { Authorization: `Bearer ${token}` },
      redirect: "manual",
      cache: "no-store",
    });
    return { status: response.status, location: response.headers.get("location") };
  } catch {
    return { status: 0, location: null };
  }
}
