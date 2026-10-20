import { describe, expect, it } from "vitest";

import {
  clearFiltersHref,
  clearSearchHref,
  hasFilters,
  listingApiQuery,
  listingSearchHref,
  parseListingSearch,
} from "./search-params";

const category = "0b5c4a7e-1d2f-4c3b-9a8e-7f6d5c4b3a21";

describe("ListingSearchParams", () => {
  it.each([
    [{}, 1],
    [{ page: "3" }, 3],
    [{ page: "0" }, 1],
    [{ page: "x" }, 1],
  ])("%o → página %i", (params, page) => {
    expect(parseListingSearch(params).page).toBe(page);
  });

  it("q recortado; vacío ignorado; de 1 carácter inválido; más de 160 recortado", () => {
    expect(parseListingSearch({ q: "  bici " })).toMatchObject({ q: "bici", qTooShort: false });
    expect(parseListingSearch({ q: "   " })).toMatchObject({ q: "", qInput: "", qTooShort: false });
    expect(parseListingSearch({ q: "a" })).toMatchObject({ q: "", qInput: "a", qTooShort: true });
    expect(parseListingSearch({ q: "x".repeat(200) }).q).toHaveLength(160);
  });

  it("type y category_id válidos; los inválidos se ignoran", () => {
    expect(parseListingSearch({ type: "sell", category_id: category })).toMatchObject({
      type: "sell",
      categoryId: category,
    });
    expect(parseListingSearch({ type: "rent", category_id: "x" })).toMatchObject({ type: "", categoryId: "" });
    expect(hasFilters(parseListingSearch({ type: "free" }))).toBe(true);
    expect(hasFilters(parseListingSearch({ q: "bici" }))).toBe(false);
  });

  it("construye la consulta a la API y los enlaces conservando los parámetros", () => {
    const search = parseListingSearch({ q: "bici roja", type: "sell", category_id: category, page: "2" });

    expect(listingApiQuery(search, 24)).toBe(
      `q=bici+roja&type=sell&category_id=${category}&sort=published_at&order=desc&page=2&page_size=24`,
    );
    expect(listingSearchHref("c1", search, 3)).toBe(`/comunidades/c1?q=bici+roja&type=sell&category_id=${category}&page=3`);
    expect(clearSearchHref("c1", search)).toBe(`/comunidades/c1?type=sell&category_id=${category}`);
    expect(clearFiltersHref("c1", search)).toBe("/comunidades/c1?q=bici+roja");
  });

  it("una búsqueda demasiado corta no llega a la API", () => {
    expect(listingApiQuery(parseListingSearch({ q: "a" }), 24)).toBe(
      "sort=published_at&order=desc&page=1&page_size=24",
    );
  });

  it.each([
    [undefined, "recientes", "sort=published_at&order=desc"],
    ["antiguos", "antiguos", "sort=published_at&order=asc"],
    ["precio-asc", "precio-asc", "sort=price&order=asc"],
    ["precio-desc", "precio-desc", "sort=price&order=desc"],
    ["barato", "recientes", "sort=published_at&order=desc"],
  ])("orden %s → %s (%s)", (orden, order, api) => {
    const search = parseListingSearch(orden ? { orden } : {});

    expect(search.order).toBe(order);
    expect(listingApiQuery(search, 24)).toBe(`${api}&page=1&page_size=24`);
  });

  it("conserva el orden en la paginación y al limpiar; el valor por defecto no va en la URL", () => {
    const search = parseListingSearch({ q: "bici", type: "free", orden: "precio-asc" });

    expect(listingSearchHref("c1", search, 2)).toBe("/comunidades/c1?q=bici&type=free&orden=precio-asc&page=2");
    expect(clearSearchHref("c1", search)).toBe("/comunidades/c1?type=free&orden=precio-asc");
    expect(clearFiltersHref("c1", search)).toBe("/comunidades/c1?q=bici&orden=precio-asc");
    expect(listingSearchHref("c1", parseListingSearch({ orden: "recientes" }), 1)).toBe("/comunidades/c1");
  });
});
