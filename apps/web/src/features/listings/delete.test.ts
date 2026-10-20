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

import { deleteListing } from "./actions";

const id = "0b5c4a7e-1d2f-4c3b-9a8e-7f6d5c4b3a21";
const form = (listingId = id) => {
  const data = new FormData();
  data.set("listing_id", listingId);
  return data;
};
const found = { ok: true, status: 200, data: { id, community_id: "c1" } };
const fail = (status: number) => ({ ok: false, error: { status, detail: null } });

describe("deleteListing", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    requireUser.mockResolvedValue({ id: "u1" });
  });

  it("204: vuelve a la comunidad del anuncio con el mensaje", async () => {
    userApiFetch.mockResolvedValueOnce(found).mockResolvedValueOnce({ ok: true, status: 204, data: null });

    await expect(deleteListing(form())).rejects.toThrow("NEXT_REDIRECT:/comunidades/c1?eliminado=1");
    expect(userApiFetch).toHaveBeenLastCalledWith(`/listings/${id}`, { method: "DELETE" });
    expect(revalidatePath).toHaveBeenCalledWith("/comunidades/c1");
  });

  it("404 al borrar: ya no estaba disponible", async () => {
    userApiFetch.mockResolvedValueOnce(found).mockResolvedValueOnce(fail(404));

    await expect(deleteListing(form())).rejects.toThrow("/comunidades/c1?no-disponible=1");
  });

  it("404 al leer: vuelve al inicio", async () => {
    userApiFetch.mockResolvedValueOnce(fail(404));

    await expect(deleteListing(form())).rejects.toThrow("NEXT_REDIRECT:/inicio?no-disponible=1");
  });

  it.each([
    [403, "eliminar-permiso"],
    [0, "eliminar"],
  ])("%i: se queda en el detalle con el error", async (status, error) => {
    userApiFetch.mockResolvedValueOnce(found).mockResolvedValueOnce(fail(status));

    await expect(deleteListing(form())).rejects.toThrow(`NEXT_REDIRECT:/anuncios/${id}?error=${error}`);
  });

  it("id no válido: no llama a la API", async () => {
    await expect(deleteListing(form("../x"))).rejects.toThrow("NEXT_REDIRECT:/inicio");
    expect(userApiFetch).not.toHaveBeenCalled();
  });
});
