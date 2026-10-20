import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { ListingGallery } from "./ListingGallery";

const images = [
  { asset_id: "a1", url: "/v1/media/a1", is_cover: false },
  { asset_id: "a2", url: "/v1/media/a2", is_cover: true },
  { asset_id: "a3", url: "/v1/media/a3", is_cover: false },
];

const main = () => screen.getByRole("img", { name: /Bici, imagen/ });

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
});
