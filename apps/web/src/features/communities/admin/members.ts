import type { MembershipRole, MembershipStatus } from "../types";

/**
 * Acciones de la gestión de miembros: cuerpo del `PATCH` (`null` si eliminan con `DELETE`) y
 * código del resultado en la URL. Las de rol solo las ofrece la página al `platform_admin` (HU-45).
 */
export const MEMBER_ACTIONS = {
  bloquear: { body: { status: "blocked" }, done: "bloqueado" },
  desbloquear: { body: { status: "approved" }, done: "desbloqueado" },
  expulsar: { body: null, done: "expulsado" },
  "nombrar-admin": { body: { role: "community_admin" }, done: "nombrado-admin" },
  "quitar-admin": { body: { role: "member" }, done: "quitado-admin" },
} as const;

export type MemberAction = keyof typeof MEMBER_ACTIONS;

/** Mensajes de los 409 de la API, por código en la URL (nunca texto arbitrario en la URL). */
export const MEMBER_CONFLICTS = {
  "ultimo-admin": "La comunidad debe tener al menos un administrador.",
  admin: "No se puede bloquear a un administrador de la comunidad.",
  propio: "No puedes cambiar el estado de tu propia membresía.",
  "solo-aprobados": "Solo se puede cambiar el rol de un miembro aprobado.",
  "no-permitido": "Este cambio no está permitido para este miembro.",
  error: "No se pudo completar la acción. Inténtalo de nuevo.",
} as const;

export type MemberConflict = keyof typeof MEMBER_CONFLICTS;

export function conflictCode(detail: unknown): MemberConflict {
  if (typeof detail !== "string") return "error";
  if (detail.includes("al menos un administrador")) return "ultimo-admin";
  if (detail.includes("bloquear a un administrador")) return "admin";
  if (detail.includes("propia membresía")) return "propio";
  if (detail.includes("miembro aprobado")) return "solo-aprobados";
  return "no-permitido";
}

/** Filtro por estado de la URL (`?estado=`), en español. */
export const STATUS_FILTERS = {
  pendiente: { status: "pending", label: "Pendientes" },
  miembro: { status: "approved", label: "Miembros" },
  bloqueado: { status: "blocked", label: "Bloqueados" },
  rechazado: { status: "rejected", label: "Rechazados" },
} as const satisfies Record<string, { status: MembershipStatus; label: string }>;

export type StatusFilter = keyof typeof STATUS_FILTERS;

export const STATUS_LABELS: Record<MembershipStatus, string> = {
  pending: "Pendiente",
  approved: "Miembro",
  blocked: "Bloqueado",
  rejected: "Rechazado",
};

export const ROLE_LABELS: Record<MembershipRole, string> = {
  member: "Miembro",
  moderator: "Moderador",
  community_admin: "Administrador",
};

/**
 * Acciones disponibles para una fila de la tabla de miembros. El `platform_admin` puede además
 * nombrar o quitar administradores de los miembros aprobados, incluida su propia fila (HU-45).
 */
export function rowActions(
  member: { status: MembershipStatus; role: MembershipRole; userId: string },
  currentUserId: string,
  isPlatformAdmin = false,
): MemberAction[] | "solicitud" {
  const roleActions: MemberAction[] =
    isPlatformAdmin && member.status === "approved"
      ? [member.role === "community_admin" ? "quitar-admin" : "nombrar-admin"]
      : [];
  if (member.userId === currentUserId || member.role === "community_admin") return roleActions;
  if (member.status === "pending") return "solicitud";
  if (member.status === "approved") return [...roleActions, "bloquear", "expulsar"];
  if (member.status === "blocked") return ["desbloquear", "expulsar"];
  return ["expulsar"];
}

export function membersPath(communityId: string, query?: Record<string, string>): string {
  const path = `/comunidades/${communityId}/gestion/miembros`;
  const text = new URLSearchParams(query).toString();
  return text ? `${path}?${text}` : path;
}
