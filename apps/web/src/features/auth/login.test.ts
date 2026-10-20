import { beforeEach, describe, expect, it, vi } from "vitest";

const { apiFetch, cookieSet, redirect } = vi.hoisted(() => ({
  apiFetch: vi.fn(),
  cookieSet: vi.fn(),
  redirect: vi.fn((url: string) => {
    throw new Error(`NEXT_REDIRECT:${url}`);
  }),
}));

vi.mock("@/lib/api/server", () => ({ apiFetch }));
vi.mock("next/headers", () => ({ cookies: async () => ({ set: cookieSet }) }));
vi.mock("next/navigation", () => ({ redirect }));

import { login } from "./actions";

function form(values: Record<string, string>) {
  const data = new FormData();
  for (const [key, value] of Object.entries(values)) data.set(key, value);
  return data;
}

const credentials = { email: "vecino@example.com", password: "UnaClaveSegura123!" };
const success = {
  ok: true,
  status: 200,
  data: { access_token: "jwt", expires_in: 86400, token_type: "Bearer", user: {} },
};

describe("login", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("crea la sesión y redirige a next si es una ruta interna", async () => {
    apiFetch.mockResolvedValue(success);

    await expect(login(undefined, form({ ...credentials, next: "/comunidades/1" }))).rejects.toThrow(
      "NEXT_REDIRECT:/comunidades/1",
    );
    expect(apiFetch).toHaveBeenCalledWith("/auth/token", { method: "POST", body: credentials });
    expect(cookieSet).toHaveBeenCalledWith("ev_session", "jwt", expect.objectContaining({ httpOnly: true }));
  });

  it.each(["https://evil.example", "//evil.example", ""])(
    "ignora next=%s y redirige a /inicio",
    async (next) => {
      apiFetch.mockResolvedValue(success);

      await expect(login(undefined, form({ ...credentials, next }))).rejects.toThrow(
        "NEXT_REDIRECT:/inicio",
      );
    },
  );

  it("muestra un error genérico con 401 y conserva solo el correo", async () => {
    apiFetch.mockResolvedValue({ ok: false, error: { status: 401, detail: "x" } });

    expect(await login(undefined, form(credentials))).toEqual({
      formError: "Correo o contraseña incorrectos.",
      values: { email: "vecino@example.com" },
    });
    expect(cookieSet).not.toHaveBeenCalled();
  });

  it("valida los campos antes de llamar a la API", async () => {
    const state = await login(undefined, form({ email: "mal", password: "" }));

    expect(apiFetch).not.toHaveBeenCalled();
    expect(state?.fieldErrors).toEqual({
      email: "Introduce un correo electrónico válido.",
      password: "Introduce tu contraseña.",
    });
  });

  it("muestra un error general si la API no responde", async () => {
    apiFetch.mockResolvedValue({ ok: false, error: { status: 0, detail: null } });

    expect((await login(undefined, form(credentials)))?.formError).toBe(
      "No se pudo iniciar sesión. Inténtalo de nuevo.",
    );
  });
});
