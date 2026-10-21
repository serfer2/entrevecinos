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

import { resendVerification, signup } from "./actions";

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

  it("con 201 devuelve el correo de validación sin crear la sesión", async () => {
    apiFetch.mockResolvedValue({
      ok: true,
      status: 201,
      data: { email: "vecino@example.com", verification_expires_at: "2026-10-22T10:00:00Z" },
    });

    const state = await signup(undefined, form(validForm));

    expect(state).toEqual({ verificationSentTo: "vecino@example.com" });
    expect(apiFetch).toHaveBeenCalledWith("/auth/register", {
      method: "POST",
      body: {
        full_name: "Alex Vecino",
        email: "vecino@example.com",
        password: "UnaClaveSegura123!",
        phone: null,
      },
    });
    expect(cookieSet).not.toHaveBeenCalled();
    expect(redirect).not.toHaveBeenCalled();
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

  it("con 409 email_pending_verification ofrece el reenvío", async () => {
    apiFetch.mockResolvedValue({
      ok: false,
      error: {
        status: 409,
        detail: "Este correo está pendiente de validación.",
        payload: { code: "email_pending_verification" },
      },
    });

    const state = await signup(undefined, form(validForm));

    expect(state).toEqual({
      fieldErrors: { email: "Este correo está pendiente de validación." },
      pendingVerification: true,
      values: keptValues,
    });
  });

  it("con 409 email_in_use no ofrece el reenvío", async () => {
    apiFetch.mockResolvedValue({
      ok: false,
      error: { status: 409, detail: "x", payload: { code: "email_in_use" } },
    });

    const state = await signup(undefined, form(validForm));

    expect(state).toEqual({ fieldErrors: { email: "Este correo ya está en uso." }, values: keptValues });
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

describe("resendVerification", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("con 202 indica que se ha enviado", async () => {
    apiFetch.mockResolvedValue({ ok: true, status: 202, data: { detail: "x" } });

    const state = await resendVerification(undefined, form({ email: "vecino@example.com" }));

    expect(state).toEqual({ sent: true });
    expect(apiFetch).toHaveBeenCalledWith("/auth/email-verification/resend", {
      method: "POST",
      body: { email: "vecino@example.com" },
    });
  });

  it.each([0, 422, 500])("con estado %i muestra un error", async (status) => {
    apiFetch.mockResolvedValue({ ok: false, error: { status, detail: null } });

    expect(await resendVerification(undefined, form({ email: "vecino@example.com" }))).toEqual({
      error: "No se pudo reenviar el correo. Inténtalo de nuevo.",
    });
  });
});
