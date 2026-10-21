import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import type { ResendVerificationState } from "../actions";
import { ResendVerificationButton } from "./ResendVerificationButton";

const BUTTON = { name: "Reenviar el correo de validación" };

function renderWith(result: ResendVerificationState) {
  const action = vi.fn<
    (state: ResendVerificationState, formData: FormData) => Promise<ResendVerificationState>
  >(async () => result);
  render(<ResendVerificationButton email="vecino@example.com" action={action} />);
  return action;
}

describe("ResendVerificationButton", () => {
  it("envía el correo y muestra el aviso en lugar del botón", async () => {
    const action = renderWith({ sent: true });

    await userEvent.click(screen.getByRole("button", BUTTON));

    expect((await screen.findByRole("status")).textContent).toBe(
      "Si tu cuenta está pendiente de validación, te hemos enviado un correo nuevo. Revisa tu bandeja de entrada.",
    );
    expect(action.mock.calls[0][1].get("email")).toBe("vecino@example.com");
    expect(screen.queryByRole("button", BUTTON)).toBeNull();
  });

  it("muestra el error y mantiene el botón", async () => {
    renderWith({ error: "No se pudo reenviar el correo. Inténtalo de nuevo." });

    await userEvent.click(screen.getByRole("button", BUTTON));

    expect((await screen.findByRole("alert")).textContent).toBe(
      "No se pudo reenviar el correo. Inténtalo de nuevo.",
    );
    expect(screen.getByRole("button", BUTTON)).toBeTruthy();
  });

  it("se deshabilita mientras se envía", async () => {
    let finish: (state: ResendVerificationState) => void = () => {};
    const action = vi.fn(
      () => new Promise<ResendVerificationState>((resolve) => (finish = resolve)),
    );
    render(<ResendVerificationButton email="vecino@example.com" action={action} />);

    await userEvent.click(screen.getByRole("button", BUTTON));

    const button = await screen.findByRole("button", { name: "Enviando…" });
    expect((button as HTMLButtonElement).disabled).toBe(true);
    finish({ sent: true });
    await screen.findByRole("status");
  });
});
