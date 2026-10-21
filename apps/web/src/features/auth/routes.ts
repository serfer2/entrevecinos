/** Rutas accesibles sin sesión. Todas las demás son privadas por defecto. */
export const PUBLIC_ROUTES: readonly string[] = [
  "/",
  "/registro",
  "/iniciar-sesion",
  "/verificar-correo",
  "/verificar-correo/error",
];

export const LOGIN_PATH = "/iniciar-sesion";
export const HOME_PATH = "/inicio";
export const COMMUNITIES_PATH = "/comunidades";
export const SESSION_EXPIRED_PATH = `${LOGIN_PATH}?motivo=sesion-caducada`;
export const EMAIL_VERIFIED_LOGIN_PATH = `${LOGIN_PATH}?motivo=correo-validado`;
/** Destino del enlace del correo de validación (lo construye la API con `WEB_PUBLIC_URL`). */
export const VERIFY_EMAIL_PATH = "/verificar-correo";
export const VERIFY_EMAIL_ERROR_PATH = "/verificar-correo/error";

/** Nombre de la cookie de sesión (sin dependencias de servidor: lo usa también el proxy). */
export const SESSION_COOKIE = "ev_session";

export function isPublicRoute(pathname: string): boolean {
  return PUBLIC_ROUTES.includes(pathname);
}
