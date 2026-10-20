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

import { changeListingStatus } from "./actions";

const id = "0b5c4a7e-1d2f-4c3b-9a8e-7f6d5c4b3a21";
const form = (status: string) => {
  const data = new FormData();
  data.set("listing_id", id);
  data.set("status", status);
  return data;
};

describe("changeListingStatus", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    requireUser.mockResolvedValue({ id: "u1" });
  });

  it.each([
    ["reserved", "reservado"],
    ["active", "disponible"],
    ["completed", "finalizado"],
  ])("%s → vuelve al detalle con cambio=%s", async (status, result) => {
    userApiFetch.mockResolvedValue({ ok: true, status: 200, data: { id, community_id: "c1" } });

    await expect(changeListingStatus(form(status))).rejects.toThrow(`NEXT_REDIRECT:/anuncios/${id}?cambio=${result}`);
    expect(userApiFetch).toHaveBeenCalledWith(`/listings/${id}/status`, { method: "PATCH", body: { status } });
    expect(revalidatePath).toHaveBeenCalledWith("/comunidades/c1");
  });

  it.each([
    [403, "estado-permiso"],
    [409, "estado-conflicto"],
    [0, "estado"],
  ])("%i → error %s", async (code, error) => {
    userApiFetch.mockResolvedValue({ ok: false, error: { status: code, detail: "x" } });

    await expect(changeListingStatus(form("reserved"))).rejects.toThrow(`?error=${error}`);
  });

  it("estado no válido (p. ej. hidden): no llama a la API", async () => {
    await expect(changeListingStatus(form("hidden"))).rejects.toThrow("?error=estado");
    expect(userApiFetch).not.toHaveBeenCalled();
  });
});
