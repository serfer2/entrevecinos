import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const { getCurrentUser, redirect } = vi.hoisted(() => ({
  getCurrentUser: vi.fn(),
  redirect: vi.fn((url: string) => {
    throw new Error(`NEXT_REDIRECT:${url}`);
  }),
}));

vi.mock("@/features/auth/actions", () => ({ requestPasswordReset: vi.fn() }));
vi.mock("@/features/auth/dal", () => ({ getCurrentUser }));
vi.mock("next/navigation", () => ({ redirect }));

import PasswordResetRequestPage from "./page";

async function renderWith(params: Record<string, string>) {
  render(await PasswordResetRequestPage({ searchParams: Promise.resolve(params) }));
}

describe("/recuperar-contrasena", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getCurrentUser.mockResolvedValue(null);
  });

  it("muestra el formulario con el correo de la URL", async () => {
    await renderWith({ email: "vecino@example.com" });

    expect(screen.getByRole("heading", { name: "Recupera tu contraseña" })).toBeTruthy();
    expect((screen.getByLabelText("Correo electrónico") as HTMLInputElement).value).toBe(
      "vecino@example.com",
    );
  });

  it("sin correo en la URL deja el campo vacío", async () => {
    await renderWith({});

    expect((screen.getByLabelText("Correo electrónico") as HTMLInputElement).value).toBe("");
  });

  it("con sesión iniciada lleva al inicio", async () => {
    getCurrentUser.mockResolvedValue({ id: "1" });

    await expect(renderWith({})).rejects.toThrow("NEXT_REDIRECT:/inicio");
  });

  it("si la API falla al comprobar la sesión, muestra el formulario", async () => {
    getCurrentUser.mockRejectedValue(new Error("API caída"));

    await renderWith({});

    expect(screen.getByRole("button", { name: "Enviar enlace" })).toBeTruthy();
  });
});
