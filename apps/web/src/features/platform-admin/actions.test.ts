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

import { approveCommunity, rejectCommunity } from "./actions";
import { PENDING_COMMUNITIES_ERRORS, PENDING_COMMUNITIES_RESULT_MESSAGES, pendingCommunitiesPath } from "./paths";

const COMMUNITY_ID = "6f1c2c5e-8f4b-4c1e-9a3d-2b7e5f0a1c9d";

function form(values: Record<string, string>) {
  const data = new FormData();
  for (const [key, value] of Object.entries(values)) data.set(key, value);
  return data;
}

describe("approveCommunity", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    requireUser.mockResolvedValue({ id: "u1", platform_role: "platform_admin" });
  });

  it("aprueba la comunidad y vuelve a la lista con el resultado", async () => {
    userApiFetch.mockResolvedValue({ ok: true, status: 200, data: { id: COMMUNITY_ID } });

    await expect(approveCommunity(form({ community_id: COMMUNITY_ID }))).rejects.toThrow(
      "NEXT_REDIRECT:/admin/comunidades?resultado=aprobada",
    );
    expect(userApiFetch).toHaveBeenCalledWith(`/admin/communities/${COMMUNITY_ID}`, {
      method: "PATCH",
      body: { is_active: true },
    });
    expect(revalidatePath).toHaveBeenCalledWith("/admin/comunidades");
  });

  it("muestra un error si la API falla", async () => {
    userApiFetch.mockResolvedValue({ ok: false, error: { status: 500, detail: null } });

    await expect(approveCommunity(form({ community_id: COMMUNITY_ID }))).rejects.toThrow(
      "NEXT_REDIRECT:/admin/comunidades?resultado=error",
    );
  });

  it("no llama a la API con un identificador no válido", async () => {
    await expect(approveCommunity(form({ community_id: "x" }))).rejects.toThrow(
      "NEXT_REDIRECT:/admin/comunidades?resultado=error",
    );
    expect(userApiFetch).not.toHaveBeenCalled();
  });
});

describe("rejectCommunity", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    requireUser.mockResolvedValue({ id: "u1", platform_role: "platform_admin" });
  });

  it("rechaza la comunidad y vuelve a la lista con su nombre", async () => {
    userApiFetch.mockResolvedValue({ ok: true, status: 204, data: null });

    await expect(
      rejectCommunity(form({ community_id: COMMUNITY_ID, name: "Los Pinos" })),
    ).rejects.toThrow("NEXT_REDIRECT:/admin/comunidades?resultado=rechazada&nombre=Los+Pinos");
    expect(userApiFetch).toHaveBeenCalledWith(`/admin/communities/${COMMUNITY_ID}`, {
      method: "DELETE",
    });
    expect(revalidatePath).toHaveBeenCalledWith("/admin/comunidades");
    expect(revalidatePath).toHaveBeenCalledWith("/inicio");
  });

  it.each([
    [409, "ya-activa"],
    [404, "no-existe"],
    [500, "error-rechazo"],
    [0, "error-rechazo"],
  ])("%i → %s", async (status, result) => {
    userApiFetch.mockResolvedValue({ ok: false, error: { status, detail: null } });

    await expect(rejectCommunity(form({ community_id: COMMUNITY_ID, name: "X" }))).rejects.toThrow(
      `NEXT_REDIRECT:/admin/comunidades?resultado=${result}`,
    );
  });

  it("no llama a la API con un identificador no válido", async () => {
    await expect(rejectCommunity(form({ community_id: "x" }))).rejects.toThrow(
      "NEXT_REDIRECT:/admin/comunidades?resultado=error-rechazo",
    );
    expect(userApiFetch).not.toHaveBeenCalled();
  });
});

describe("mensajes de comunidades pendientes", () => {
  it("incluye el nombre en el rechazo y marca los errores", () => {
    expect(PENDING_COMMUNITIES_RESULT_MESSAGES.rechazada("Los Pinos")).toBe(
      "Se ha rechazado la comunidad Los Pinos.",
    );
    expect(PENDING_COMMUNITIES_RESULT_MESSAGES.rechazada("")).toBe("Se ha rechazado la comunidad.");
    expect(PENDING_COMMUNITIES_RESULT_MESSAGES.aprobada()).toBe("Comunidad aprobada.");
    expect(PENDING_COMMUNITIES_ERRORS.has("ya-activa")).toBe(true);
    expect(PENDING_COMMUNITIES_ERRORS.has("rechazada")).toBe(false);
  });

  it("construye la ruta del resultado", () => {
    expect(pendingCommunitiesPath()).toBe("/admin/comunidades");
    expect(pendingCommunitiesPath("aprobada")).toBe("/admin/comunidades?resultado=aprobada");
  });
});
