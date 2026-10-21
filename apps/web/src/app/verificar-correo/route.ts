import { type NextRequest, NextResponse } from "next/server";

import { getCurrentUser } from "@/features/auth/dal";
import {
  COMMUNITIES_PATH,
  EMAIL_VERIFIED_LOGIN_PATH,
  VERIFY_EMAIL_ERROR_PATH,
} from "@/features/auth/routes";
import { createSession } from "@/features/auth/session";
import type { AuthResponse } from "@/features/auth/types";
import { type ApiError, errorCodeOf } from "@/lib/api/errors";
import { apiFetch } from "@/lib/api/server";

/**
 * Destino del enlace del correo de validación. Es un route handler porque una página de servidor
 * no puede escribir la cookie de sesión.
 */
export async function GET(request: NextRequest) {
  const token = request.nextUrl.searchParams.get("token");
  if (!token) return redirectTo(errorPath("invalido"));

  const result = await apiFetch<AuthResponse>("/auth/email-verification", {
    method: "POST",
    body: { token },
  });

  if (result.ok) {
    await createSession(result.data.access_token, result.data.expires_in);
    // Igual que el registro antes de la validación: una cuenta nueva empieza buscando su comunidad.
    return redirectTo(COMMUNITIES_PATH);
  }
  if (result.error.status === 410) return redirectTo(errorPath("caducado", result.error));
  if (result.error.status === 400) {
    const code = errorCodeOf(result.error);
    if (code === "email_already_verified") {
      // Enlace ya usado (abierto dos veces o por el escáner del cliente de correo): con sesión se
      // sigue como si nada; sin ella, se pide iniciarla.
      const user = await getCurrentUser().catch(() => null);
      return redirectTo(user ? COMMUNITIES_PATH : EMAIL_VERIFIED_LOGIN_PATH);
    }
    if (code === "verification_superseded") {
      return redirectTo(errorPath("reemplazado", result.error));
    }
    return redirectTo(errorPath("invalido"));
  }
  return redirectTo(errorPath("error"));
}

/** Página de error con el motivo y, si la API lo devuelve, el correo para ofrecer el reenvío. */
function errorPath(reason: string, error?: ApiError): string {
  const query = new URLSearchParams({ motivo: reason });
  const email = error?.payload?.email;
  if (typeof email === "string") query.set("email", email);
  return `${VERIFY_EMAIL_ERROR_PATH}?${query}`;
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
