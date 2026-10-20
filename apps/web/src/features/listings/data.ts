import "server-only";

import { cache } from "react";

import { userApiFetch } from "@/features/auth/api";

import type { ApiPage } from "@/lib/api/types";

import { listingApiQuery, type ListingSearchParams } from "./search-params";
import type { ApiCategory, ApiListing } from "./types";

export const getCategories = cache(async (): Promise<ApiCategory[]> => {
  const result = await userApiFetch<{ items: ApiCategory[] }>("/categories");
  if (result.ok) return result.data.items;
  throw new Error(`No se pudieron cargar las categorías (estado ${result.error.status})`);
});

export const LISTINGS_PAGE_SIZE = 24;

export async function getCommunityListings(
  communityId: string,
  search: ListingSearchParams,
): Promise<ApiPage<ApiListing>> {
  const result = await userApiFetch<ApiPage<ApiListing>>(
    `/communities/${communityId}/listings?${listingApiQuery(search, LISTINGS_PAGE_SIZE)}`,
  );
  if (result.ok) return result.data;
  throw new Error(`No se pudieron cargar los anuncios (estado ${result.error.status})`);
}
