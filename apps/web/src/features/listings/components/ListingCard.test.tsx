import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { ApiListing } from "../types";
import { ListingCard } from "./ListingCard";

const base: ApiListing = {
  id: "l1",
  community_id: "c1",
  owner: { id: "u1", full_name: "Ana", phone: null, email: "ana@example.com", avatar_url: null },
  category_id: "cat",
  title: "Bicicleta infantil",
  description: "Poco uso",
  type: "sell",
  price: 45.5,
  currency: "EUR",
  images: [
    { asset_id: "a2", url: "/v1/media/a2", position: 1, is_cover: false },
    { asset_id: "a1", url: "/v1/media/a1", position: 0, is_cover: true },
  ],
  status: "active",
  published_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

describe("ListingCard", () => {
  it("enlaza al detalle con portada, tipo, precio y fecha", () => {
    render(<ListingCard listing={base} />);

    expect(screen.getByRole("link").getAttribute("href")).toBe("/anuncios/l1");
    const image = screen.getByRole("img", { name: "Bicicleta infantil" });
    expect(image.getAttribute("src")).toBe("/media/a1");
    expect(image.getAttribute("loading")).toBe("lazy");
    expect(screen.getByText("Vendo")).toBeTruthy();
    expect(screen.getByText(/45,50/)).toBeTruthy();
    expect(screen.getByText("hoy").tagName).toBe("TIME");
  });

  it("sin imágenes muestra un marcador y sin precio no muestra importe", () => {
    render(<ListingCard listing={{ ...base, images: [], price: null, currency: null, type: "wanted" }} />);

    expect(screen.queryByRole("img")).toBeNull();
    expect(screen.queryByText(/€/)).toBeNull();
    expect(screen.queryByText("Gratis")).toBeNull();
  });

  it("regalo sin precio: «Gratis»; reservado: etiqueta", () => {
    render(<ListingCard listing={{ ...base, type: "free", price: null, currency: null, status: "reserved" }} />);

    expect(screen.getByText("Gratis")).toBeTruthy();
    expect(screen.getByText("Reservado")).toBeTruthy();
    expect(screen.getByText("Regalo")).toBeTruthy();
  });
});
