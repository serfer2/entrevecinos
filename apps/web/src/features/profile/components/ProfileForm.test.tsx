import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import type { ProfileState } from "../actions";
import { ProfileForm } from "./ProfileForm";

type Action = (state: ProfileState, formData: FormData) => Promise<ProfileState>;

describe("ProfileForm", () => {
  it("muestra los valores actuales", () => {
    render(
      <ProfileForm action={vi.fn<Action>()} initialValues={{ full_name: "Alex", phone: null }} />,
    );

    expect((screen.getByLabelText("Nombre") as HTMLInputElement).value).toBe("Alex");
    expect((screen.getByLabelText("Teléfono") as HTMLInputElement).value).toBe("");
  });

  it("anuncia el éxito con role=status", async () => {
    const action = vi.fn<Action>(async () => ({
      success: "Perfil actualizado.",
      values: { full_name: "Alex García", phone: "" },
    }));
    render(<ProfileForm action={action} initialValues={{ full_name: "Alex", phone: null }} />);

    await userEvent.click(screen.getByRole("button", { name: "Guardar cambios" }));

    expect((await screen.findByRole("status")).textContent).toBe("Perfil actualizado.");
    expect((screen.getByLabelText("Nombre") as HTMLInputElement).value).toBe("Alex García");
  });

  it("muestra el error bajo el campo y conserva lo escrito", async () => {
    const action = vi.fn<Action>(async () => ({
      fieldErrors: { phone: "Introduce un teléfono válido." },
      values: { full_name: "Alex", phone: "llámame" },
    }));
    render(<ProfileForm action={action} initialValues={{ full_name: "Alex", phone: "600111222" }} />);

    await userEvent.click(screen.getByRole("button", { name: "Guardar cambios" }));

    const phone = await screen.findByLabelText("Teléfono");
    await screen.findByText("Introduce un teléfono válido.");
    expect(phone.getAttribute("aria-invalid")).toBe("true");
    expect((phone as HTMLInputElement).value).toBe("llámame");
  });
});
