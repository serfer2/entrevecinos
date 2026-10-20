import { isUuid } from "@/lib/forms";
import { firstParam, pageParam, type SearchParams } from "@/lib/search-params";

import { LISTING_TYPES, type ListingType } from "./labels";

export const MIN_QUERY_LENGTH = 2;
export const MAX_QUERY_LENGTH = 160;
export const SHORT_QUERY_MESSAGE = "La búsqueda debe tener al menos 2 caracteres.";

/** Parámetros del listado de una comunidad leídos de la URL (el orden lo amplía). */
export type ListingSearchParams = {
  page: number;
  /** Búsqueda válida (≥ 2 caracteres) o `""`. */
  q: string;
  /** Lo escrito en el buscador, aunque no sea válido, para volver a mostrarlo. */
  qInput: string;
  /** Se escribió una búsqueda de un carácter: no se envía a la API. */
  qTooShort: boolean;
  type: ListingType | "";
  categoryId: string;
};

export function parseListingSearch(params: SearchParams): ListingSearchParams {
  const qInput = firstParam(params, "q").slice(0, MAX_QUERY_LENGTH);
  const qTooShort = qInput.length > 0 && qInput.length < MIN_QUERY_LENGTH;
  const type = firstParam(params, "type");
  const categoryId = firstParam(params, "category_id");
  return {
    page: pageParam(params),
    q: qTooShort ? "" : qInput,
    qInput,
    qTooShort,
    // Los valores no válidos se ignoran en lugar de provocar un error de la API.
    type: (LISTING_TYPES as readonly string[]).includes(type) ? (type as ListingType) : "",
    categoryId: isUuid(categoryId) ? categoryId : "",
  };
}

/** Si hay filtros de tipo o categoría (la búsqueda de texto va aparte). */
export function hasFilters(search: ListingSearchParams): boolean {
  return search.type !== "" || search.categoryId !== "";
}

/** Parámetros que definen el resultado (sin la página), con los nombres de la URL y de la API. */
export function listingCriteria(search: ListingSearchParams): URLSearchParams {
  const query = new URLSearchParams();
  if (search.q) query.set("q", search.q);
  if (search.type) query.set("type", search.type);
  if (search.categoryId) query.set("category_id", search.categoryId);
  return query;
}

/** Query string para la API (`page_size` fijo de la interfaz). */
export function listingApiQuery(search: ListingSearchParams, pageSize: number): string {
  const query = listingCriteria(search);
  query.set("page", String(search.page));
  query.set("page_size", String(pageSize));
  return query.toString();
}

/** Enlace a otra página del listado conservando la búsqueda y los filtros. */
export function listingSearchHref(communityId: string, search: ListingSearchParams, page: number): string {
  const query = listingCriteria(search);
  if (page > 1) query.set("page", String(page));
  const text = query.toString();
  return `/comunidades/${communityId}${text ? `?${text}` : ""}`;
}

/** Enlace sin la búsqueda de texto, conservando el resto de filtros. */
export function clearSearchHref(communityId: string, search: ListingSearchParams): string {
  return listingSearchHref(communityId, { ...search, q: "", qInput: "", qTooShort: false }, 1);
}

/** Enlace sin los filtros de tipo y categoría, conservando la búsqueda. */
export function clearFiltersHref(communityId: string, search: ListingSearchParams): string {
  return listingSearchHref(communityId, { ...search, type: "", categoryId: "" }, 1);
}
