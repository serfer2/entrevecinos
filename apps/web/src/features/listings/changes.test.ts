import { describe, expect, it } from "vitest";

import { imagesChanged, listingChanges, listingFormValuesOf } from "./changes";
import { listingSchema } from "./schemas";
import type { ApiListing } from "./types";

const current: ApiListing = {
  id: "l1",
  community_id: "c1",
  owner: { id: "u1", full_name: "Ana", phone: null, avatar_url: null },
  category_id: "0b5c4a7e-1d2f-4c3b-9a8e-7f6d5c4b3a21",
  title: "Bicicleta",
  description: "Poco uso",
  type: "sell",
  price: 45.5,
  currency: "EUR",
  images: [
    { asset_id: "1c6d5b8f-2e3a-4d4c-8b9f-8a7e6d5c4b32", url: "/v1/media/a", position: 0, is_cover: true },
    { asset_id: "2d7e6c9a-3f4b-4e5d-9c0a-9b8f7e6d5c43", url: "/v1/media/b", position: 1, is_cover: false },
  ],
  status: "active",
  published_at: "2026-10-01T10:00:00Z",
  updated_at: "2026-10-01T10:00:00Z",
};

const parse = (overrides: Partial<ReturnType<typeof listingFormValuesOf>> = {}) =>
  listingSchema.parse({ ...listingFormValuesOf(current), ...overrides });

describe("listingFormValuesOf", () => {
  it("precarga el precio con coma y las imágenes en orden", () => {
    expect(listingFormValuesOf(current)).toMatchObject({ price: "45,50", image_asset_ids: [current.images[0].asset_id, current.images[1].asset_id] });
  });
});

describe("listingChanges", () => {
  it("sin cambios", () => {
    expect(listingChanges(current, parse())).toEqual({});
  });

  it("solo el precio (y la moneda actual)", () => {
    expect(listingChanges(current, parse({ price: "40" }))).toEqual({ price: "40.00", currency: "EUR" });
  });

  it("borrar el precio", () => {
    expect(listingChanges(current, parse({ price: "" }))).toEqual({ price: null });
  });

  it("título y tipo", () => {
    expect(listingChanges(current, parse({ title: "Bici", type: "free" }))).toEqual({ title: "Bici", type: "free" });
  });
});

describe("imagesChanged", () => {
  const [a, b] = current.images.map((i) => i.asset_id);

  it("mismo orden y portada → sin cambios", () => {
    expect(imagesChanged(current, [a, b])).toBe(false);
  });

  it.each([[[b, a]], [[a]], [[a, b, "otra"]], [[]]])("cambia con %o", (ids) => {
    expect(imagesChanged(current, ids)).toBe(true);
  });

  it("portada que no es la primera → cambio", () => {
    const wrongCover = { ...current, images: current.images.map((i) => ({ ...i, is_cover: i.position === 1 })) };

    expect(imagesChanged(wrongCover, [a, b])).toBe(true);
  });
});
