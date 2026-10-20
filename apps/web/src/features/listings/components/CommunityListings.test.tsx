import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const { getCommunityListings, getCategories, getMyMemberships } = vi.hoisted(() => ({
  getCommunityListings: vi.fn(),
  getCategories: vi.fn(),
  getMyMemberships: vi.fn(),
}));
vi.mock("../data", () => ({ getCommunityListings, getCategories }));
vi.mock("@/features/communities/data", () => ({ getMyMemberships }));

import { parseListingSearch } from "../search-params";
import { CommunityListings } from "./CommunityListings";

const sports = "0b5c4a7e-1d2f-4c3b-9a8e-7f6d5c4b3a21";
const listing = {
  id: "l1",
  community_id: "c1",
  owner: { id: "u1", full_name: "Ana", phone: null, email: "ana@example.com", avatar_url: null },
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
const membership = (id: string, name: string, status = "approved") => ({
  community: { id, name },
  role: "member",
  status,
  requested_at: "",
  joined_at: null,
});

async function renderListings(params: Record<string, string> = {}) {
  render(await CommunityListings({ communityId: "c1", search: parseListingSearch(params) }));
}

describe("CommunityListings", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getCategories.mockResolvedValue([{ id: sports, name: "Deporte y ocio", slug: "deporte-y-ocio", is_active: true }]);
    getMyMemberships.mockResolvedValue([membership("c1", "Los Olivos")]);
  });

  it("estado vacío con invitación a publicar", async () => {
    getCommunityListings.mockResolvedValue(page([], 0));

    await renderListings();

    expect(screen.getByText("Todavía no hay anuncios en esta comunidad.")).toBeTruthy();
    expect(screen.getByRole("link", { name: "Publica el primero" }).getAttribute("href")).toBe(
      "/comunidades/c1/anuncios/nuevo",
    );
  });

  it("tarjetas y paginación", async () => {
    getCommunityListings.mockResolvedValue(page([listing], 30));

    await renderListings();

    expect(screen.getByText("Lámpara")).toBeTruthy();
    expect(screen.getByRole("link", { name: "Siguiente" }).getAttribute("href")).toBe("/comunidades/c1?page=2");
  });

  it("con búsqueda: número de resultados y paginación que conserva q", async () => {
    getCommunityListings.mockResolvedValue(page([listing], 30));

    await renderListings({ q: "lampara" });

    expect(screen.getByText('30 resultados para "lampara"')).toBeTruthy();
    expect(screen.getByRole("link", { name: "Siguiente" }).getAttribute("href")).toBe("/comunidades/c1?q=lampara&page=2");
    expect(screen.getByRole("link", { name: "Limpiar búsqueda" }).getAttribute("href")).toBe("/comunidades/c1");
    expect((screen.getByRole("searchbox", { name: "Buscar anuncios" }) as HTMLInputElement).value).toBe("lampara");
  });

  it("sin resultados es distinto de una comunidad vacía", async () => {
    getCommunityListings.mockResolvedValue(page([], 0));

    await renderListings({ q: "patinete" });

    expect(screen.getByText('No hay anuncios que coincidan con "patinete".')).toBeTruthy();
    expect(screen.getByRole("link", { name: "Ver todos los anuncios" }).getAttribute("href")).toBe("/comunidades/c1");
    expect(screen.queryByText("Todavía no hay anuncios en esta comunidad.")).toBeNull();
  });

  it("búsqueda de un carácter: aviso y listado sin filtrar", async () => {
    getCommunityListings.mockResolvedValue(page([listing], 1));

    await renderListings({ q: "a" });

    expect(screen.getByText("La búsqueda debe tener al menos 2 caracteres.")).toBeTruthy();
    expect(screen.getByRole("searchbox").getAttribute("aria-invalid")).toBe("true");
    expect(getCommunityListings.mock.calls[0][1].q).toBe("");
    expect(screen.getByText("Lámpara")).toBeTruthy();
  });

  it("filtros: valores iniciales, filtros activos y «Limpiar filtros»", async () => {
    getCommunityListings.mockResolvedValue(page([], 0));

    await renderListings({ q: "bici", type: "sell", category_id: sports });

    expect((screen.getByLabelText("Tipo") as HTMLSelectElement).value).toBe("sell");
    expect((screen.getByLabelText("Categoría") as HTMLSelectElement).value).toBe(sports);
    expect(screen.getByText("Filtros activos: Vendo · Deporte y ocio")).toBeTruthy();
    expect(screen.getByText("No hay anuncios con estos filtros.")).toBeTruthy();
    const clear = screen.getAllByRole("link", { name: "Limpiar filtros" });
    expect(clear.every((link) => link.getAttribute("href") === "/comunidades/c1?q=bici")).toBe(true);
  });

  it("selector de comunidad: oculto con una sola, visible con dos conservando filtros", async () => {
    getCommunityListings.mockResolvedValue(page([listing], 1));
    await renderListings({ type: "sell" });
    expect(screen.queryByLabelText("Comunidad")).toBeNull();

    getMyMemberships.mockResolvedValue([
      membership("c1", "Los Olivos"),
      membership("c2", "El Pinar"),
      membership("c3", "Pendiente", "pending"),
    ]);
    const { container } = render(
      await CommunityListings({ communityId: "c1", search: parseListingSearch({ type: "sell" }) }),
    );

    const select = container.querySelector<HTMLSelectElement>("#community-switcher")!;
    expect(select.value).toBe("c1");
    expect(Array.from(select.options).map((o) => o.textContent)).toEqual(["Los Olivos", "El Pinar"]);
    expect(container.querySelector<HTMLInputElement>("form[action='/comunidades/ir'] input[name=type]")?.value).toBe("sell");
  });
});
