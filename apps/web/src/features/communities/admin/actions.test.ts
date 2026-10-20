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

import { reviewRequest } from "./actions";

const communityId = "0b5c4a7e-1d2f-4c3b-9a8e-7f6d5c4b3a21";
const userId = "1c6d5b8f-2e3a-4d4c-8b9f-8a7e6d5c4b32";
const path = `/comunidades/${communityId}/gestion/solicitudes`;

function form(decision: string, overrides: Record<string, string> = {}) {
  const data = new FormData();
  for (const [k, v] of Object.entries({ community_id: communityId, user_id: userId, decision, ...overrides })) {
    data.set(k, v);
  }
  return data;
}

describe("reviewRequest", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    requireUser.mockResolvedValue({ id: "admin" });
  });

  it.each([
    ["approved", "aprobada"],
    ["rejected", "rechazada"],
  ])("%s: envía la decisión y vuelve con el resultado", async (decision, result) => {
    userApiFetch.mockResolvedValue({ ok: true, status: 200, data: {} });

    await expect(reviewRequest(form(decision))).rejects.toThrow(`NEXT_REDIRECT:${path}?resultado=${result}`);
    expect(userApiFetch).toHaveBeenCalledWith(`/communities/${communityId}/memberships/${userId}`, {
      method: "PATCH",
      body: { status: decision },
    });
    expect(revalidatePath).toHaveBeenCalledWith(path);
  });

  it("409: ya revisada", async () => {
    userApiFetch.mockResolvedValue({ ok: false, error: { status: 409, detail: "x" } });

    await expect(reviewRequest(form("approved"))).rejects.toThrow(`${path}?resultado=revisada`);
  });

  it("403: vuelve a la página, que mostrará el aviso de permisos", async () => {
    userApiFetch.mockResolvedValue({ ok: false, error: { status: 403, detail: "x" } });

    await expect(reviewRequest(form("approved"))).rejects.toThrow(`NEXT_REDIRECT:${path}`);
  });

  it("error de red", async () => {
    userApiFetch.mockResolvedValue({ ok: false, error: { status: 0, detail: null } });

    await expect(reviewRequest(form("approved"))).rejects.toThrow(`${path}?resultado=error`);
  });

  it.each<Record<string, string>>([{ decision: "blocked" }, { user_id: "x" }, { community_id: "../x" }])(
    "no llama a la API con datos no válidos (%o)",
    async (overrides) => {
      await expect(reviewRequest(form("approved", overrides))).rejects.toThrow("NEXT_REDIRECT");
      expect(userApiFetch).not.toHaveBeenCalled();
    },
  );
});
