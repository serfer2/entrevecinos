import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

const { getCommunityListings } = vi.hoisted(() => ({ getCommunityListings: vi.fn() }));
vi.mock("../data", () => ({ getCommunityListings }));

import { parseListingSearch } from "../search-params";
import { CommunityListings } from "./CommunityListings";

const listing = {
  id: "l1",
  community_id: "c1",
  owner: { id: "u1", full_name: "Ana", phone: null, avatar_url: null },
  category_id: "cat",
  title: "Lámpara",
  description: "x",
  type: "sell",
  price: null,
  currency: null,
  images: [],
  status: "active",
  published_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

const page = (items: unknown[], total: number) => ({ items, page: 1, page_size: 24, total });

describe("CommunityListings", () => {
  it("estado vacío con invitación a publicar", async () => {
    getCommunityListings.mockResolvedValue(page([], 0));

    render(await CommunityListings({ communityId: "c1", search: parseListingSearch({}) }));

    expect(screen.getByText("Todavía no hay anuncios en esta comunidad.")).toBeTruthy();
    expect(screen.getByRole("link", { name: "Publica el primero" }).getAttribute("href")).toBe(
      "/comunidades/c1/anuncios/nuevo",
    );
  });

  it("tarjetas y paginación", async () => {
    getCommunityListings.mockResolvedValue(page([listing], 30));

    render(await CommunityListings({ communityId: "c1", search: parseListingSearch({}) }));

    expect(screen.getByText("Lámpara")).toBeTruthy();
    expect(screen.getByRole("link", { name: "Siguiente" }).getAttribute("href")).toBe("/comunidades/c1?page=2");
  });

  it("con búsqueda: número de resultados y paginación que conserva q", async () => {
    getCommunityListings.mockResolvedValue(page([listing], 30));

    render(await CommunityListings({ communityId: "c1", search: parseListingSearch({ q: "lampara" }) }));

    expect(screen.getByText('30 resultados para "lampara"')).toBeTruthy();
    expect(screen.getByRole("link", { name: "Siguiente" }).getAttribute("href")).toBe("/comunidades/c1?q=lampara&page=2");
    expect(screen.getByRole("link", { name: "Limpiar" }).getAttribute("href")).toBe("/comunidades/c1");
    expect((screen.getByRole("searchbox", { name: "Buscar anuncios" }) as HTMLInputElement).value).toBe("lampara");
  });

  it("sin resultados es distinto de una comunidad vacía", async () => {
    getCommunityListings.mockResolvedValue(page([], 0));

    render(await CommunityListings({ communityId: "c1", search: parseListingSearch({ q: "patinete" }) }));

    expect(screen.getByText('No hay anuncios que coincidan con "patinete".')).toBeTruthy();
    expect(screen.getByRole("link", { name: "Ver todos los anuncios" }).getAttribute("href")).toBe("/comunidades/c1");
    expect(screen.queryByText("Todavía no hay anuncios en esta comunidad.")).toBeNull();
  });

  it("búsqueda de un carácter: aviso y listado sin filtrar", async () => {
    getCommunityListings.mockResolvedValue(page([listing], 1));
    const search = parseListingSearch({ q: "a" });

    render(await CommunityListings({ communityId: "c1", search }));

    expect(screen.getByText("La búsqueda debe tener al menos 2 caracteres.")).toBeTruthy();
    expect(screen.getByRole("searchbox").getAttribute("aria-invalid")).toBe("true");
    expect(getCommunityListings).toHaveBeenLastCalledWith("c1", search);
    expect(screen.getByText("Lámpara")).toBeTruthy();
  });
});
