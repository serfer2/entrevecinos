import type { ApiUser } from "@/features/auth/types";

import type { ApiMyMembership } from "./types";

type Viewer = Pick<ApiUser, "platform_role">;
type Membership = Pick<ApiMyMembership, "status" | "role"> | undefined;

/**
 * Acceso a los anuncios de la comunidad, como `CommunityAccess.require_member` de la API: membresía
 * aprobada o `platform_admin` (aunque no tenga membresía o la suya siga pendiente).
 */
export function canAccessCommunity(user: Viewer, membership: Membership): boolean {
  return user.platform_role === "platform_admin" || membership?.status === "approved";
}

/** Gestión de la comunidad (solicitudes y miembros): `community_admin` aprobado o `platform_admin`. */
export function canManageCommunity(user: Viewer, membership: Membership): boolean {
  return (
    user.platform_role === "platform_admin" ||
    (membership?.status === "approved" && membership.role === "community_admin")
  );
}
