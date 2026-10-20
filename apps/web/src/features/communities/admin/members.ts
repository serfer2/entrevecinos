import type { MembershipRole, MembershipStatus } from "../types";

/** Acciones de la gestión de miembros y el estado al que llevan (o `null` si eliminan). */
export const MEMBER_ACTIONS = {
  bloquear: { status: "blocked", done: "bloqueado" },
  desbloquear: { status: "approved", done: "desbloqueado" },
  expulsar: { status: null, done: "expulsado" },
} as const;

export type MemberAction = keyof typeof MEMBER_ACTIONS;

/** Mensajes de los 409 de la API, por código en la URL (nunca texto arbitrario en la URL). */
export const MEMBER_CONFLICTS = {
  "ultimo-admin": "La comunidad debe tener al menos un administrador.",
  admin: "No se puede bloquear a un administrador de la comunidad.",
  propio: "No puedes cambiar el estado de tu propia membresía.",
  "no-permitido": "Este cambio no está permitido para este miembro.",
  error: "No se pudo completar la acción. Inténtalo de nuevo.",
} as const;

export type MemberConflict = keyof typeof MEMBER_CONFLICTS;

export function conflictCode(detail: unknown): MemberConflict {
  if (typeof detail !== "string") return "error";
  if (detail.includes("al menos un administrador")) return "ultimo-admin";
  if (detail.includes("bloquear a un administrador")) return "admin";
  if (detail.includes("propia membresía")) return "propio";
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

/** Acciones disponibles para una fila de la tabla de miembros. */
export function rowActions(
  member: { status: MembershipStatus; role: MembershipRole; userId: string },
  currentUserId: string,
): MemberAction[] | "solicitud" {
  if (member.userId === currentUserId || member.role === "community_admin") return [];
  if (member.status === "pending") return "solicitud";
  if (member.status === "approved") return ["bloquear", "expulsar"];
  if (member.status === "blocked") return ["desbloquear", "expulsar"];
  return ["expulsar"];
}

export function membersPath(communityId: string, query?: Record<string, string>): string {
  const path = `/comunidades/${communityId}/gestion/miembros`;
  const text = new URLSearchParams(query).toString();
  return text ? `${path}?${text}` : path;
}
