import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeAll, describe, expect, it } from "vitest";

import { ListingGallery } from "./ListingGallery";

const images = [
  { asset_id: "a1", url: "/v1/media/a1", is_cover: false },
  { asset_id: "a2", url: "/v1/media/a2", is_cover: true },
  { asset_id: "a3", url: "/v1/media/a3", is_cover: false },
];

const main = () => screen.getByRole("img", { name: /Bici, imagen/ });

// jsdom no implementa los diálogos modales.
beforeAll(() => {
  HTMLDialogElement.prototype.showModal = function showModal() {
    this.setAttribute("open", "");
  };
  HTMLDialogElement.prototype.close = function close() {
    this.removeAttribute("open");
  };
});

async function openLightbox() {
  await userEvent.click(screen.getByRole("button", { name: /Ampliar imagen/ }));
  const dialog = screen.getByRole("dialog", { name: "Fotografías de Bici" });
  const image = () => dialog.querySelector("img")!;
  return { dialog, image };
}

describe("ListingGallery", () => {
  it("empieza por la portada y cambia con las miniaturas", async () => {
    render(<ListingGallery title="Bici" images={images} />);

    expect(main().getAttribute("src")).toBe("/media/a2");
    await userEvent.click(screen.getByRole("button", { name: "Imagen 3 de 3" }));

    expect(main().getAttribute("src")).toBe("/media/a3");
    expect(main().getAttribute("alt")).toBe("Bici, imagen 3 de 3");
    expect(screen.getByRole("button", { name: "Imagen 3 de 3" }).getAttribute("aria-pressed")).toBe("true");
  });

  it("flechas del teclado, de forma circular", () => {
    render(<ListingGallery title="Bici" images={images} />);
    const gallery = screen.getByRole("group", { name: "Fotografías de Bici" });

    fireEvent.keyDown(gallery, { key: "ArrowRight" });
    expect(main().getAttribute("src")).toBe("/media/a3");
    fireEvent.keyDown(gallery, { key: "ArrowRight" });
    expect(main().getAttribute("src")).toBe("/media/a1");
    fireEvent.keyDown(gallery, { key: "ArrowLeft" });
    expect(main().getAttribute("src")).toBe("/media/a3");
  });

  it("sin imágenes", () => {
    render(<ListingGallery title="Bici" images={[]} />);

    expect(screen.getByText("Sin fotografías")).toBeTruthy();
  });

  it("pulsar la imagen la abre a pantalla completa y se cierra con «Cerrar»", async () => {
    render(<ListingGallery title="Bici" images={images} />);

    const { dialog, image } = await openLightbox();

    expect(dialog.hasAttribute("open")).toBe(true);
    expect(image().getAttribute("src")).toBe("/media/a2");
    expect(dialog.textContent).toContain("2 / 3");
    await userEvent.click(screen.getByRole("button", { name: "Cerrar" }));
    expect(dialog.hasAttribute("open")).toBe(false);
  });

  it("en el visor, botones y flechas del teclado cambian de imagen (también en la galería)", async () => {
    render(<ListingGallery title="Bici" images={images} />);
    const { dialog, image } = await openLightbox();

    await userEvent.click(screen.getByRole("button", { name: "Imagen siguiente" }));
    expect(image().getAttribute("src")).toBe("/media/a3");
    await userEvent.click(screen.getByRole("button", { name: "Imagen siguiente" }));
    expect(image().getAttribute("src")).toBe("/media/a1");
    fireEvent.keyDown(dialog, { key: "ArrowLeft" });
    expect(image().getAttribute("src")).toBe("/media/a3");
    await userEvent.click(screen.getByRole("button", { name: "Imagen anterior" }));
    expect(image().getAttribute("src")).toBe("/media/a2");
    expect(dialog.hasAttribute("open")).toBe(true);

    fireEvent.keyDown(dialog, { key: "ArrowRight" });
    await userEvent.click(screen.getByRole("button", { name: "Cerrar" }));
    expect(main().getAttribute("src")).toBe("/media/a3");
  });

  it("deslizar a izquierda o derecha cambia de imagen; un movimiento corto, no", async () => {
    render(<ListingGallery title="Bici" images={images} />);
    const { dialog, image } = await openLightbox();
    const stage = image().parentElement!;
    const swipe = (from: number, to: number) => {
      fireEvent.pointerDown(stage, { pointerId: 1, pointerType: "touch", clientX: from, clientY: 100 });
      fireEvent.pointerMove(stage, { pointerId: 1, pointerType: "touch", clientX: to, clientY: 100 });
      fireEvent.pointerUp(stage, { pointerId: 1, pointerType: "touch", clientX: to, clientY: 100 });
    };

    swipe(300, 100);
    expect(image().getAttribute("src")).toBe("/media/a3");
    swipe(100, 300);
    expect(image().getAttribute("src")).toBe("/media/a2");
    swipe(100, 120);
    expect(image().getAttribute("src")).toBe("/media/a2");
    expect(dialog.hasAttribute("open")).toBe(true);
  });

  it("con una sola imagen, el visor no tiene flechas", async () => {
    render(<ListingGallery title="Bici" images={[images[0]]} />);
    await openLightbox();

    expect(screen.queryByRole("button", { name: "Imagen siguiente" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Imagen anterior" })).toBeNull();
  });
});
