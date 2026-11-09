/**
 * Mensajes de `/admin/comunidades` según `?resultado=`. Reciben el nombre de la comunidad
 * (`?nombre=`), que solo usa el del rechazo.
 */
export const PENDING_COMMUNITIES_RESULT_MESSAGES = {
  aprobada: () => "Comunidad aprobada.",
  error: () => "No se pudo aprobar la comunidad. Inténtalo de nuevo.",
  rechazada: (name: string) =>
    name ? `Se ha rechazado la comunidad ${name}.` : "Se ha rechazado la comunidad.",
  "ya-activa": () => "Esta comunidad ya está activa: no se puede rechazar.",
  "no-existe": () => "Esta comunidad ya no está pendiente.",
  "error-rechazo": () => "No se pudo rechazar la comunidad. Inténtalo de nuevo.",
} as const satisfies Record<string, (name: string) => string>;

export type PendingCommunitiesResult = keyof typeof PENDING_COMMUNITIES_RESULT_MESSAGES;

/** Resultados que se muestran como error (`role="alert"`). */
export const PENDING_COMMUNITIES_ERRORS: ReadonlySet<PendingCommunitiesResult> = new Set([
  "error",
  "ya-activa",
  "no-existe",
  "error-rechazo",
]);

export const PENDING_COMMUNITIES_PATH = "/admin/comunidades";

export function pendingCommunitiesPath(result?: PendingCommunitiesResult, name?: string): string {
  if (!result) return PENDING_COMMUNITIES_PATH;
  const query = new URLSearchParams({ resultado: result, ...(name ? { nombre: name } : {}) });
  return `${PENDING_COMMUNITIES_PATH}?${query}`;
}

/** Ancla de cada comunidad en la lista: el correo de una comunidad nueva enlaza a ella (TK-111). */
export function pendingCommunityAnchor(communityId: string): string {
  return `comunidad-${communityId}`;
}
