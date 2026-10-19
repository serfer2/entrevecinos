/** Rutas accesibles sin sesión. Todas las demás son privadas por defecto. */
export const PUBLIC_ROUTES: readonly string[] = ["/", "/registro", "/iniciar-sesion"];

export const LOGIN_PATH = "/iniciar-sesion";
export const HOME_PATH = "/inicio";
export const SESSION_EXPIRED_PATH = `${LOGIN_PATH}?motivo=sesion-caducada`;

/** Nombre de la cookie de sesión (sin dependencias de servidor: lo usa también el proxy). */
export const SESSION_COOKIE = "ev_session";

export function isPublicRoute(pathname: string): boolean {
  return PUBLIC_ROUTES.includes(pathname);
}
