/** Esquema `Community` de la API. */
export type ApiCommunity = {
  id: string;
  name: string;
  description: string | null;
  postal_code: string | null;
  city: string | null;
  created_by: string;
  is_active: boolean;
  created_at: string;
};

export type MembershipStatus = "pending" | "approved" | "rejected" | "blocked";
export type MembershipRole = "member" | "community_admin" | "moderator";

/** Esquema `MyMembership` de la API. */
export type ApiMyMembership = {
  community: ApiCommunity;
  role: MembershipRole;
  status: MembershipStatus;
  requested_at: string;
  joined_at: string | null;
};

/** Esquema `UserSummary` de la API. */
export type ApiUserSummary = {
  id: string;
  full_name: string;
  avatar_url: string | null;
};

/** Esquema `Membership` de la API. */
export type ApiMembership = {
  community_id: string;
  user: ApiUserSummary;
  role: MembershipRole;
  status: MembershipStatus;
  reviewed_by: string | null;
  requested_at: string;
  reviewed_at: string | null;
  joined_at: string | null;
};
