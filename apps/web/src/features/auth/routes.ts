/** Rutas accesibles sin sesión. Todas las demás son privadas por defecto. */
export const PUBLIC_ROUTES: readonly string[] = [
  "/",
  "/registro",
  "/iniciar-sesion",
  "/verificar-correo",
  "/verificar-correo/error",
  "/recuperar-contrasena",
  "/restablecer-contrasena",
  "/restablecer-contrasena/enlace",
];

export const LOGIN_PATH = "/iniciar-sesion";
export const HOME_PATH = "/inicio";
export const COMMUNITIES_PATH = "/comunidades";
export const SESSION_EXPIRED_PATH = `${LOGIN_PATH}?motivo=sesion-caducada`;
export const EMAIL_VERIFIED_LOGIN_PATH = `${LOGIN_PATH}?motivo=correo-validado`;
/** Destino del enlace del correo de validación (lo construye la API con `WEB_PUBLIC_URL`). */
export const VERIFY_EMAIL_PATH = "/verificar-correo";
export const VERIFY_EMAIL_ERROR_PATH = "/verificar-correo/error";
/** Formulario para pedir el enlace de restablecimiento de la contraseña (TK-103). */
export const PASSWORD_RESET_REQUEST_PATH = "/recuperar-contrasena";
/** Página para elegir la contraseña nueva (TK-104). */
export const PASSWORD_RESET_PATH = "/restablecer-contrasena";
/** Destino del enlace del correo (lo construye la API con `WEB_PUBLIC_URL`). */
export const PASSWORD_RESET_LINK_PATH = "/restablecer-contrasena/enlace";
export const PASSWORD_CHANGED_LOGIN_PATH = `${LOGIN_PATH}?motivo=contrasena-cambiada`;

/** Nombre de la cookie de sesión (sin dependencias de servidor: lo usa también el proxy). */
export const SESSION_COOKIE = "ev_session";
/** Token del enlace para restablecer la contraseña, solo para `PASSWORD_RESET_PATH`. */
export const PASSWORD_RESET_COOKIE = "ev_password_reset";

export function isPublicRoute(pathname: string): boolean {
  return PUBLIC_ROUTES.includes(pathname);
}
