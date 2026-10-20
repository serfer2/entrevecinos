import { describe, expect, it } from "vitest";

import { communitySchema } from "./schemas";

const valid = { name: "Los Olivos", description: "", city: "", postal_code: "" };

describe("communitySchema", () => {
  it("recorta y convierte los opcionales vacíos en null", () => {
    expect(communitySchema.parse({ ...valid, name: "  Los Olivos ", city: " Majadahonda " })).toEqual({
      name: "Los Olivos",
      description: null,
      city: "Majadahonda",
      postal_code: null,
    });
  });

  it.each([
    [{ name: "   " }, "name", "El nombre de la comunidad es obligatorio."],
    [{ name: "x".repeat(121) }, "name", "Máximo 120 caracteres."],
    [{ description: "x".repeat(2001) }, "description", "Máximo 2000 caracteres."],
    [{ city: "x".repeat(121) }, "city", "Máximo 120 caracteres."],
    [{ postal_code: "1".repeat(17) }, "postal_code", "Máximo 16 caracteres."],
  ])("rechaza %o", (override, field, message) => {
    const result = communitySchema.safeParse({ ...valid, ...override });

    expect(result.success).toBe(false);
    expect(result.error?.issues[0]).toMatchObject({ path: [field], message });
  });
});
