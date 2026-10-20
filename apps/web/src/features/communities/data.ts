import "server-only";

import { notFound } from "next/navigation";
import { cache } from "react";

import { userApiFetch } from "@/features/auth/api";
import type { ApiPage } from "@/lib/api/types";
import { isUuid } from "@/lib/forms";

import { type CommunitySearch, searchQuery } from "./search";
import type { ApiCommunity, ApiMembership, ApiMyMembership, MembershipStatus } from "./types";

/** Comunidad activa o `notFound()`. Memorizada durante la petición. */
export const getCommunity = cache(async (communityId: string): Promise<ApiCommunity> => {
  if (!isUuid(communityId)) notFound();
  const result = await userApiFetch<ApiCommunity>(`/communities/${communityId}`);
  if (result.ok) return result.data;
  if (result.error.status === 404) notFound();
  throw new Error(`No se pudo cargar la comunidad (estado ${result.error.status})`);
});

/** Membresías del usuario de la sesión, en cualquier estado. */
export const getMyMemberships = cache(async (): Promise<ApiMyMembership[]> => {
  const result = await userApiFetch<{ items: ApiMyMembership[] }>("/users/me/memberships");
  if (result.ok) return result.data.items;
  throw new Error(`No se pudieron cargar tus comunidades (estado ${result.error.status})`);
});

export async function getMyMembership(communityId: string): Promise<ApiMyMembership | undefined> {
  return (await getMyMemberships()).find((m) => m.community.id === communityId);
}

export async function searchCommunities(search: CommunitySearch): Promise<ApiPage<ApiCommunity>> {
  const result = await userApiFetch<ApiPage<ApiCommunity>>(`/communities?${searchQuery(search)}`);
  if (result.ok) return result.data;
  throw new Error(`No se pudo buscar comunidades (estado ${result.error.status})`);
}

export type CommunityMembershipsResult =
  | { ok: true; page: ApiPage<ApiMembership> }
  | { ok: false; forbidden: true };

/** Membresías de la comunidad para su gestión. `forbidden` si la API responde 403. */
export async function getCommunityMemberships(
  communityId: string,
  params: { status?: MembershipStatus; page?: number },
): Promise<CommunityMembershipsResult> {
  if (!isUuid(communityId)) notFound();
  const query = new URLSearchParams();
  if (params.status) query.set("status", params.status);
  if (params.page && params.page > 1) query.set("page", String(params.page));
  const result = await userApiFetch<ApiPage<ApiMembership>>(
    `/communities/${communityId}/memberships?${query}`,
  );
  if (result.ok) return { ok: true, page: result.data };
  if (result.error.status === 403) return { ok: false, forbidden: true };
  if (result.error.status === 404) notFound();
  throw new Error(`No se pudieron cargar las membresías (estado ${result.error.status})`);
}
