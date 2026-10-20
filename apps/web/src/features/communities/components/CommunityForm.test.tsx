import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import type { CommunityFormState } from "../actions";
import { CommunityForm } from "./CommunityForm";

type Action = (state: CommunityFormState, formData: FormData) => Promise<CommunityFormState>;

describe("CommunityForm", () => {
  it("muestra los errores por campo y conserva lo escrito", async () => {
    const action = vi.fn<Action>(async () => ({
      fieldErrors: { name: "El nombre de la comunidad es obligatorio." },
      values: { name: "", description: "Fases 1 a 3", city: "Majadahonda", postal_code: "" },
    }));
    render(<CommunityForm action={action} />);
    await userEvent.type(screen.getByLabelText("Nombre de la comunidad"), "x");

    await userEvent.click(screen.getByRole("button", { name: "Crear comunidad" }));

    await screen.findByText("El nombre de la comunidad es obligatorio.");
    expect(screen.getByLabelText("Nombre de la comunidad").getAttribute("aria-invalid")).toBe("true");
    expect((screen.getByLabelText("Descripción (opcional)") as HTMLTextAreaElement).value).toBe(
      "Fases 1 a 3",
    );
    expect((screen.getByLabelText("Ciudad (opcional)") as HTMLInputElement).value).toBe("Majadahonda");
  });

  it("muestra el error general", async () => {
    const action = vi.fn<Action>(async () => ({ formError: "No se pudo crear la comunidad." }));
    render(<CommunityForm action={action} />);
    await userEvent.type(screen.getByLabelText("Nombre de la comunidad"), "Los Olivos");

    await userEvent.click(screen.getByRole("button", { name: "Crear comunidad" }));

    expect((await screen.findByRole("alert")).textContent).toBe("No se pudo crear la comunidad.");
  });
});
