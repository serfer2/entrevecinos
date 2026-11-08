import { beforeEach, describe, expect, it, vi } from "vitest";

const { apiFetch } = vi.hoisted(() => ({ apiFetch: vi.fn() }));

vi.mock("@/lib/api/server", () => ({ apiFetch }));
vi.mock("next/headers", () => ({ cookies: async () => ({ set: vi.fn() }) }));
vi.mock("next/navigation", () => ({ redirect: vi.fn() }));

import { requestPasswordReset } from "./actions";
import { isPublicRoute, PASSWORD_RESET_REQUEST_PATH } from "./routes";

function form(email: string) {
  const data = new FormData();
  data.set("email", email);
  return data;
}

function apiError(status: number, payload: Record<string, unknown> = {}) {
  return { ok: false, error: { status, detail: payload.detail, payload } };
}

describe("requestPasswordReset", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("con 202 confirma el envío sin revelar si la cuenta existe", async () => {
    apiFetch.mockResolvedValue({ ok: true, status: 202, data: { detail: "…" } });

    const state = await requestPasswordReset(undefined, form("  vecino@example.com "));

    expect(state).toEqual({ sent: true });
    expect(apiFetch).toHaveBeenCalledWith("/auth/password-reset", {
      method: "POST",
      body: { email: "vecino@example.com" },
    });
  });

  it("no llama a la API con un correo no válido", async () => {
    const state = await requestPasswordReset(undefined, form("no-es-un-correo"));

    expect(state).toEqual({
      fieldErrors: { email: "Introduce un correo electrónico válido." },
      values: { email: "no-es-un-correo" },
    });
    expect(apiFetch).not.toHaveBeenCalled();
  });

  it("sin cupo de correos lo explica y conserva el correo", async () => {
    apiFetch.mockResolvedValue(
      apiError(503, { detail: "Sin cupo", code: "email_quota_exceeded" }),
    );

    const state = await requestPasswordReset(undefined, form("vecino@example.com"));

    expect(state).toEqual({
      formError: "Ahora mismo no podemos enviar correos. Inténtalo de nuevo en unos días.",
      values: { email: "vecino@example.com" },
    });
  });

  it("con 422 marca el campo de correo", async () => {
    apiFetch.mockResolvedValue(
      apiError(422, { detail: [{ loc: ["body", "email"], msg: "x", type: "value_error" }] }),
    );

    const state = await requestPasswordReset(undefined, form("vecino@example.com"));

    expect(state?.fieldErrors).toEqual({ email: "Introduce un correo electrónico válido." });
  });

  it.each([429, 500, 0])("con otro error (%i) pide intentarlo más tarde", async (status) => {
    apiFetch.mockResolvedValue(apiError(status));

    const state = await requestPasswordReset(undefined, form("vecino@example.com"));

    expect(state).toEqual({
      formError: "No hemos podido enviar el enlace. Inténtalo de nuevo en unos minutos.",
      values: { email: "vecino@example.com" },
    });
  });
});

describe("rutas", () => {
  it("/recuperar-contrasena es pública", () => {
    expect(PASSWORD_RESET_REQUEST_PATH).toBe("/recuperar-contrasena");
    expect(isPublicRoute("/recuperar-contrasena")).toBe(true);
  });
});
