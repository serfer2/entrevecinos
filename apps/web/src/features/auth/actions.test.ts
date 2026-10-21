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

import { signup } from "./actions";

function form(values: Record<string, string>) {
  const data = new FormData();
  for (const [key, value] of Object.entries(values)) data.set(key, value);
  return data;
}

const validForm = {
  full_name: "Alex Vecino",
  email: "vecino@example.com",
  password: "UnaClaveSegura123!",
  phone: "",
};
const keptValues = { full_name: "Alex Vecino", email: "vecino@example.com", phone: "" };

describe("signup", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("crea la sesión y redirige a /comunidades con 201", async () => {
    apiFetch.mockResolvedValue({
      ok: true,
      status: 201,
      data: { access_token: "jwt", expires_in: 86400, token_type: "Bearer", user: {} },
    });

    await expect(signup(undefined, form(validForm))).rejects.toThrow("NEXT_REDIRECT:/comunidades");

    expect(apiFetch).toHaveBeenCalledWith("/auth/register", {
      method: "POST",
      body: {
        full_name: "Alex Vecino",
        email: "vecino@example.com",
        password: "UnaClaveSegura123!",
        phone: null,
      },
    });
    expect(cookieSet).toHaveBeenCalledWith(
      "ev_session",
      "jwt",
      expect.objectContaining({ httpOnly: true, sameSite: "lax", path: "/", maxAge: 86400 }),
    );
  });

  it("no llama a la API si los datos no son válidos", async () => {
    const state = await signup(
      undefined,
      form({ ...validForm, email: "mal", password: "corta", full_name: " " }),
    );

    expect(apiFetch).not.toHaveBeenCalled();
    expect(Object.keys(state?.fieldErrors ?? {}).sort()).toEqual(["email", "full_name", "password"]);
  });

  it("marca el correo con 409 y conserva los valores sin la contraseña", async () => {
    apiFetch.mockResolvedValue({ ok: false, error: { status: 409, detail: "El correo ya está en uso." } });

    const state = await signup(undefined, form(validForm));

    expect(state).toEqual({ fieldErrors: { email: "Este correo ya está en uso." }, values: keptValues });
    expect(cookieSet).not.toHaveBeenCalled();
  });

  it("traduce los campos de un 422", async () => {
    apiFetch.mockResolvedValue({
      ok: false,
      error: { status: 422, detail: [{ loc: ["body", "password"], msg: "too short", type: "x" }] },
    });

    const state = await signup(undefined, form(validForm));

    expect(state?.fieldErrors).toEqual({
      password: "La contraseña debe tener al menos 12 caracteres.",
    });
  });

  it.each([0, 500, 503])("muestra un error general con estado %i", async (status) => {
    apiFetch.mockResolvedValue({ ok: false, error: { status, detail: null } });

    const state = await signup(undefined, form(validForm));

    expect(state).toEqual({
      formError: "No se pudo crear la cuenta. Inténtalo de nuevo.",
      values: keptValues,
    });
  });
});
