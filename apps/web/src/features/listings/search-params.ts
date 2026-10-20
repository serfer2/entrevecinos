import { pageParam, type SearchParams } from "@/lib/search-params";

/** Parámetros del listado de una comunidad leídos de la URL (búsqueda, filtros y orden los amplían). */
export type ListingSearchParams = {
  page: number;
};

export function parseListingSearch(params: SearchParams): ListingSearchParams {
  return { page: pageParam(params) };
}

/** Query string para la API (`page_size` fijo de la interfaz). */
export function listingApiQuery(search: ListingSearchParams, pageSize: number): string {
  const query = new URLSearchParams({ page: String(search.page), page_size: String(pageSize) });
  return query.toString();
}

/** Enlace a otra página del listado conservando el resto de parámetros. */
export function listingSearchHref(communityId: string, search: ListingSearchParams, page: number): string {
  const query = new URLSearchParams();
  if (page > 1) query.set("page", String(page));
  const text = query.toString();
  return `/comunidades/${communityId}${text ? `?${text}` : ""}`;
}
