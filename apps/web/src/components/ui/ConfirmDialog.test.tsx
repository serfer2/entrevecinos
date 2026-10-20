import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, describe, expect, it, vi } from "vitest";

import { ConfirmDialog } from "./ConfirmDialog";

beforeAll(() => {
  // jsdom no implementa los diálogos modales.
  HTMLDialogElement.prototype.showModal = function showModal() {
    this.setAttribute("open", "");
  };
  HTMLDialogElement.prototype.close = function close() {
    this.removeAttribute("open");
  };
});

function setup() {
  const action = vi.fn();
  render(
    <ConfirmDialog
      action={action}
      triggerLabel="Rechazar"
      title="¿Rechazar la solicitud?"
      message="No podrá volver a solicitar el acceso."
      confirmLabel="Rechazar solicitud"
    >
      <input type="hidden" name="user_id" value="u1" />
    </ConfirmDialog>,
  );
  return action;
}

describe("ConfirmDialog", () => {
  it("abre el diálogo sin enviar el formulario", async () => {
    const action = setup();

    await userEvent.click(screen.getByRole("button", { name: "Rechazar" }));

    const dialog = screen.getByRole("dialog", { name: "¿Rechazar la solicitud?" });
    expect(dialog.hasAttribute("open")).toBe(true);
    expect(dialog.getAttribute("aria-describedby")).toBeTruthy();
    expect(action).not.toHaveBeenCalled();
  });

  it("cancelar cierra el diálogo sin enviar", async () => {
    const action = setup();
    await userEvent.click(screen.getByRole("button", { name: "Rechazar" }));

    await userEvent.click(screen.getByRole("button", { name: "Cancelar" }));

    expect(screen.getByRole("dialog", { hidden: true }).hasAttribute("open")).toBe(false);
    expect(action).not.toHaveBeenCalled();
  });

  it("confirmar envía el formulario con sus campos", async () => {
    const action = setup();
    await userEvent.click(screen.getByRole("button", { name: "Rechazar" }));

    fireEvent.click(screen.getByRole("button", { name: "Rechazar solicitud" }));

    await vi.waitFor(() => expect(action).toHaveBeenCalled());
    expect((action.mock.calls[0][0] as FormData).get("user_id")).toBe("u1");
  });
});
