import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, describe, expect, it, vi } from "vitest";

const { deleteListing, moderateListing, changeListingStatus } = vi.hoisted(() => ({
  deleteListing: vi.fn(),
  moderateListing: vi.fn(),
  changeListingStatus: vi.fn(),
}));
vi.mock("../actions", () => ({ deleteListing, moderateListing, changeListingStatus }));

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

  it("moderación: «Ocultar anuncio» en un anuncio visible, sin acciones de autor", () => {
    render(<ListingActions listing={listing} isOwner={false} canModerate />);

    expect(screen.getByRole("button", { name: "Ocultar anuncio" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Restaurar anuncio" })).toBeNull();
  });

  it("moderación: anuncio retirado con aviso y «Restaurar anuncio»", () => {
    render(<ListingActions listing={{ ...listing, status: "hidden" }} isOwner={false} canModerate />);

    expect(screen.getByRole("status").textContent).toBe("Este anuncio está oculto y no se muestra en la comunidad.");
    expect(screen.getByRole("button", { name: "Restaurar anuncio" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Ocultar anuncio" })).toBeNull();
  });

  it("autor de un anuncio retirado: aviso, sin «Editar» ni moderación", () => {
    render(<ListingActions listing={{ ...listing, status: "hidden" }} isOwner canModerate={false} />);

    expect(screen.getByRole("status")).toBeTruthy();
    expect(screen.queryByRole("link", { name: "Editar anuncio" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Restaurar anuncio" })).toBeNull();
  });

  it("los roles se suman: autor y administrador", () => {
    render(<ListingActions listing={listing} isOwner canModerate />);

    for (const name of ["Eliminar anuncio", "Ocultar anuncio"]) {
      expect(screen.getByRole("button", { name })).toBeTruthy();
    }
    expect(screen.getByRole("link", { name: "Editar anuncio" })).toBeTruthy();
  });

  it("miembro sin rol en el anuncio de otro: ninguna acción", () => {
    const { container } = render(<ListingActions listing={listing} isOwner={false} canModerate={false} />);

    expect(container.innerHTML).toBe("");
  });

  it.each([
    ["active", ["Marcar como reservado", "Marcar como finalizado"]],
    ["reserved", ["Quitar reserva", "Marcar como finalizado"]],
    ["completed", []],
    ["hidden", []],
  ] as const)("autor, anuncio %s: botones de estado %o", (status, expected) => {
    render(<ListingActions listing={{ ...listing, status }} isOwner canModerate={false} />);

    const labels = ["Marcar como reservado", "Quitar reserva", "Marcar como finalizado"];
    expect(labels.filter((name) => screen.queryByRole("button", { name }))).toEqual(expected);
  });

  it("un administrador que no es el autor no ve los botones de estado", () => {
    render(<ListingActions listing={listing} isOwner={false} canModerate />);

    expect(screen.queryByRole("button", { name: "Marcar como reservado" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Marcar como finalizado" })).toBeNull();
  });

  it("finalizar pide confirmación y cancelar no llama a la acción", async () => {
    render(<ListingActions listing={listing} isOwner canModerate={false} />);

    await userEvent.click(screen.getByRole("button", { name: "Marcar como finalizado" }));
    expect(screen.getByRole("dialog", { name: "¿Marcar este anuncio como finalizado?" })).toBeTruthy();
    await userEvent.click(screen.getByRole("button", { name: "Cancelar" }));

    expect(changeListingStatus).not.toHaveBeenCalled();
  });
});
