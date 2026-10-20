const INTERNAL_ORIGIN = "http://entrevecinos.internal";

/** Devuelve `value` si es una ruta interna segura, o `null` (evita los open redirects). */
export function safeNextPath(value: unknown): string | null {
  if (typeof value !== "string") return null;
  if (!value.startsWith("/") || value.startsWith("//") || value.includes("\\")) return null;
  if (/[\u0000-\u001f\u007f]/.test(value)) return null;

  const url = new URL(value, INTERNAL_ORIGIN);
  if (url.origin !== INTERNAL_ORIGIN) return null;
  return `${url.pathname}${url.search}${url.hash}`;
}
