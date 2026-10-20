import { describe, expect, it } from "vitest";

import { parseCommunitySearch, searchHref, searchQuery } from "./search";

describe("parseCommunitySearch", () => {
  it("recorta los valores y usa la página 1 por defecto", () => {
    expect(parseCommunitySearch({ q: " olivos ", city: ["Majadahonda", "x"] })).toEqual({
      q: "olivos",
      city: "Majadahonda",
      postal_code: "",
      page: 1,
    });
  });

  it.each(["0", "-1", "abc", "1.5", ""])("ignora la página %s", (page) => {
    expect(parseCommunitySearch({ page }).page).toBe(1);
  });

  it("ignora valores más largos que el contrato", () => {
    expect(parseCommunitySearch({ q: "x".repeat(161), postal_code: "1".repeat(17) })).toMatchObject({
      q: "",
      postal_code: "",
    });
  });
});

describe("searchQuery y searchHref", () => {
  const search = { q: "olivos", city: "", postal_code: "28220", page: 3 };

  it("solo incluye los filtros no vacíos", () => {
    expect(searchQuery(search)).toBe("q=olivos&postal_code=28220&page=3");
  });

  it("construye el enlace de otra página", () => {
    expect(searchHref(search, 1)).toBe("/comunidades?q=olivos&postal_code=28220");
    expect(searchHref({ q: "", city: "", postal_code: "", page: 1 }, 1)).toBe("/comunidades");
  });
});
