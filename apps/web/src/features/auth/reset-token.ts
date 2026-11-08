import "server-only";

import { cookies } from "next/headers";

import { PASSWORD_RESET_COOKIE, PASSWORD_RESET_PATH } from "./routes";

/** Vida de la cookie: la del enlace (60 minutos). La caducidad real la decide la API. */
const MAX_AGE_SECONDS = 60 * 60;

/**
 * Guarda el token del enlace del correo en una cookie httpOnly que solo viaja a la página de la
 * contraseña nueva y a su Server Action: así no queda en la URL, el historial ni el `Referer`.
 */
export async function savePasswordResetToken(token: string): Promise<void> {
  const cookieStore = await cookies();
  cookieStore.set(PASSWORD_RESET_COOKIE, token, {
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: PASSWORD_RESET_PATH,
    maxAge: MAX_AGE_SECONDS,
  });
}

export async function getPasswordResetToken(): Promise<string | undefined> {
  const cookieStore = await cookies();
  return cookieStore.get(PASSWORD_RESET_COOKIE)?.value || undefined;
}

export async function deletePasswordResetToken(): Promise<void> {
  const cookieStore = await cookies();
  cookieStore.delete({ name: PASSWORD_RESET_COOKIE, path: PASSWORD_RESET_PATH });
}
