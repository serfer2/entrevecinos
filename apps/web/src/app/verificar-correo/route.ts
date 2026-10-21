import { type NextRequest, NextResponse } from "next/server";

import { getCurrentUser } from "@/features/auth/dal";
import {
  COMMUNITIES_PATH,
  EMAIL_VERIFIED_LOGIN_PATH,
  VERIFY_EMAIL_ERROR_PATH,
} from "@/features/auth/routes";
import { createSession } from "@/features/auth/session";
import type { AuthResponse } from "@/features/auth/types";
import { apiFetch } from "@/lib/api/server";

/**
 * Destino del enlace del correo de validación. Es un route handler porque una página de servidor
 * no puede escribir la cookie de sesión.
 */
export async function GET(request: NextRequest) {
  const token = request.nextUrl.searchParams.get("token");
  if (!token) return redirectTo(`${VERIFY_EMAIL_ERROR_PATH}?motivo=invalido`);

  const result = await apiFetch<AuthResponse>("/auth/email-verification", {
    method: "POST",
    body: { token },
  });

  if (result.ok) {
    await createSession(result.data.access_token, result.data.expires_in);
    // Igual que el registro antes de la validación: una cuenta nueva empieza buscando su comunidad.
    return redirectTo(COMMUNITIES_PATH);
  }
  if (result.error.status === 410) {
    const email = result.error.payload?.email;
    const query = new URLSearchParams({ motivo: "caducado" });
    if (typeof email === "string") query.set("email", email);
    return redirectTo(`${VERIFY_EMAIL_ERROR_PATH}?${query}`);
  }
  if (result.error.status === 400) {
    // Enlace ya usado (abierto dos veces o por el escáner del cliente de correo): con sesión se
    // sigue como si nada; sin ella, se pide iniciarla.
    const user = await getCurrentUser().catch(() => null);
    return redirectTo(user ? COMMUNITIES_PATH : EMAIL_VERIFIED_LOGIN_PATH);
  }
  return redirectTo(`${VERIFY_EMAIL_ERROR_PATH}?motivo=error`);
}

/**
 * Redirección con `Location` relativo: `request.url` lleva el host interno del servidor. El token
 * va en la URL: no se guarda en caché (el `Referrer-Policy: no-referrer` se fija en next.config.ts).
 */
function redirectTo(path: string): NextResponse {
  return new NextResponse(null, {
    status: 303,
    headers: { Location: path, "Cache-Control": "no-store" },
  });
}
