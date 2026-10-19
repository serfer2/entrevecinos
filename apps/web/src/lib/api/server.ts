import "server-only";

import type { ApiError } from "./errors";

export type ApiResult<T> =
  | { ok: true; status: number; data: T }
  | { ok: false; error: ApiError };

type ApiFetchOptions = {
  method?: "GET" | "POST" | "PATCH" | "DELETE";
  body?: unknown;
  token?: string;
};

/** Llama a la API desde el servidor de Next. Nunca lanza: los fallos llegan como `ok: false`. */
export async function apiFetch<T>(
  path: string,
  { method = "GET", body, token }: ApiFetchOptions = {},
): Promise<ApiResult<T>> {
  const baseUrl = process.env.API_INTERNAL_URL;
  if (!baseUrl) throw new Error("API_INTERNAL_URL no está definida");

  const headers: Record<string, string> = { Accept: "application/json" };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (token) headers.Authorization = `Bearer ${token}`;

  let response: Response;
  try {
    response = await fetch(`${baseUrl}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      cache: "no-store",
    });
  } catch {
    return { ok: false, error: { status: 0, detail: null } };
  }

  const payload = await response.json().catch(() => null);
  if (response.ok) return { ok: true, status: response.status, data: payload as T };
  return { ok: false, error: { status: response.status, detail: payload?.detail ?? null } };
}
