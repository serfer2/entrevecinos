import { act, render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { ImagePicker } from "./ImagePicker";

const ids = ["0b5c4a7e-1d2f-4c3b-9a8e-7f6d5c4b3a21", "1c6d5b8f-2e3a-4d4c-8b9f-8a7e6d5c4b32", "2d7e6c9a-3f4b-4e5d-9c0a-9b8f7e6d5c43"];

const png = (name: string, size = 100) => new File([new Uint8Array(size)], name, { type: "image/png" });

function hiddenIds(container: HTMLElement) {
  return Array.from(container.querySelectorAll<HTMLInputElement>("input[name=image_asset_ids]")).map((i) => i.value);
}

describe("ImagePicker", () => {
  it("sube cada fichero en serie y muestra la portada", async () => {
    let n = 0;
    const upload = vi.fn(async () => ({ id: ids[n++] }));
    const { container } = render(<ImagePicker upload={upload} />);

    await userEvent.upload(screen.getByLabelText("Añadir fotografías"), [png("a.png"), png("b.png")]);

    await screen.findByText("Portada");
    expect(upload).toHaveBeenCalledTimes(2);
    expect(hiddenIds(container)).toEqual([ids[0], ids[1]]);
    expect(screen.getByAltText("Fotografía 1").getAttribute("src")).toBe(`/media/${ids[0]}`);
  });

  it("reordena y quita", async () => {
    const { container } = render(<ImagePicker upload={vi.fn()} initialIds={ids} />);

    await userEvent.click(screen.getByRole("button", { name: "Subir fotografía 3" }));
    expect(hiddenIds(container)).toEqual([ids[0], ids[2], ids[1]]);

    await userEvent.click(screen.getByRole("button", { name: "Bajar fotografía 1" }));
    expect(hiddenIds(container)).toEqual([ids[2], ids[0], ids[1]]);
    expect(screen.getByRole("button", { name: "Subir fotografía 1" }).hasAttribute("disabled")).toBe(true);

    await userEvent.click(screen.getByRole("button", { name: "Quitar fotografía 1" }));
    expect(hiddenIds(container)).toEqual([ids[0], ids[1]]);
  });

  it("muestra el error del fichero sin subirlo", async () => {
    const upload = vi.fn();
    render(<ImagePicker upload={upload} />);

    await userEvent.upload(screen.getByLabelText("Añadir fotografías"), png("grande.png", 5 * 1024 * 1024 + 1));

    const item = (await screen.findByText("grande.png")).closest("li")!;
    expect(within(item).getByText("La imagen supera 5 MB.")).toBeTruthy();
    expect(upload).not.toHaveBeenCalled();
  });

  it("muestra el error devuelto por la subida", async () => {
    render(<ImagePicker upload={vi.fn(async () => ({ error: "Formato no permitido. Usa JPEG, PNG o WebP." }))} />);

    await userEvent.upload(screen.getByLabelText("Añadir fotografías"), png("falso.png"));

    expect(await screen.findByText("Formato no permitido. Usa JPEG, PNG o WebP.")).toBeTruthy();
  });

  it("como mucho 10 fotografías", async () => {
    const existing = Array.from({ length: 9 }, (_, i) => `0b5c4a7e-1d2f-4c3b-9a8e-7f6d5c4b3a${String(i).padStart(2, "0")}`);
    const upload = vi.fn(async () => ({ id: ids[0] }));
    const { container } = render(<ImagePicker upload={upload} initialIds={existing} />);

    await act(() => userEvent.upload(screen.getByLabelText("Añadir fotografías"), [png("a.png"), png("b.png")]));

    await screen.findByText("Puedes adjuntar hasta 10 fotografías.");
    expect(upload).toHaveBeenCalledTimes(1);
    expect(hiddenIds(container)).toHaveLength(10);
  });
});
