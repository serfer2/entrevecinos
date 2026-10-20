import { describe, expect, it } from "vitest";

import { clearSearchHref, listingApiQuery, listingSearchHref, parseListingSearch } from "./search-params";

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

  it("construye la consulta a la API y los enlaces conservando q", () => {
    const search = parseListingSearch({ q: "bici roja", page: "2" });

    expect(listingApiQuery(search, 24)).toBe("q=bici+roja&page=2&page_size=24");
    expect(listingSearchHref("c1", search, 1)).toBe("/comunidades/c1?q=bici+roja");
    expect(listingSearchHref("c1", search, 3)).toBe("/comunidades/c1?q=bici+roja&page=3");
    expect(clearSearchHref("c1", search)).toBe("/comunidades/c1");
  });

  it("una búsqueda demasiado corta no llega a la API", () => {
    expect(listingApiQuery(parseListingSearch({ q: "a" }), 24)).toBe("page=1&page_size=24");
  });
});
