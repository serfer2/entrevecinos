import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import type { LoginState, ResendVerificationState } from "../actions";
import { LoginForm } from "./LoginForm";

describe("LoginForm", () => {
  it("envía next oculto y muestra el error genérico conservando el correo", async () => {
    const action = vi.fn<(state: LoginState, formData: FormData) => Promise<LoginState>>(
      async () => ({
        formError: "Correo o contraseña incorrectos.",
        values: { email: "vecino@example.com" },
      }),
    );
    render(<LoginForm action={action} resendAction={vi.fn()} next="/comunidades/1" />);

    await userEvent.type(screen.getByLabelText("Correo electrónico"), "vecino@example.com");
    await userEvent.type(screen.getByLabelText("Contraseña"), "incorrecta");
    await userEvent.click(screen.getByRole("button", { name: "Iniciar sesión" }));

    expect(await screen.findByText("Correo o contraseña incorrectos.")).toBeTruthy();
    const formData = action.mock.calls[0][1];
    expect(formData.get("next")).toBe("/comunidades/1");
    expect((screen.getByLabelText("Correo electrónico") as HTMLInputElement).value).toBe(
      "vecino@example.com",
    );
    expect((screen.getByLabelText("Contraseña") as HTMLInputElement).value).toBe("");
    expect(screen.getByLabelText("Correo electrónico").getAttribute("aria-invalid")).toBeNull();
    expect(screen.queryByRole("button", { name: "Reenviar el correo de validación" })).toBeNull();
  });

  it("con el correo sin validar ofrece reenviar el correo escrito", async () => {
    const resendAction = vi.fn<
      (state: ResendVerificationState, formData: FormData) => Promise<ResendVerificationState>
    >(async () => ({ sent: true }));
    render(
      <LoginForm
        action={async () => ({
          formError: "Tienes que validar tu correo electrónico antes de iniciar sesión.",
          emailNotVerified: true,
          values: { email: "vecino@example.com" },
        })}
        resendAction={resendAction}
      />,
    );

    await userEvent.type(screen.getByLabelText("Correo electrónico"), "vecino@example.com");
    await userEvent.type(screen.getByLabelText("Contraseña"), "una-clave-cualquiera");
    await userEvent.click(screen.getByRole("button", { name: "Iniciar sesión" }));
    await userEvent.click(
      await screen.findByRole("button", { name: "Reenviar el correo de validación" }),
    );

    expect(resendAction.mock.calls[0][1].get("email")).toBe("vecino@example.com");
  });

  it("muestra el aviso de sesión caducada", () => {
    render(
      <LoginForm
        action={vi.fn()}
        resendAction={vi.fn()}
        notice="Tu sesión ha caducado. Vuelve a iniciar sesión."
      />,
    );

    expect(screen.getByRole("status").textContent).toBe(
      "Tu sesión ha caducado. Vuelve a iniciar sesión.",
    );
  });
});
