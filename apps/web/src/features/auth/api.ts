import "server-only";

import { redirect } from "next/navigation";

import { apiFetch, type ApiResult } from "@/lib/api/server";

import { SESSION_EXPIRED_PATH } from "./routes";
import { getSessionToken } from "./session";

type UserApiFetchOptions = Omit<NonNullable<Parameters<typeof apiFetch>[1]>, "token">;

/**
 * Llama a la API con el token de la sesión. Si la API responde 401 (token caducado o revocado),
 * redirige al inicio de sesión: el resto de errores llegan como `ok: false`.
 */
export async function userApiFetch<T>(
  path: string,
  options: UserApiFetchOptions = {},
): Promise<ApiResult<T>> {
  const token = await getSessionToken();
  if (!token) redirect(SESSION_EXPIRED_PATH);

  const result = await apiFetch<T>(path, { ...options, token });
  if (!result.ok && result.error.status === 401) redirect(SESSION_EXPIRED_PATH);
  return result;
}
