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

import { updateListing } from "./actions";
import type { ApiListing } from "./types";

const listingId = "0b5c4a7e-1d2f-4c3b-9a8e-7f6d5c4b3a21";
const [a, b] = ["1c6d5b8f-2e3a-4d4c-8b9f-8a7e6d5c4b32", "2d7e6c9a-3f4b-4e5d-9c0a-9b8f7e6d5c43"];
const current: ApiListing = {
  id: listingId,
  community_id: "c1",
  owner: { id: "u1", full_name: "Ana", phone: null, avatar_url: null },
  category_id: "3e8f7d0b-4a5c-4f6e-8d1b-0c9a8f7e6d54",
  title: "Bicicleta",
  description: "Poco uso",
  type: "sell",
  price: 45,
  currency: "EUR",
  images: [
    { asset_id: a, url: `/v1/media/${a}`, position: 0, is_cover: true },
    { asset_id: b, url: `/v1/media/${b}`, position: 1, is_cover: false },
  ],
  status: "active",
  published_at: "2026-10-01T10:00:00Z",
  updated_at: "2026-10-01T10:00:00Z",
};

function form(overrides: Record<string, string> = {}, images = [a, b]) {
  const data = new FormData();
  const values = {
    title: current.title,
    description: current.description,
    category_id: current.category_id,
    type: current.type,
    price: "45,00",
    ...overrides,
  };
  for (const [k, v] of Object.entries(values)) data.set(k, v);
  for (const id of images) data.append("image_asset_ids", id);
  return data;
}

const ok = (data: unknown) => ({ ok: true, status: 200, data });
const fail = (status: number, detail: unknown = "x") => ({ ok: false, error: { status, detail } });

describe("updateListing", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    requireUser.mockResolvedValue({ id: "u1" });
  });

  it("envía solo los campos cambiados y las imágenes si cambia el orden", async () => {
    userApiFetch.mockResolvedValueOnce(ok(current)).mockResolvedValue(ok(current));

    await expect(updateListing(listingId, undefined, form({ title: "Bici", price: "40" }, [b, a]))).rejects.toThrow(
      `NEXT_REDIRECT:/anuncios/${listingId}?actualizado=1`,
    );
    expect(userApiFetch).toHaveBeenNthCalledWith(2, `/listings/${listingId}`, {
      method: "PATCH",
      body: { title: "Bici", price: "40.00", currency: "EUR" },
    });
    expect(userApiFetch).toHaveBeenNthCalledWith(3, `/listings/${listingId}/images`, {
      method: "PUT",
      body: { images: [{ asset_id: b, is_cover: true }, { asset_id: a, is_cover: false }] },
    });
  });

  it("sin cambios no llama ni al PATCH ni al PUT", async () => {
    userApiFetch.mockResolvedValueOnce(ok(current));

    await expect(updateListing(listingId, undefined, form())).rejects.toThrow("actualizado=1");
    expect(userApiFetch).toHaveBeenCalledTimes(1);
  });

  it("valida antes de llamar a la API", async () => {
    const state = await updateListing(listingId, undefined, form({ title: " " }));

    expect(state?.fieldErrors).toEqual({ title: "El título es obligatorio." });
    expect(userApiFetch).not.toHaveBeenCalled();
  });

  it("422 de la API: errores por campo", async () => {
    userApiFetch
      .mockResolvedValueOnce(ok(current))
      .mockResolvedValueOnce(fail(422, [{ loc: ["body", "category_id"], msg: "x", type: "x" }]));

    expect((await updateListing(listingId, undefined, form({ title: "Otro" })))?.fieldErrors).toEqual({
      category_id: "Elige una categoría.",
    });
  });

  it("403: solo el autor, o el motivo del bloqueo", async () => {
    userApiFetch.mockResolvedValueOnce(ok(current)).mockResolvedValueOnce(fail(403, "No tienes permisos."));
    expect((await updateListing(listingId, undefined, form({ title: "Otro" })))?.formError).toBe(
      "Solo quien publicó el anuncio puede editarlo.",
    );

    const retired = "Este anuncio ha sido retirado por la administración de la comunidad.";
    userApiFetch.mockResolvedValueOnce(ok(current)).mockResolvedValueOnce(fail(403, retired));
    expect((await updateListing(listingId, undefined, form({ title: "Otro" })))?.formError).toBe(retired);
  });

  it("fallo parcial: datos guardados pero no las fotografías", async () => {
    userApiFetch.mockResolvedValueOnce(ok(current)).mockResolvedValueOnce(ok(current)).mockResolvedValueOnce(fail(500));

    expect((await updateListing(listingId, undefined, form({ title: "Otro" }, [b])))?.formError).toBe(
      "Los datos se han guardado, pero no las fotografías. Inténtalo de nuevo.",
    );
  });
});
