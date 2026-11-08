import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import type { PasswordResetRequestState } from "../actions";
import { PasswordResetRequestForm } from "./PasswordResetRequestForm";

type Action = (
  state: PasswordResetRequestState,
  formData: FormData,
) => Promise<PasswordResetRequestState>;

describe("PasswordResetRequestForm", () => {
  it("rellena el correo recibido y, al enviarlo, muestra el aviso", async () => {
    const action = vi.fn<Action>(async () => ({ sent: true }));
    render(<PasswordResetRequestForm action={action} defaultEmail="vecino@example.com" />);

    expect((screen.getByLabelText("Correo electrónico") as HTMLInputElement).value).toBe(
      "vecino@example.com",
    );
    await userEvent.click(screen.getByRole("button", { name: "Enviar enlace" }));

    const status = await screen.findByRole("status");
    expect(status.textContent).toContain(
      "Si hay una cuenta con ese correo, te hemos enviado un enlace para restablecer la contraseña. Caduca en 1 hora.",
    );
    expect(action.mock.calls[0][1].get("email")).toBe("vecino@example.com");
    expect(screen.getByRole("link", { name: "Volver a iniciar sesión" }).getAttribute("href")).toBe(
      "/iniciar-sesion",
    );
    expect(screen.queryByLabelText("Correo electrónico")).toBeNull();
  });

  it("muestra el error y conserva el correo escrito", async () => {
    const action = vi.fn<Action>(async () => ({
      formError: "Ahora mismo no podemos enviar correos. Inténtalo de nuevo en unos días.",
      values: { email: "otro@example.com" },
    }));
    render(<PasswordResetRequestForm action={action} />);

    await userEvent.type(screen.getByLabelText("Correo electrónico"), "otro@example.com");
    await userEvent.click(screen.getByRole("button", { name: "Enviar enlace" }));

    expect((await screen.findByRole("alert")).textContent).toBe(
      "Ahora mismo no podemos enviar correos. Inténtalo de nuevo en unos días.",
    );
    expect((screen.getByLabelText("Correo electrónico") as HTMLInputElement).value).toBe(
      "otro@example.com",
    );
  });

  it("muestra el error del campo", async () => {
    const action = vi.fn<Action>(async () => ({
      fieldErrors: { email: "Introduce un correo electrónico válido." },
      values: { email: "x@y" },
    }));
    render(<PasswordResetRequestForm action={action} />);

    await userEvent.type(screen.getByLabelText("Correo electrónico"), "x@y");
    await userEvent.click(screen.getByRole("button", { name: "Enviar enlace" }));

    expect(await screen.findByText("Introduce un correo electrónico válido.")).toBeTruthy();
    expect(screen.getByLabelText("Correo electrónico").getAttribute("aria-invalid")).toBe("true");
  });
});
