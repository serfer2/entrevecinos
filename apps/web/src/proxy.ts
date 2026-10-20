import { type NextRequest, NextResponse } from "next/server";

import { isPublicRoute, LOGIN_PATH, SESSION_COOKIE } from "@/features/auth/routes";
import { buildCsp, originOf } from "@/lib/security/csp";

// Se calcula al cargar: sin un origen válido, falla al arrancar en lugar de bloquear las imágenes.
const storageOrigin = originOf(process.env.STORAGE_PUBLIC_URL);

/**
 * 1. Sin cookie de sesión, las rutas privadas redirigen al inicio de sesión. No valida el token
 *    (se ejecuta en cada petición, incluidos los prefetch): lo hace el DAL.
 * 2. Content-Security-Policy con un nonce por petición; Next lo lee de la cabecera de la
 *    petición y lo aplica a sus scripts (guía «Content Security Policy» de Next.js).
 */
export function proxy(request: NextRequest) {
  const { pathname, search } = request.nextUrl;
  if (!isPublicRoute(pathname) && !request.cookies.has(SESSION_COOKIE)) {
    const loginUrl = new URL(LOGIN_PATH, request.url);
    loginUrl.searchParams.set("next", `${pathname}${search}`);
    return NextResponse.redirect(loginUrl);
  }

  const nonce = Buffer.from(crypto.randomUUID()).toString("base64");
  const csp = buildCsp({ nonce, isDev: process.env.NODE_ENV === "development", storageOrigin });

  const requestHeaders = new Headers(request.headers);
  requestHeaders.set("x-nonce", nonce);
  requestHeaders.set("Content-Security-Policy", csp);
  const response = NextResponse.next({ request: { headers: requestHeaders } });
  response.headers.set("Content-Security-Policy", csp);
  return response;
}

export const config = {
  // Todo salvo los recursos estáticos de Next y los ficheros con extensión (public/).
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\..*).*)"],
};
