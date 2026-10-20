export type SearchParams = Record<string, string | string[] | undefined>;

/** Primer valor de un parámetro de la URL, recortado (`""` si falta). */
export function firstParam(params: SearchParams, name: string): string {
  const value = params[name];
  return (Array.isArray(value) ? value[0] : value)?.trim() ?? "";
}

/** Página de la URL: entero ≥ 1, o 1 si falta o no es válida. */
export function pageParam(params: SearchParams): number {
  const page = Number(firstParam(params, "page"));
  return Number.isInteger(page) && page >= 1 ? page : 1;
}
