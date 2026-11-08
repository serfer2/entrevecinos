import { beforeEach, describe, expect, it, vi } from "vitest";

const { apiFetch, cookieGet, cookieDelete, redirect } = vi.hoisted(() => ({
  apiFetch: vi.fn(),
  cookieGet: vi.fn(),
  cookieDelete: vi.fn(),
  redirect: vi.fn((url: string) => {
    throw new Error(`NEXT_REDIRECT:${url}`);
  }),
}));

vi.mock("@/lib/api/server", () => ({ apiFetch }));
vi.mock("next/headers", () => ({
  cookies: async () => ({ get: cookieGet, delete: cookieDelete, set: vi.fn() }),
}));
vi.mock("next/navigation", () => ({ redirect }));

import { resetPassword } from "./actions";
import { isPublicRoute } from "./routes";

const PASSWORD = "OtraClaveSegura456!";

function form(password: string, confirm = password) {
  const data = new FormData();
  data.set("password", password);
  data.set("password_confirm", confirm);
  return data;
}

function withToken(token: string | undefined) {
  cookieGet.mockImplementation((name: string) =>
    name === "ev_password_reset" && token ? { name, value: token } : undefined,
  );
}

function apiError(status: number, payload: Record<string, unknown> = {}) {
  return { ok: false, error: { status, detail: payload.detail ?? null, payload } };
}

const resetCookie = { name: "ev_password_reset", path: "/restablecer-contrasena" };
const sessionCookie = { name: "ev_session", path: "/" };

describe("resetPassword", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    withToken("token-del-correo");
  });

  it("con 204 envía el token de la cookie, cierra la sesión y lleva al inicio de sesión", async () => {
    apiFetch.mockResolvedValue({ ok: true, status: 204, data: null });

    await expect(resetPassword(undefined, form(PASSWORD))).rejects.toThrow(
      "NEXT_REDIRECT:/iniciar-sesion?motivo=contrasena-cambiada",
    );

    expect(apiFetch).toHaveBeenCalledWith("/auth/password-reset/confirm", {
      method: "POST",
      body: { token: "token-del-correo", password: PASSWORD },
    });
    expect(cookieDelete).toHaveBeenCalledWith(resetCookie);
    expect(cookieDelete).toHaveBeenCalledWith(sessionCookie);
  });

  it("sin la cookie del enlace no llama a la API", async () => {
    withToken(undefined);

    expect(await resetPassword(undefined, form(PASSWORD))).toEqual({ linkError: "invalido" });
    expect(apiFetch).not.toHaveBeenCalled();
  });

  it("si las contraseñas no coinciden no llama a la API", async () => {
    const state = await resetPassword(undefined, form(PASSWORD, "OtraDistinta789!"));

    expect(state).toEqual({ fieldErrors: { password_confirm: "Las contraseñas no coinciden." } });
    expect(apiFetch).not.toHaveBeenCalled();
  });

  it("con una contraseña corta marca el campo sin llamar a la API", async () => {
    const state = await resetPassword(undefined, form("corta"));

    expect(state?.fieldErrors?.password).toBe("La contraseña debe tener al menos 12 caracteres.");
    expect(apiFetch).not.toHaveBeenCalled();
  });

  it.each([
    [410, "password_reset_expired", "caducado"],
    [400, "password_reset_invalid", "invalido"],
  ])("con %i borra la cookie y explica el enlace", async (status, code, reason) => {
    apiFetch.mockResolvedValue(apiError(status, { detail: "x", code }));

    expect(await resetPassword(undefined, form(PASSWORD))).toEqual({ linkError: reason });
    expect(cookieDelete).toHaveBeenCalledWith(resetCookie);
    expect(cookieDelete).not.toHaveBeenCalledWith(sessionCookie);
  });

  it("con 422 marca la contraseña y conserva la cookie", async () => {
    apiFetch.mockResolvedValue(
      apiError(422, { detail: [{ loc: ["body", "password"], msg: "x", type: "too_short" }] }),
    );

    const state = await resetPassword(undefined, form(PASSWORD));

    expect(state?.fieldErrors?.password).toBe("La contraseña debe tener al menos 12 caracteres.");
    expect(cookieDelete).not.toHaveBeenCalled();
  });

  it.each([429, 500, 0])("con otro error (%i) pide intentarlo más tarde", async (status) => {
    apiFetch.mockResolvedValue(apiError(status));

    expect(await resetPassword(undefined, form(PASSWORD))).toEqual({
      formError: "No hemos podido cambiar la contraseña. Inténtalo de nuevo en unos minutos.",
    });
    expect(cookieDelete).not.toHaveBeenCalled();
  });
});

describe("rutas", () => {
  it("la página y el enlace son públicos", () => {
    expect(isPublicRoute("/restablecer-contrasena")).toBe(true);
    expect(isPublicRoute("/restablecer-contrasena/enlace")).toBe(true);
  });
});
