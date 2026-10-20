import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, describe, expect, it, vi } from "vitest";

const { deleteListing } = vi.hoisted(() => ({ deleteListing: vi.fn() }));
vi.mock("../actions", () => ({ deleteListing }));

import type { ApiListing } from "../types";
import { ListingActions } from "./ListingActions";

const listing = { id: "l1", status: "active" } as ApiListing;

beforeAll(() => {
  // jsdom no implementa los diálogos modales.
  HTMLDialogElement.prototype.showModal = function showModal() {
    this.setAttribute("open", "");
  };
  HTMLDialogElement.prototype.close = function close() {
    this.removeAttribute("open");
  };
});

describe("ListingActions", () => {
  it("el autor ve «Editar anuncio» y «Eliminar anuncio»", () => {
    render(<ListingActions listing={listing} isOwner canModerate={false} />);

    expect(screen.getByRole("link", { name: "Editar anuncio" }).getAttribute("href")).toBe("/anuncios/l1/editar");
    expect(screen.getByRole("button", { name: "Eliminar anuncio" })).toBeTruthy();
  });

  it("otros vecinos no ven ni la edición ni el borrado", () => {
    render(<ListingActions listing={listing} isOwner={false} canModerate />);

    expect(screen.queryByRole("link", { name: "Editar anuncio" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Eliminar anuncio" })).toBeNull();
  });

  it.each(["hidden", "completed"] as const)("sin edición en anuncios %s (sí se puede eliminar)", (status) => {
    render(<ListingActions listing={{ ...listing, status }} isOwner canModerate={false} />);

    expect(screen.queryByRole("link", { name: "Editar anuncio" })).toBeNull();
    expect(screen.getByRole("button", { name: "Eliminar anuncio" })).toBeTruthy();
  });

  it("eliminar pide confirmación y cancelar no llama a la acción", async () => {
    render(<ListingActions listing={listing} isOwner canModerate={false} />);

    await userEvent.click(screen.getByRole("button", { name: "Eliminar anuncio" }));
    expect(screen.getByRole("dialog", { name: "¿Eliminar este anuncio?" })).toBeTruthy();
    await userEvent.click(screen.getByRole("button", { name: "Cancelar" }));

    expect(deleteListing).not.toHaveBeenCalled();
  });
});
