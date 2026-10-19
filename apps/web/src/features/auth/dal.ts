import "server-only";

import { redirect } from "next/navigation";
import { cache } from "react";

import { apiFetch } from "@/lib/api/server";

import { SESSION_EXPIRED_PATH } from "./routes";
import { getSessionToken } from "./session";
import type { ApiUser } from "./types";

/** Datos del usuario que necesita la interfaz (nunca el token). */
export type CurrentUser = Pick<ApiUser, "id" | "full_name" | "email" | "phone">;

/**
 * Usuario de la sesión, validado por la API. `null` si no hay sesión o el token ya no es válido.
 * Se memoriza durante la petición: varias llamadas hacen una sola consulta.
 */
export const getCurrentUser = cache(async (): Promise<CurrentUser | null> => {
  const token = await getSessionToken();
  if (!token) return null;

  const result = await apiFetch<ApiUser>("/users/me", { token });
  if (result.ok) {
    const { id, full_name, email, phone } = result.data;
    return { id, full_name, email, phone };
  }
  if (result.error.status === 401) return null;
  throw new Error(`No se pudo comprobar la sesión (estado ${result.error.status})`);
});

/** Usuario de la sesión o redirección al inicio de sesión. Llamar en cada página o acción privada. */
export async function requireUser(): Promise<CurrentUser> {
  const user = await getCurrentUser();
  if (!user) redirect(SESSION_EXPIRED_PATH);
  return user;
}
