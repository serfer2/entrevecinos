// @vitest-environment node
import { NextRequest } from "next/server";
import { beforeEach, describe, expect, it, vi } from "vitest";

const { apiRedirect, getSessionToken } = vi.hoisted(() => ({
  apiRedirect: vi.fn(),
  getSessionToken: vi.fn(),
}));

vi.mock("@/lib/api/server", () => ({ apiRedirect }));
vi.mock("@/features/auth/session", () => ({ getSessionToken }));

import { GET } from "./route";

const id = "0b5c4a7e-1d2f-4c3b-9a8e-7f6d5c4b3a21";

function call(assetId = id) {
  return GET(new NextRequest(`http://localhost:3000/media/${assetId}`), {
    params: Promise.resolve({ assetId }),
  });
}

describe("GET /media/[assetId]", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getSessionToken.mockResolvedValue("jwt");
  });

  it("reenvía la redirección a la URL prefirmada", async () => {
    apiRedirect.mockResolvedValue({ status: 302, location: "http://localhost:9000/b/k?sig" });

    const response = await call();

    expect(apiRedirect).toHaveBeenCalledWith(`/media/${id}`, "jwt");
    expect(response.status).toBe(302);
    expect(response.headers.get("location")).toBe("http://localhost:9000/b/k?sig");
    expect(response.headers.get("cache-control")).toBe("private, max-age=240");
  });

  it.each([403, 404])("%i de la API → 404", async (status) => {
    apiRedirect.mockResolvedValue({ status, location: null });

    expect((await call()).status).toBe(404);
  });

  it("id no válido → 404 sin llamar a la API", async () => {
    expect((await call("../users/me")).status).toBe(404);
    expect(apiRedirect).not.toHaveBeenCalled();
  });

  it("sin sesión → 401", async () => {
    getSessionToken.mockResolvedValue(undefined);

    expect((await call()).status).toBe(401);
  });
});
