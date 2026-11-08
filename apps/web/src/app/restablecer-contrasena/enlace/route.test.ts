// @vitest-environment node
import { NextRequest } from "next/server";
import { beforeEach, describe, expect, it, vi } from "vitest";

const { cookieSet, apiFetch } = vi.hoisted(() => ({ cookieSet: vi.fn(), apiFetch: vi.fn() }));

vi.mock("next/headers", () => ({ cookies: async () => ({ set: cookieSet }) }));
vi.mock("@/lib/api/server", () => ({ apiFetch }));

import { GET } from "./route";

function call(query: string) {
  return GET(new NextRequest(`http://localhost:3000/restablecer-contrasena/enlace${query}`));
}

describe("GET /restablecer-contrasena/enlace", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("guarda el token en una cookie httpOnly y redirige a la página sin el token", async () => {
    const response = await call("?token=abc");

    expect(cookieSet).toHaveBeenCalledWith("ev_password_reset", "abc", {
      httpOnly: true,
      sameSite: "lax",
      secure: false,
      path: "/restablecer-contrasena",
      maxAge: 3600,
    });
    expect(response.status).toBe(303);
    expect(response.headers.get("location")).toBe("/restablecer-contrasena");
    expect(response.headers.get("cache-control")).toBe("no-store");
  });

  it("no llama a la API: un escáner de enlaces no consume nada", async () => {
    await call("?token=abc");

    expect(apiFetch).not.toHaveBeenCalled();
  });

  it.each(["", "?token=", `?token=${"a".repeat(257)}`])(
    "sin un token razonable (%s) explica que el enlace no es válido",
    async (query) => {
      const response = await call(query);

      expect(cookieSet).not.toHaveBeenCalled();
      expect(response.headers.get("location")).toBe("/restablecer-contrasena?motivo=invalido");
    },
  );
});
