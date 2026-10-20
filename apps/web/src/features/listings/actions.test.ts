import { beforeEach, describe, expect, it, vi } from "vitest";

const { userApiFetch, requireUser, redirect, revalidatePath } = vi.hoisted(() => ({
  userApiFetch: vi.fn(),
  requireUser: vi.fn(),
  revalidatePath: vi.fn(),
  redirect: vi.fn((url: string) => {
    throw new Error(`NEXT_REDIRECT:${url}`);
  }),
}));

vi.mock("@/features/auth/api", () => ({ userApiFetch }));
vi.mock("@/features/auth/dal", () => ({ requireUser }));
vi.mock("next/navigation", () => ({ redirect }));
vi.mock("next/cache", () => ({ revalidatePath }));

import { publishListing } from "./actions";

const communityId = "0b5c4a7e-1d2f-4c3b-9a8e-7f6d5c4b3a21";
const categoryId = "1c6d5b8f-2e3a-4d4c-8b9f-8a7e6d5c4b32";
const imageIds = ["2d7e6c9a-3f4b-4e5d-9c0a-9b8f7e6d5c43", "3e8f7d0b-4a5c-4f6e-8d1b-0c9a8f7e6d54"];

function form(overrides: Record<string, string> = {}, images = imageIds) {
  const data = new FormData();
  const values = {
    title: "Bicicleta",
    description: "Poco uso",
    category_id: categoryId,
    type: "sell",
    price: "45,5",
    ...overrides,
  };
  for (const [k, v] of Object.entries(values)) data.set(k, v);
  for (const id of images) data.append("image_asset_ids", id);
  return data;
}

describe("publishListing", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    requireUser.mockResolvedValue({ id: "u1" });
  });

  it("publica con las imágenes en orden y vuelve a la comunidad", async () => {
    userApiFetch.mockResolvedValue({ ok: true, status: 201, data: { id: "l1" } });

    await expect(publishListing(communityId, undefined, form())).rejects.toThrow(
      `NEXT_REDIRECT:/comunidades/${communityId}?publicado=1`,
    );
    expect(userApiFetch).toHaveBeenCalledWith(`/communities/${communityId}/listings`, {
      method: "POST",
      body: {
        title: "Bicicleta",
        description: "Poco uso",
        category_id: categoryId,
        type: "sell",
        price: "45.50",
        currency: "EUR",
        image_asset_ids: imageIds,
      },
    });
  });

  it("regalo sin precio: sin moneda", async () => {
    userApiFetch.mockResolvedValue({ ok: true, status: 201, data: { id: "l1" } });

    await expect(publishListing(communityId, undefined, form({ type: "free", price: "" }))).rejects.toThrow();
    expect(userApiFetch.mock.calls[0][1].body).toMatchObject({ price: null, currency: null });
  });

  it("no llama a la API si faltan campos y conserva los valores y las imágenes", async () => {
    const state = await publishListing(communityId, undefined, form({ title: "" }));

    expect(userApiFetch).not.toHaveBeenCalled();
    expect(state?.fieldErrors).toEqual({ title: "El título es obligatorio." });
    expect(state?.values?.image_asset_ids).toEqual(imageIds);
  });

  it.each([
    ["pending", "Tu solicitud está pendiente de aprobación. Podrás publicar cuando un administrador la apruebe."],
    [undefined, "No tienes acceso para publicar en esta comunidad."],
  ])("403 con status %s", async (status, message) => {
    userApiFetch.mockResolvedValue({
      ok: false,
      error: { status: 403, detail: "x", payload: status ? { detail: "x", status } : { detail: "x" } },
    });

    expect((await publishListing(communityId, undefined, form()))?.formError).toBe(message);
  });

  it("400: alguna fotografía no es válida", async () => {
    userApiFetch.mockResolvedValue({ ok: false, error: { status: 400, detail: "x" } });

    const state = await publishListing(communityId, undefined, form());

    expect(state?.fieldErrors).toEqual({ image_asset_ids: "Alguna fotografía no es válida. Vuelve a subirla." });
  });

  it("422: errores por campo", async () => {
    userApiFetch.mockResolvedValue({
      ok: false,
      error: { status: 422, detail: [{ loc: ["body", "category_id"], msg: "x", type: "x" }] },
    });

    expect((await publishListing(communityId, undefined, form()))?.fieldErrors).toEqual({
      category_id: "Elige una categoría.",
    });
  });

  it("error de red", async () => {
    userApiFetch.mockResolvedValue({ ok: false, error: { status: 0, detail: null } });

    expect((await publishListing(communityId, undefined, form()))?.formError).toBe(
      "No se pudo publicar el anuncio. Inténtalo de nuevo.",
    );
  });
});
