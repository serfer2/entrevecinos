import type { ApiCommunity, ApiMyMembership } from "./types";

/** Comunidad que el usuario creó y sigue pendiente de aprobación (como mucho hay una). */
export function pendingCommunityOf(
  memberships: ApiMyMembership[],
  userId: string,
): ApiCommunity | undefined {
  return memberships.find(
    ({ community }) => !community.is_active && community.created_by === userId,
  )?.community;
}
