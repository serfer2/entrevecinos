import { beforeEach, describe, expect, it, vi } from "vitest";

const { apiFetch, getSessionToken, redirect } = vi.hoisted(() => ({
  apiFetch: vi.fn(),
  getSessionToken: vi.fn(),
  redirect: vi.fn((url: string) => {
    throw new Error(`NEXT_REDIRECT:${url}`);
  }),
}));

vi.mock("@/lib/api/server", () => ({ apiFetch }));
vi.mock("./session", () => ({ getSessionToken }));
vi.mock("next/navigation", () => ({ redirect }));

import { userApiFetch } from "./api";

describe("userApiFetch", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getSessionToken.mockResolvedValue("jwt");
  });

  it("añade el token de la sesión", async () => {
    apiFetch.mockResolvedValue({ ok: true, status: 200, data: { id: 1 } });

    const result = await userApiFetch("/x", { method: "POST", body: { a: 1 } });

    expect(apiFetch).toHaveBeenCalledWith("/x", { method: "POST", body: { a: 1 }, token: "jwt" });
    expect(result).toEqual({ ok: true, status: 200, data: { id: 1 } });
  });

  it("redirige si no hay sesión o la API responde 401", async () => {
    getSessionToken.mockResolvedValueOnce(undefined);
    await expect(userApiFetch("/x")).rejects.toThrow("NEXT_REDIRECT:/iniciar-sesion?motivo=sesion-caducada");

    apiFetch.mockResolvedValue({ ok: false, error: { status: 401, detail: null } });
    await expect(userApiFetch("/x")).rejects.toThrow("NEXT_REDIRECT");
  });

  it("devuelve el resto de errores", async () => {
    apiFetch.mockResolvedValue({ ok: false, error: { status: 404, detail: "x" } });

    expect(await userApiFetch("/x")).toEqual({ ok: false, error: { status: 404, detail: "x" } });
  });
});
