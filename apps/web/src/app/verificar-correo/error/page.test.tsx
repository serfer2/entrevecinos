import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/features/auth/actions", () => ({ resendVerification: vi.fn() }));

import VerifyEmailErrorPage from "./page";

async function renderWith(params: Record<string, string>) {
  render(await VerifyEmailErrorPage({ searchParams: Promise.resolve(params) }));
}

function href(name: string): string | null {
  return screen.getByRole("link", { name }).getAttribute("href");
}

describe("/verificar-correo/error", () => {
  it.each([
    [{ motivo: "caducado", email: "vecino@example.com" }],
    [{ motivo: "caducado" }],
    [{ motivo: "invalido" }],
    [{ motivo: "error" }],
    [{}],
  ])("siempre enlaza con la raíz (%j)", async (params) => {
    await renderWith(params);

    expect(href("Volver al inicio")).toBe("/");
  });

  it("con el enlace caducado y el correo ofrece el reenvío", async () => {
    await renderWith({ motivo: "caducado", email: "vecino@example.com" });

    expect(screen.getByRole("alert").textContent).toBe("El enlace de validación ha caducado.");
    expect(screen.getByRole("button", { name: "Reenviar el correo de validación" })).toBeTruthy();
  });

  it("con el enlace caducado sin correo enlaza con el registro", async () => {
    await renderWith({ motivo: "caducado" });

    expect(href("Ir al registro")).toBe("/registro");
  });

  it("con un motivo desconocido muestra el enlace no válido y el inicio de sesión", async () => {
    await renderWith({ motivo: "otro" });

    expect(screen.getByRole("alert").textContent).toBe("El enlace de validación no es válido.");
    expect(href("Ir a iniciar sesión")).toBe("/iniciar-sesion");
  });
});
