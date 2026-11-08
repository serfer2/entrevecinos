import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/features/auth/actions", () => ({ login: vi.fn(), resendVerification: vi.fn() }));
vi.mock("@/features/auth/dal", () => ({ getCurrentUser: vi.fn(async () => null) }));
vi.mock("next/navigation", () => ({ redirect: vi.fn() }));

import LoginPage from "./page";

describe("/iniciar-sesion", () => {
  it("tras cambiar la contraseña muestra el aviso", async () => {
    render(await LoginPage({ searchParams: Promise.resolve({ motivo: "contrasena-cambiada" }) }));

    expect(screen.getByRole("status").textContent).toBe(
      "Tu contraseña se ha cambiado. Inicia sesión con la nueva.",
    );
  });
});
