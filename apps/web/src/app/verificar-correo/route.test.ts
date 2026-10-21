// @vitest-environment node
import { NextRequest } from "next/server";
import { beforeEach, describe, expect, it, vi } from "vitest";

const { apiFetch, createSession, getCurrentUser } = vi.hoisted(() => ({
  apiFetch: vi.fn(),
  createSession: vi.fn(),
  getCurrentUser: vi.fn(),
}));

vi.mock("@/lib/api/server", () => ({ apiFetch }));
vi.mock("@/features/auth/session", () => ({ createSession }));
vi.mock("@/features/auth/dal", () => ({ getCurrentUser }));

import { GET } from "./route";

function call(query = "?token=abc") {
  return GET(new NextRequest(`http://localhost:3000/verificar-correo${query}`));
}

function location(response: Response): string | null {
  return response.headers.get("location");
}

describe("GET /verificar-correo", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getCurrentUser.mockResolvedValue(null);
  });

  it("con 200 crea la sesión y lleva a /comunidades", async () => {
    apiFetch.mockResolvedValue({
      ok: true,
      status: 200,
      data: {
        access_token: "jwt",
        expires_in: 86400,
        token_type: "Bearer",
        user: {},
      },
    });

    const response = await call();

    expect(apiFetch).toHaveBeenCalledWith("/auth/email-verification", {
      method: "POST",
      body: { token: "abc" },
    });
    expect(createSession).toHaveBeenCalledWith("jwt", 86400);
    expect(response.status).toBe(303);
    expect(location(response)).toBe("/comunidades");
    expect(response.headers.get("cache-control")).toBe("no-store");
  });

  it("con 410 lleva a la página de enlace caducado con el correo", async () => {
    apiFetch.mockResolvedValue({
      ok: false,
      error: {
        status: 410,
        detail: "x",
        payload: { code: "verification_expired", email: "vecino@example.com" },
      },
    });

    const response = await call();

    expect(location(response)).toBe(
      "/verificar-correo/error?motivo=caducado&email=vecino%40example.com",
    );
    expect(createSession).not.toHaveBeenCalled();
  });

  it("con 400 y sin sesión pide iniciar sesión", async () => {
    apiFetch.mockResolvedValue({
      ok: false,
      error: { status: 400, detail: "x" },
    });

    expect(location(await call())).toBe("/iniciar-sesion?motivo=correo-validado");
  });

  it("con 400 y con sesión sigue a /comunidades", async () => {
    apiFetch.mockResolvedValue({
      ok: false,
      error: { status: 400, detail: "x" },
    });
    getCurrentUser.mockResolvedValue({ id: "u1" });

    expect(location(await call())).toBe("/comunidades");
  });

  it.each([0, 500])("con estado %i muestra el error genérico", async (status) => {
    apiFetch.mockResolvedValue({
      ok: false,
      error: { status, detail: null },
    });

    expect(location(await call())).toBe("/verificar-correo/error?motivo=error");
  });

  it("sin token no llama a la API", async () => {
    expect(location(await call(""))).toBe("/verificar-correo/error?motivo=invalido");
    expect(apiFetch).not.toHaveBeenCalled();
  });
});
