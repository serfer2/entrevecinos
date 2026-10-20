export type CommunitySearch = {
  q: string;
  city: string;
  postal_code: string;
  page: number;
};

import { firstParam, pageParam, type SearchParams } from "@/lib/search-params";

const LIMITS = { q: 160, city: 120, postal_code: 16 } as const;

/** Filtros de `/comunidades` leídos de la URL. Los valores no válidos se ignoran. */
export function parseCommunitySearch(params: SearchParams): CommunitySearch {
  const text = (name: keyof typeof LIMITS) => {
    const value = firstParam(params, name);
    return value.length <= LIMITS[name] ? value : "";
  };
  return {
    q: text("q"),
    city: text("city"),
    postal_code: text("postal_code"),
    page: pageParam(params),
  };
}

/** Query string con los filtros no vacíos (y la página si no es la primera). */
export function searchQuery(search: CommunitySearch, page = search.page): string {
  const query = new URLSearchParams();
  for (const name of ["q", "city", "postal_code"] as const) {
    if (search[name]) query.set(name, search[name]);
  }
  if (page > 1) query.set("page", String(page));
  return query.toString();
}

export function searchHref(search: CommunitySearch, page: number): string {
  const query = searchQuery(search, page);
  return query ? `/comunidades?${query}` : "/comunidades";
}
