export const REQUESTS_RESULT_MESSAGES = {
  aprobada: "Solicitud aprobada.",
  rechazada: "Solicitud rechazada.",
  revisada: "Esta solicitud ya se había revisado.",
  error: "No se pudo revisar la solicitud. Inténtalo de nuevo.",
} as const;

export type RequestsResult = keyof typeof REQUESTS_RESULT_MESSAGES;

export function requestsPath(communityId: string, result?: RequestsResult): string {
  const path = `/comunidades/${communityId}/gestion/solicitudes`;
  return result ? `${path}?resultado=${result}` : path;
}
