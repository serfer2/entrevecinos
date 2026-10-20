import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

vi.mock("@/features/media/actions", () => ({ uploadImage: vi.fn() }));

import type { ListingFormAction } from "../form";
import { ListingForm } from "./ListingForm";

const categories = [
  { id: "0b5c4a7e-1d2f-4c3b-9a8e-7f6d5c4b3a21", name: "Deporte y ocio", slug: "deporte-y-ocio", is_active: true },
  { id: "1c6d5b8f-2e3a-4d4c-8b9f-8a7e6d5c4b32", name: "Otros", slug: "otros", is_active: true },
];

function renderForm(action: ListingFormAction) {
  render(<ListingForm action={action} categories={categories} submitLabel="Publicar anuncio" pendingLabel="Publicando…" />);
}

describe("ListingForm", () => {
  it("muestra las categorías y los seis tipos", () => {
    renderForm(vi.fn());

    expect(screen.getByRole("option", { name: "Otros" })).toBeTruthy();
    for (const label of ["Vendo", "Busco", "Ofrezco", "Necesito", "Regalo", "Otros"]) {
      expect(screen.getByRole("radio", { name: label })).toBeTruthy();
    }
  });

  it("con «Regalo» sugiere dejarlo sin precio", async () => {
    renderForm(vi.fn());

    await userEvent.click(screen.getByRole("radio", { name: "Regalo" }));

    expect(screen.getByText("Normalmente sin precio.")).toBeTruthy();
  });

  it("muestra los errores por campo y conserva lo escrito", async () => {
    const action = vi.fn<ListingFormAction>(async () => ({
      fieldErrors: { title: "El título es obligatorio.", price: "Introduce un precio válido." },
      values: {
        title: "",
        description: "Poco uso",
        category_id: categories[0].id,
        type: "sell",
        price: "abc",
        image_asset_ids: [],
      },
    }));
    renderForm(action);
    const form = screen.getByRole("button", { name: "Publicar anuncio" }).closest("form")!;
    form.noValidate = true;

    await userEvent.click(screen.getByRole("button", { name: "Publicar anuncio" }));

    await screen.findByText("El título es obligatorio.");
    expect(screen.getByText("Introduce un precio válido.")).toBeTruthy();
    expect((screen.getByLabelText("Descripción") as HTMLTextAreaElement).value).toBe("Poco uso");
    expect((screen.getByLabelText("Categoría") as HTMLSelectElement).value).toBe(categories[0].id);
    expect((screen.getByRole("radio", { name: "Vendo" }) as HTMLInputElement).checked).toBe(true);
  });
});
