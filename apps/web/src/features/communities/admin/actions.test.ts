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

import { manageMember, reviewRequest } from "./actions";

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

describe("manageMember", () => {
  const members = `/comunidades/${communityId}/gestion/miembros`;

  function memberForm(action: string, overrides: Record<string, string> = {}) {
    const data = new FormData();
    const values = { community_id: communityId, user_id: userId, action, name: "Mario", ...overrides };
    for (const [k, v] of Object.entries(values)) data.set(k, v);
    return data;
  }

  beforeEach(() => {
    vi.clearAllMocks();
    requireUser.mockResolvedValue({ id: "admin" });
  });

  it.each([
    ["bloquear", "PATCH", { status: "blocked" }, "bloqueado"],
    ["desbloquear", "PATCH", { status: "approved" }, "desbloqueado"],
    ["expulsar", "DELETE", undefined, "expulsado"],
  ])("%s", async (action, method, body, done) => {
    userApiFetch.mockResolvedValue({ ok: true, status: 200, data: null });

    await expect(manageMember(memberForm(action))).rejects.toThrow(
      `NEXT_REDIRECT:${members}?resultado=${done}&nombre=Mario`,
    );
    expect(userApiFetch).toHaveBeenCalledWith(
      `/communities/${communityId}/memberships/${userId}`,
      body ? { method, body } : { method },
    );
  });

  it("409: código del conflicto en la URL", async () => {
    userApiFetch.mockResolvedValue({
      ok: false,
      error: { status: 409, detail: "La comunidad debe tener al menos un administrador." },
    });

    await expect(manageMember(memberForm("expulsar"))).rejects.toThrow(`${members}?error=ultimo-admin`);
  });

  it("403: vuelve a la página (aviso de permisos)", async () => {
    userApiFetch.mockResolvedValue({ ok: false, error: { status: 403, detail: "x" } });

    await expect(manageMember(memberForm("bloquear"))).rejects.toThrow(`NEXT_REDIRECT:${members}`);
  });

  it("acción o id no válidos: no llama a la API", async () => {
    await expect(manageMember(memberForm("borrar"))).rejects.toThrow(`${members}?error=error`);
    await expect(manageMember(memberForm("bloquear", { user_id: "x" }))).rejects.toThrow("error=error");
    expect(userApiFetch).not.toHaveBeenCalled();
  });
});
