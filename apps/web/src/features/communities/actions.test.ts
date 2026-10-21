import { beforeEach, describe, expect, it, vi } from "vitest";

const { userApiFetch, requireUser, redirect, revalidatePath } = vi.hoisted(() => ({
  userApiFetch: vi.fn(),
  revalidatePath: vi.fn(),
  requireUser: vi.fn(),
  redirect: vi.fn((url: string) => {
    throw new Error(`NEXT_REDIRECT:${url}`);
  }),
}));

vi.mock("@/features/auth/api", () => ({ userApiFetch }));
vi.mock("@/features/auth/dal", () => ({ requireUser }));
vi.mock("next/navigation", () => ({ redirect }));
vi.mock("next/cache", () => ({ revalidatePath }));

import { createCommunity, requestAccess } from "./actions";

function form(values: Record<string, string>) {
  const data = new FormData();
  for (const [key, value] of Object.entries(values)) data.set(key, value);
  return data;
}

const filled = { name: "Los Olivos", description: "", city: "Majadahonda", postal_code: "28220" };

describe("createCommunity", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    requireUser.mockResolvedValue({ id: "u1" });
  });

  it("crea la comunidad y, si queda pendiente, avisa en /inicio", async () => {
    userApiFetch.mockResolvedValue({ ok: true, status: 201, data: { id: "c1", is_active: false } });

    await expect(createCommunity(undefined, form(filled))).rejects.toThrow(
      "NEXT_REDIRECT:/inicio?comunidad-pendiente=1",
    );
  });

  it("crea la comunidad y, si ya está activa, redirige a su página", async () => {
    userApiFetch.mockResolvedValue({ ok: true, status: 201, data: { id: "c1", is_active: true } });

    await expect(createCommunity(undefined, form(filled))).rejects.toThrow(
      "NEXT_REDIRECT:/comunidades/c1",
    );
    expect(userApiFetch).toHaveBeenCalledWith("/communities", {
      method: "POST",
      body: { name: "Los Olivos", description: null, city: "Majadahonda", postal_code: "28220" },
    });
  });

  it("avisa si ya hay una comunidad pendiente (409) y conserva los valores", async () => {
    userApiFetch.mockResolvedValue({ ok: false, error: { status: 409, detail: "x" } });

    expect(await createCommunity(undefined, form(filled))).toEqual({
      formError: "Ya tienes una comunidad pendiente de aprobación.",
      values: filled,
    });
  });

  it("comprueba la sesión antes de hacer nada", async () => {
    requireUser.mockRejectedValue(new Error("NEXT_REDIRECT:/iniciar-sesion?motivo=sesion-caducada"));

    await expect(createCommunity(undefined, form(filled))).rejects.toThrow("NEXT_REDIRECT");
    expect(userApiFetch).not.toHaveBeenCalled();
  });

  it("no llama a la API sin nombre y conserva lo escrito", async () => {
    const state = await createCommunity(undefined, form({ ...filled, name: "  " }));

    expect(userApiFetch).not.toHaveBeenCalled();
    expect(state).toEqual({
      fieldErrors: { name: "El nombre de la comunidad es obligatorio." },
      values: { ...filled, name: "  " },
    });
  });

  it("traduce los campos de un 422", async () => {
    userApiFetch.mockResolvedValue({
      ok: false,
      error: { status: 422, detail: [{ loc: ["body", "city"], msg: "x", type: "x" }] },
    });

    const state = await createCommunity(undefined, form(filled));

    expect(state?.fieldErrors).toEqual({ city: "Máximo 120 caracteres." });
  });

  it("muestra un error general si la API falla", async () => {
    userApiFetch.mockResolvedValue({ ok: false, error: { status: 0, detail: null } });

    const state = await createCommunity(undefined, form(filled));

    expect(state?.formError).toBe("No se pudo crear la comunidad. Inténtalo de nuevo.");
  });
});

describe("requestAccess", () => {
  const communityId = "0b5c4a7e-1d2f-4c3b-9a8e-7f6d5c4b3a21";

  beforeEach(() => {
    vi.clearAllMocks();
    requireUser.mockResolvedValue({ id: "u1" });
  });

  it.each([201, 409])("con %i revalida las páginas sin error", async (status) => {
    userApiFetch.mockResolvedValue(
      status === 201 ? { ok: true, status, data: {} } : { ok: false, error: { status, detail: "x" } },
    );

    const state = await requestAccess(undefined, form({ community_id: communityId }));

    expect(state).toBeUndefined();
    expect(userApiFetch).toHaveBeenCalledWith(`/communities/${communityId}/memberships`, {
      method: "POST",
    });
    expect(revalidatePath).toHaveBeenCalledWith("/comunidades");
    expect(revalidatePath).toHaveBeenCalledWith("/inicio");
  });

  it("404: la comunidad ya no está disponible", async () => {
    userApiFetch.mockResolvedValue({ ok: false, error: { status: 404, detail: "x" } });

    expect(await requestAccess(undefined, form({ community_id: communityId }))).toEqual({
      error: "Esta comunidad ya no está disponible.",
    });
    expect(revalidatePath).not.toHaveBeenCalled();
  });

  it("error de red: mensaje general", async () => {
    userApiFetch.mockResolvedValue({ ok: false, error: { status: 0, detail: null } });

    expect(await requestAccess(undefined, form({ community_id: communityId }))).toEqual({
      error: "No se pudo enviar la solicitud. Inténtalo de nuevo.",
    });
  });

  it("no llama a la API con un id no válido", async () => {
    await requestAccess(undefined, form({ community_id: "../users" }));

    expect(userApiFetch).not.toHaveBeenCalled();
  });
});
