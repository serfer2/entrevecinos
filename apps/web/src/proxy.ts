import { type NextRequest, NextResponse } from "next/server";

import { isPublicRoute, LOGIN_PATH, SESSION_COOKIE } from "@/features/auth/routes";

/**
 * Comprobación rápida: sin cookie de sesión, las rutas privadas redirigen al inicio de sesión.
 * No valida el token (se ejecuta en cada petición, incluidos los prefetch): lo hace el DAL.
 */
export function proxy(request: NextRequest) {
  const { pathname, search } = request.nextUrl;
  if (isPublicRoute(pathname) || request.cookies.has(SESSION_COOKIE)) {
    return NextResponse.next();
  }

  const loginUrl = new URL(LOGIN_PATH, request.url);
  loginUrl.searchParams.set("next", `${pathname}${search}`);
  return NextResponse.redirect(loginUrl);
}

export const config = {
  // Todo salvo los recursos estáticos de Next y los ficheros con extensión (public/).
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\..*).*)"],
};
