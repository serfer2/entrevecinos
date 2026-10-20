// @vitest-environment node
import { beforeEach, describe, expect, it, vi } from "vitest";

const { apiFetch, cookieGet, redirect } = vi.hoisted(() => ({
  apiFetch: vi.fn(),
  cookieGet: vi.fn(),
  redirect: vi.fn((url: string) => {
    throw new Error(`NEXT_REDIRECT:${url}`);
  }),
}));

vi.mock("@/lib/api/server", () => ({ apiFetch }));
vi.mock("next/headers", () => ({ cookies: async () => ({ get: cookieGet }) }));
vi.mock("next/navigation", () => ({ redirect }));
// `cache` de React solo memoriza dentro de una petición de servidor; en las pruebas, sin efecto.
vi.mock("react", async (original) => ({ ...(await original()), cache: (fn: unknown) => fn }));

import { getCurrentUser, requireUser } from "./dal";

const apiUser = {
  id: "u1",
  email: "vecino@example.com",
  full_name: "Alex Vecino",
  phone: null,
  avatar_url: null,
  platform_role: "user",
  is_active: true,
  created_at: "2026-10-19T00:00:00Z",
};

describe("getCurrentUser", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    cookieGet.mockReturnValue({ value: "jwt" });
  });

  it("devuelve null sin cookie y no llama a la API", async () => {
    cookieGet.mockReturnValue(undefined);

    expect(await getCurrentUser()).toBeNull();
    expect(apiFetch).not.toHaveBeenCalled();
  });

  it("devuelve solo los datos que necesita la interfaz", async () => {
    apiFetch.mockResolvedValue({ ok: true, status: 200, data: apiUser });

    expect(await getCurrentUser()).toEqual({
      id: "u1",
      email: "vecino@example.com",
      full_name: "Alex Vecino",
      phone: null,
      platform_role: "user",
    });
    expect(apiFetch).toHaveBeenCalledWith("/users/me", { token: "jwt" });
  });

  it("devuelve null con un token que la API rechaza", async () => {
    apiFetch.mockResolvedValue({ ok: false, error: { status: 401, detail: "x" } });

    expect(await getCurrentUser()).toBeNull();
  });

  it("lanza un error si la API falla por otro motivo", async () => {
    apiFetch.mockResolvedValue({ ok: false, error: { status: 0, detail: null } });

    await expect(getCurrentUser()).rejects.toThrow();
  });

  it("requireUser redirige con el aviso de sesión caducada", async () => {
    apiFetch.mockResolvedValue({ ok: false, error: { status: 401, detail: "x" } });

    await expect(requireUser()).rejects.toThrow("NEXT_REDIRECT:/iniciar-sesion?motivo=sesion-caducada");
  });
});
