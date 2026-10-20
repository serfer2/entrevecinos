import { beforeEach, describe, expect, it, vi } from "vitest";

const { apiFetch, requireUser, revalidatePath, redirect } = vi.hoisted(() => ({
  apiFetch: vi.fn(),
  requireUser: vi.fn(),
  revalidatePath: vi.fn(),
  redirect: vi.fn((url: string) => {
    throw new Error(`NEXT_REDIRECT:${url}`);
  }),
}));

vi.mock("@/lib/api/server", () => ({ apiFetch }));
vi.mock("@/features/auth/dal", () => ({ requireUser }));
vi.mock("@/features/auth/session", () => ({ getSessionToken: async () => "jwt" }));
vi.mock("next/cache", () => ({ revalidatePath }));
vi.mock("next/navigation", () => ({ redirect }));

import { updateProfile } from "./actions";

function form(values: Record<string, string>) {
  const data = new FormData();
  for (const [key, value] of Object.entries(values)) data.set(key, value);
  return data;
}

describe("updateProfile", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    requireUser.mockResolvedValue({ id: "u1", full_name: "Alex", email: "a@b.c", phone: null });
  });

  it("guarda, revalida /perfil y devuelve el mensaje de éxito", async () => {
    apiFetch.mockResolvedValue({
      ok: true,
      status: 200,
      data: { full_name: "Alex García", phone: null },
    });

    const state = await updateProfile(undefined, form({ full_name: " Alex García ", phone: "" }));

    expect(apiFetch).toHaveBeenCalledWith("/users/me", {
      method: "PATCH",
      body: { full_name: "Alex García", phone: null },
      token: "jwt",
    });
    expect(revalidatePath).toHaveBeenCalledWith("/perfil");
    expect(state).toEqual({
      success: "Perfil actualizado.",
      values: { full_name: "Alex García", phone: "" },
    });
  });

  it("comprueba la sesión antes de hacer nada", async () => {
    requireUser.mockRejectedValue(new Error("NEXT_REDIRECT:/iniciar-sesion?motivo=sesion-caducada"));

    await expect(updateProfile(undefined, form({ full_name: "Alex", phone: "" }))).rejects.toThrow(
      "NEXT_REDIRECT",
    );
    expect(apiFetch).not.toHaveBeenCalled();
  });

  it("no llama a la API con el nombre vacío y conserva lo escrito", async () => {
    const state = await updateProfile(undefined, form({ full_name: "   ", phone: "600111222" }));

    expect(apiFetch).not.toHaveBeenCalled();
    expect(state).toEqual({
      fieldErrors: { full_name: "El nombre es obligatorio." },
      values: { full_name: "   ", phone: "600111222" },
    });
  });

  it("redirige al inicio de sesión si la API responde 401", async () => {
    apiFetch.mockResolvedValue({ ok: false, error: { status: 401, detail: "x" } });

    await expect(updateProfile(undefined, form({ full_name: "Alex", phone: "" }))).rejects.toThrow(
      "NEXT_REDIRECT:/iniciar-sesion?motivo=sesion-caducada",
    );
  });

  it("traduce los campos de un 422", async () => {
    apiFetch.mockResolvedValue({
      ok: false,
      error: { status: 422, detail: [{ loc: ["body", "phone"], msg: "x", type: "x" }] },
    });

    const state = await updateProfile(undefined, form({ full_name: "Alex", phone: "600111222" }));

    expect(state?.fieldErrors).toEqual({ phone: "Introduce un teléfono válido." });
  });

  it("muestra un error general si la API no responde", async () => {
    apiFetch.mockResolvedValue({ ok: false, error: { status: 0, detail: null } });

    const state = await updateProfile(undefined, form({ full_name: "Alex", phone: "" }));

    expect(state?.formError).toBe("No se pudieron guardar los cambios. Inténtalo de nuevo.");
    expect(revalidatePath).not.toHaveBeenCalled();
  });
});
