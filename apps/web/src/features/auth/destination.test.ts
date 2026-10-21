import { beforeEach, describe, expect, it, vi } from "vitest";

const { apiFetch } = vi.hoisted(() => ({ apiFetch: vi.fn() }));

vi.mock("@/lib/api/server", () => ({ apiFetch }));

import { postLoginPath } from "./destination";

function membership(id: string, isActive = true) {
  return { community: { id, is_active: isActive }, role: "member", status: "approved" };
}

function memberships(...items: ReturnType<typeof membership>[]) {
  return { ok: true, status: 200, data: { items } };
}

describe("postLoginPath", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("pide solo las membresías aprobadas con el token recibido", async () => {
    apiFetch.mockResolvedValue(memberships());

    await postLoginPath("jwt");

    expect(apiFetch).toHaveBeenCalledWith("/users/me/memberships?status=approved", { token: "jwt" });
  });

  it("lleva a /comunidades sin membresías aprobadas", async () => {
    apiFetch.mockResolvedValue(memberships());

    expect(await postLoginPath("jwt")).toBe("/comunidades");
  });

  it("lleva a /comunidades si la única comunidad está desactivada", async () => {
    apiFetch.mockResolvedValue(memberships(membership("c1", false)));

    expect(await postLoginPath("jwt")).toBe("/comunidades");
  });

  it("lleva a /inicio con alguna comunidad", async () => {
    apiFetch.mockResolvedValue(memberships(membership("c1"), membership("c2")));

    expect(await postLoginPath("jwt")).toBe("/inicio");
  });

  it("lleva a /inicio si la API falla", async () => {
    apiFetch.mockResolvedValue({ ok: false, error: { status: 503, detail: null } });

    expect(await postLoginPath("jwt")).toBe("/inicio");
  });
});
