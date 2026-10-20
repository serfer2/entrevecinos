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

import { moderateListing } from "./actions";

const id = "0b5c4a7e-1d2f-4c3b-9a8e-7f6d5c4b3a21";
const form = (status: string, listingId = id) => {
  const data = new FormData();
  data.set("listing_id", listingId);
  data.set("status", status);
  return data;
};
const ok = { ok: true, status: 200, data: { id, community_id: "c1" } };
const fail = (status: number) => ({ ok: false, error: { status, detail: "x" } });

describe("moderateListing", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    requireUser.mockResolvedValue({ id: "admin" });
  });

  it("retirar: vuelve a la comunidad con el mensaje", async () => {
    userApiFetch.mockResolvedValue(ok);

    await expect(moderateListing(form("hidden"))).rejects.toThrow("NEXT_REDIRECT:/comunidades/c1?retirado=1");
    expect(userApiFetch).toHaveBeenCalledWith(`/listings/${id}/status`, { method: "PATCH", body: { status: "hidden" } });
    expect(revalidatePath).toHaveBeenCalledWith("/comunidades/c1");
  });

  it("restaurar: se queda en el detalle", async () => {
    userApiFetch.mockResolvedValue(ok);

    await expect(moderateListing(form("active"))).rejects.toThrow(`NEXT_REDIRECT:/anuncios/${id}?restaurado=1`);
  });

  it.each([
    [403, "moderar-permiso"],
    [409, "moderar-estado"],
    [0, "moderar"],
  ])("%i → error %s en el detalle", async (status, error) => {
    userApiFetch.mockResolvedValue(fail(status));

    await expect(moderateListing(form("hidden"))).rejects.toThrow(`NEXT_REDIRECT:/anuncios/${id}?error=${error}`);
  });

  it("estado no válido: no llama a la API", async () => {
    await expect(moderateListing(form("deleted"))).rejects.toThrow("error=moderar");
    expect(userApiFetch).not.toHaveBeenCalled();
  });
});
