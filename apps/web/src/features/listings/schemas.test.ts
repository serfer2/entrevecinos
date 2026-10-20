import { describe, expect, it } from "vitest";

import { listingBody, listingSchema } from "./schemas";

const valid = {
  title: " Bicicleta ",
  description: "Poco uso",
  category_id: "0b5c4a7e-1d2f-4c3b-9a8e-7f6d5c4b3a21",
  type: "sell",
  price: "",
  image_asset_ids: [],
};

describe("listingSchema", () => {
  it.each([
    ["", null],
    ["12,50", "12.50"],
    ["12.5", "12.50"],
    ["0", "0.00"],
    ["45", "45.00"],
  ])("precio %s → %s", (input, expected) => {
    expect(listingSchema.parse({ ...valid, price: input }).price).toBe(expected);
  });

  it.each(["-1", "1,234", "abc", "1.2.3", "123456789"])("rechaza el precio %s", (input) => {
    const result = listingSchema.safeParse({ ...valid, price: input });

    expect(result.error?.issues[0]).toMatchObject({ path: ["price"], message: "Introduce un precio válido." });
  });

  it("exige título, descripción, categoría y tipo", () => {
    const result = listingSchema.safeParse({ ...valid, title: " ", description: "", category_id: "", type: "" });

    expect(Object.fromEntries(result.error!.issues.map((i) => [i.path[0], i.message]))).toEqual({
      title: "El título es obligatorio.",
      description: "La descripción es obligatoria.",
      category_id: "Elige una categoría.",
      type: "Elige el tipo de anuncio.",
    });
  });

  it("como mucho 10 fotografías", () => {
    const ids = Array.from({ length: 11 }, () => valid.category_id);

    expect(listingSchema.safeParse({ ...valid, image_asset_ids: ids }).success).toBe(false);
  });

  it("añade EUR solo si hay precio", () => {
    expect(listingBody(listingSchema.parse({ ...valid, price: "5" }))).toMatchObject({ price: "5.00", currency: "EUR" });
    expect(listingBody(listingSchema.parse(valid))).toMatchObject({ price: null, currency: null });
  });
});
