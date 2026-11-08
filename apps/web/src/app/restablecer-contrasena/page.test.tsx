import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const { getPasswordResetToken } = vi.hoisted(() => ({ getPasswordResetToken: vi.fn() }));

vi.mock("@/features/auth/actions", () => ({ resetPassword: vi.fn() }));
vi.mock("@/features/auth/reset-token", () => ({ getPasswordResetToken }));

import PasswordResetPage from "./page";

async function renderWith(params: Record<string, string> = {}) {
  render(await PasswordResetPage({ searchParams: Promise.resolve(params) }));
}

describe("/restablecer-contrasena", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getPasswordResetToken.mockResolvedValue("token-del-correo");
  });

  it("con el token del enlace muestra el formulario", async () => {
    await renderWith();

    expect(screen.getByRole("heading", { name: "Elige una contraseña nueva" })).toBeTruthy();
    expect(screen.getByLabelText("Contraseña nueva")).toBeTruthy();
    expect(screen.getByLabelText("Repite la contraseña")).toBeTruthy();
  });

  it("sin el token explica que el enlace no es válido", async () => {
    getPasswordResetToken.mockResolvedValue(undefined);

    await renderWith();

    expect(screen.getByRole("alert").textContent).toContain(
      "El enlace para restablecer la contraseña no es válido.",
    );
    expect(screen.getByRole("link", { name: "Pedir otro enlace" }).getAttribute("href")).toBe(
      "/recuperar-contrasena",
    );
    expect(screen.queryByLabelText("Contraseña nueva")).toBeNull();
  });

  it.each([
    ["caducado", "El enlace para restablecer la contraseña ha caducado."],
    ["invalido", "El enlace para restablecer la contraseña no es válido."],
  ])("con motivo=%s muestra su mensaje", async (motivo, message) => {
    await renderWith({ motivo });

    expect(screen.getByRole("alert").textContent).toContain(message);
  });

  it("ignora un motivo desconocido", async () => {
    await renderWith({ motivo: "otro" });

    expect(screen.getByLabelText("Contraseña nueva")).toBeTruthy();
  });
});
