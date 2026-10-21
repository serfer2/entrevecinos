import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import type { ResendVerificationState, SignupState } from "../actions";
import { SignupForm } from "./SignupForm";

async function submitWith(state: SignupState, resendAction = vi.fn()) {
  const action = vi.fn(async () => state);
  render(<SignupForm action={action} resendAction={resendAction} />);
  // jsdom aplica la validación nativa (`required`): sin rellenar, el formulario no se envía.
  await userEvent.type(screen.getByLabelText("Nombre"), "Alex Vecino");
  await userEvent.type(screen.getByLabelText("Correo electrónico"), "vecino@example.com");
  await userEvent.type(screen.getByLabelText("Contraseña"), "una-clave-cualquiera");
  await userEvent.click(screen.getByRole("button", { name: "Crear cuenta" }));
  return action;
}

describe("SignupForm", () => {
  it("muestra los errores bajo cada campo y marca los campos inválidos", async () => {
    await submitWith({
      fieldErrors: { email: "Este correo ya está en uso.", full_name: "Introduce tu nombre." },
      values: { full_name: "", email: "vecino@example.com", phone: "" },
    });

    const email = await screen.findByLabelText("Correo electrónico");
    expect(email.getAttribute("aria-invalid")).toBe("true");
    expect(screen.getByText("Este correo ya está en uso.").id).toBe(
      email.getAttribute("aria-describedby"),
    );
    expect(screen.getByLabelText("Nombre").getAttribute("aria-invalid")).toBe("true");
  });

  it("muestra el error general como alerta", async () => {
    await submitWith({ formError: "No se pudo crear la cuenta. Inténtalo de nuevo." });

    expect((await screen.findByRole("alert")).textContent).toBe(
      "No se pudo crear la cuenta. Inténtalo de nuevo.",
    );
  });

  it("conserva los valores devueltos pero no la contraseña", async () => {
    await submitWith({
      formError: "Error",
      values: { full_name: "Alex Vecino", email: "vecino@example.com", phone: "600111222" },
    });

    await screen.findByRole("alert");
    expect((screen.getByLabelText("Nombre") as HTMLInputElement).value).toBe("Alex Vecino");
    expect((screen.getByLabelText("Correo electrónico") as HTMLInputElement).value).toBe(
      "vecino@example.com",
    );
    expect((screen.getByLabelText("Teléfono (opcional)") as HTMLInputElement).value).toBe(
      "600111222",
    );
    expect((screen.getByLabelText("Contraseña") as HTMLInputElement).value).toBe("");
  });

  it("tras el registro sustituye el formulario por el aviso del correo enviado", async () => {
    await submitWith({ verificationSentTo: "vecino@example.com" });

    const notice = await screen.findByRole("status");
    expect(notice.textContent).toContain("Te hemos enviado un correo a vecino@example.com.");
    expect(notice.textContent).toContain("El enlace caduca en 24 horas.");
    expect(notice.textContent).toContain("revisa la carpeta de correo no deseado");
    expect(screen.queryByRole("button", { name: "Crear cuenta" })).toBeNull();
  });

  it("con un correo pendiente ofrece reenviar el correo de validación", async () => {
    const resendAction = vi.fn<
      (state: ResendVerificationState, formData: FormData) => Promise<ResendVerificationState>
    >(async () => ({ sent: true }));
    await submitWith(
      {
        fieldErrors: { email: "Este correo está pendiente de validación." },
        pendingVerification: true,
        values: { full_name: "Alex Vecino", email: "vecino@example.com", phone: "" },
      },
      resendAction,
    );

    expect(await screen.findByText("Este correo está pendiente de validación.")).toBeTruthy();
    await userEvent.click(screen.getByRole("button", { name: "Reenviar el correo de validación" }));

    expect(resendAction.mock.calls[0][1].get("email")).toBe("vecino@example.com");
  });

  it("con el correo en uso no ofrece el reenvío", async () => {
    await submitWith({
      fieldErrors: { email: "Este correo ya está en uso." },
      values: { full_name: "Alex Vecino", email: "vecino@example.com", phone: "" },
    });

    await screen.findByText("Este correo ya está en uso.");
    expect(screen.queryByRole("button", { name: "Reenviar el correo de validación" })).toBeNull();
  });

  it("enlaza con el inicio de sesión", () => {
    render(<SignupForm action={vi.fn()} resendAction={vi.fn()} />);

    expect(screen.getByRole("link", { name: "Inicia sesión" }).getAttribute("href")).toBe(
      "/iniciar-sesion",
    );
  });
});
