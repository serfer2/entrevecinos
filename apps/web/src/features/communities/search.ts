export type CommunitySearch = {
  q: string;
  city: string;
  postal_code: string;
  page: number;
};

type SearchParams = Record<string, string | string[] | undefined>;

const LIMITS = { q: 160, city: 120, postal_code: 16 } as const;

function single(params: SearchParams, name: string): string {
  const value = params[name];
  return (Array.isArray(value) ? value[0] : value)?.trim() ?? "";
}

/** Filtros de `/comunidades` leídos de la URL. Los valores no válidos se ignoran. */
export function parseCommunitySearch(params: SearchParams): CommunitySearch {
  const text = (name: keyof typeof LIMITS) => {
    const value = single(params, name);
    return value.length <= LIMITS[name] ? value : "";
  };
  const page = Number(single(params, "page"));
  return {
    q: text("q"),
    city: text("city"),
    postal_code: text("postal_code"),
    page: Number.isInteger(page) && page >= 1 ? page : 1,
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
