// @vitest-environment node
import { NextRequest } from "next/server";
import { describe, expect, it } from "vitest";

import { proxy } from "./proxy";

function request(path: string, cookie?: string) {
  const headers = cookie ? { cookie } : undefined;
  return new NextRequest(new URL(path, "http://localhost:3000"), { headers });
}

describe("proxy", () => {
  it.each(["/", "/registro", "/iniciar-sesion"])("deja pasar la ruta pública %s sin cookie", (path) => {
    expect(proxy(request(path)).headers.get("location")).toBeNull();
  });

  it("redirige una ruta privada sin cookie al inicio de sesión con next", () => {
    const response = proxy(request("/comunidades/123/anuncios?page=2"));

    expect(response.status).toBe(307);
    const location = new URL(response.headers.get("location")!);
    expect(location.pathname).toBe("/iniciar-sesion");
    expect(location.searchParams.get("next")).toBe("/comunidades/123/anuncios?page=2");
  });

  it("deja pasar una ruta privada con cookie de sesión (el DAL valida el token)", () => {
    expect(proxy(request("/inicio", "ev_session=cualquier-valor")).headers.get("location")).toBeNull();
  });
});
