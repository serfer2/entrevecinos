import { describe, expect, it } from "vitest";

import { listingApiQuery, listingSearchHref, parseListingSearch } from "./search-params";

describe("ListingSearchParams", () => {
  it.each([
    [{}, 1],
    [{ page: "3" }, 3],
    [{ page: "0" }, 1],
    [{ page: "x" }, 1],
  ])("%o → página %i", (params, page) => {
    expect(parseListingSearch(params).page).toBe(page);
  });

  it("construye la consulta y los enlaces", () => {
    expect(listingApiQuery({ page: 2 }, 24)).toBe("page=2&page_size=24");
    expect(listingSearchHref("c1", { page: 2 }, 1)).toBe("/comunidades/c1");
    expect(listingSearchHref("c1", { page: 1 }, 3)).toBe("/comunidades/c1?page=3");
  });
});
