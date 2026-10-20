import "server-only";

import { notFound } from "next/navigation";
import { cache } from "react";

import { userApiFetch } from "@/features/auth/api";

import type { ApiPage } from "@/lib/api/types";
import { isUuid } from "@/lib/forms";

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

export type ListingResult = { ok: true; listing: ApiListing } | { ok: false; forbidden: true };

/** Detalle de un anuncio: `notFound()` si no existe o no está disponible; `forbidden` con 403. */
export const getListing = cache(async (listingId: string): Promise<ListingResult> => {
  if (!isUuid(listingId)) notFound();
  const result = await userApiFetch<ApiListing>(`/listings/${listingId}`);
  if (result.ok) return { ok: true, listing: result.data };
  if (result.error.status === 403) return { ok: false, forbidden: true };
  if (result.error.status === 404) notFound();
  throw new Error(`No se pudo cargar el anuncio (estado ${result.error.status})`);
});
