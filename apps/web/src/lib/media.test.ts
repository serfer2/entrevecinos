import { describe, expect, it } from "vitest";

import { imageFileError, mediaSrc } from "./media";

describe("mediaSrc", () => {
  it("traduce la URL de la API a la ruta de Next", () => {
    expect(mediaSrc("/v1/media/abc")).toBe("/media/abc");
    expect(mediaSrc("abc")).toBe("/media/abc");
  });
});

describe("imageFileError", () => {
  it.each([
    [{ size: 100, type: "image/png" }, null],
    [{ size: 5 * 1024 * 1024, type: "image/webp" }, null],
    [{ size: 5 * 1024 * 1024 + 1, type: "image/jpeg" }, "La imagen supera 5 MB."],
    [{ size: 100, type: "application/pdf" }, "Formato no permitido. Usa JPEG, PNG o WebP."],
    [{ size: 100, type: "image/gif" }, "Formato no permitido. Usa JPEG, PNG o WebP."],
  ])("%o → %s", (file, error) => {
    expect(imageFileError(file)).toBe(error);
  });
});
