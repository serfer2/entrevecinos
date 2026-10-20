import { firstParam, pageParam, type SearchParams } from "@/lib/search-params";

export const MIN_QUERY_LENGTH = 2;
export const MAX_QUERY_LENGTH = 160;
export const SHORT_QUERY_MESSAGE = "La búsqueda debe tener al menos 2 caracteres.";

/** Parámetros del listado de una comunidad leídos de la URL (filtros y orden los amplían). */
export type ListingSearchParams = {
  page: number;
  /** Búsqueda válida (≥ 2 caracteres) o `""`. */
  q: string;
  /** Lo escrito en el buscador, aunque no sea válido, para volver a mostrarlo. */
  qInput: string;
  /** Se escribió una búsqueda de un carácter: no se envía a la API. */
  qTooShort: boolean;
};

export function parseListingSearch(params: SearchParams): ListingSearchParams {
  const qInput = firstParam(params, "q").slice(0, MAX_QUERY_LENGTH);
  const qTooShort = qInput.length > 0 && qInput.length < MIN_QUERY_LENGTH;
  return { page: pageParam(params), q: qTooShort ? "" : qInput, qInput, qTooShort };
}

/** Parámetros que definen el resultado (sin la página), en el orden de la URL. */
function criteria(search: ListingSearchParams): URLSearchParams {
  const query = new URLSearchParams();
  if (search.q) query.set("q", search.q);
  return query;
}

/** Query string para la API (`page_size` fijo de la interfaz). */
export function listingApiQuery(search: ListingSearchParams, pageSize: number): string {
  const query = criteria(search);
  query.set("page", String(search.page));
  query.set("page_size", String(pageSize));
  return query.toString();
}

/** Enlace a otra página del listado conservando la búsqueda y los filtros. */
export function listingSearchHref(communityId: string, search: ListingSearchParams, page: number): string {
  const query = criteria(search);
  if (page > 1) query.set("page", String(page));
  const text = query.toString();
  return `/comunidades/${communityId}${text ? `?${text}` : ""}`;
}

/** Enlace sin la búsqueda de texto, conservando el resto de filtros. */
export function clearSearchHref(communityId: string, search: ListingSearchParams): string {
  return listingSearchHref(communityId, { ...search, q: "", qInput: "", qTooShort: false }, 1);
}
