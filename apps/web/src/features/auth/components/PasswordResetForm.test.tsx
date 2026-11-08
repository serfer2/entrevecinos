import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import type { PasswordResetState } from "../actions";
import { PasswordResetForm } from "./PasswordResetForm";

type Action = (state: PasswordResetState, formData: FormData) => Promise<PasswordResetState>;

async function submit(password: string, confirm: string) {
  await userEvent.type(screen.getByLabelText("Contraseña nueva"), password);
  await userEvent.type(screen.getByLabelText("Repite la contraseña"), confirm);
  await userEvent.click(screen.getByRole("button", { name: "Cambiar contraseña" }));
}

describe("PasswordResetForm", () => {
  it("envía las dos contraseñas, sin ningún token en el formulario", async () => {
    const action = vi.fn<Action>(async () => undefined);
    const { container } = render(<PasswordResetForm action={action} />);

    expect(container.querySelector('input[type="hidden"]')).toBeNull();
    expect(screen.getByLabelText("Contraseña nueva").getAttribute("autocomplete")).toBe(
      "new-password",
    );
    await submit("OtraClaveSegura456!", "OtraClaveSegura456!");

    const formData = action.mock.calls[0][1];
    expect(formData.get("password")).toBe("OtraClaveSegura456!");
    expect(formData.get("password_confirm")).toBe("OtraClaveSegura456!");
  });

  it("muestra el error de la confirmación", async () => {
    const action = vi.fn<Action>(async () => ({
      fieldErrors: { password_confirm: "Las contraseñas no coinciden." },
    }));
    render(<PasswordResetForm action={action} />);

    await submit("OtraClaveSegura456!", "OtraDistinta789!x");

    expect(await screen.findByText("Las contraseñas no coinciden.")).toBeTruthy();
    expect(screen.getByLabelText("Repite la contraseña").getAttribute("aria-invalid")).toBe("true");
  });

  it("con el enlace caducado lo explica y ofrece pedir otro", async () => {
    const action = vi.fn<Action>(async () => ({ linkError: "caducado" }));
    render(<PasswordResetForm action={action} />);

    await submit("OtraClaveSegura456!", "OtraClaveSegura456!");

    expect((await screen.findByRole("alert")).textContent).toBe(
      "El enlace para restablecer la contraseña ha caducado.",
    );
    expect(screen.getByRole("link", { name: "Pedir otro enlace" }).getAttribute("href")).toBe(
      "/recuperar-contrasena",
    );
    expect(screen.queryByLabelText("Contraseña nueva")).toBeNull();
  });

  it("muestra el error general", async () => {
    const action = vi.fn<Action>(async () => ({
      formError: "No hemos podido cambiar la contraseña. Inténtalo de nuevo en unos minutos.",
    }));
    render(<PasswordResetForm action={action} />);

    await submit("OtraClaveSegura456!", "OtraClaveSegura456!");

    expect((await screen.findByRole("alert")).textContent).toBe(
      "No hemos podido cambiar la contraseña. Inténtalo de nuevo en unos minutos.",
    );
  });
});
