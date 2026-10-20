import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

const { getCommunityListings } = vi.hoisted(() => ({ getCommunityListings: vi.fn() }));
vi.mock("../data", () => ({ getCommunityListings }));

import { CommunityListings } from "./CommunityListings";

describe("CommunityListings", () => {
  it("estado vacío con invitación a publicar", async () => {
    getCommunityListings.mockResolvedValue({ items: [], page: 1, page_size: 24, total: 0 });

    render(await CommunityListings({ communityId: "c1", search: { page: 1 } }));

    expect(screen.getByText("Todavía no hay anuncios en esta comunidad.")).toBeTruthy();
    expect(screen.getByRole("link", { name: "Publica el primero" }).getAttribute("href")).toBe(
      "/comunidades/c1/anuncios/nuevo",
    );
  });

  it("tarjetas y paginación", async () => {
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
    getCommunityListings.mockResolvedValue({ items: [listing], page: 1, page_size: 24, total: 30 });

    render(await CommunityListings({ communityId: "c1", search: { page: 1 } }));

    expect(screen.getByText("Lámpara")).toBeTruthy();
    expect(screen.getByRole("link", { name: "Siguiente" }).getAttribute("href")).toBe("/comunidades/c1?page=2");
  });
});
