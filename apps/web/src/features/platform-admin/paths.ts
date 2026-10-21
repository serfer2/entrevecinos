export const PENDING_COMMUNITIES_RESULT_MESSAGES = {
  aprobada: "Comunidad aprobada.",
  error: "No se pudo aprobar la comunidad. Inténtalo de nuevo.",
} as const;

export type PendingCommunitiesResult = keyof typeof PENDING_COMMUNITIES_RESULT_MESSAGES;

export const PENDING_COMMUNITIES_PATH = "/admin/comunidades";

export function pendingCommunitiesPath(result?: PendingCommunitiesResult): string {
  return result ? `${PENDING_COMMUNITIES_PATH}?resultado=${result}` : PENDING_COMMUNITIES_PATH;
}
