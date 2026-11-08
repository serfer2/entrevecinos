import { type NextRequest, NextResponse } from "next/server";

import { savePasswordResetToken } from "@/features/auth/reset-token";
import { PASSWORD_RESET_PATH } from "@/features/auth/routes";

/**
 * Destino del enlace del correo para restablecer la contraseña. Pasa el token a una cookie y
 * redirige a la página limpia: el token no queda en la barra de direcciones ni en el historial.
 * No llama a la API: un escáner del cliente de correo que abra el enlace no consume nada.
 */
export async function GET(request: NextRequest) {
  const token = request.nextUrl.searchParams.get("token");
  if (!token || token.length > 256) return redirectTo(`${PASSWORD_RESET_PATH}?motivo=invalido`);

  await savePasswordResetToken(token);
  return redirectTo(PASSWORD_RESET_PATH);
}

/** `Location` relativo (`request.url` lleva el host interno) y sin caché: la URL lleva el token. */
function redirectTo(path: string): NextResponse {
  return new NextResponse(null, {
    status: 303,
    headers: { Location: path, "Cache-Control": "no-store" },
  });
}
