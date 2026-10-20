import { beforeEach, describe, expect, it, vi } from "vitest";

const { userApiFetch, requireUser } = vi.hoisted(() => ({
  userApiFetch: vi.fn(),
  requireUser: vi.fn(),
}));

vi.mock("@/features/auth/api", () => ({ userApiFetch }));
vi.mock("@/features/auth/dal", () => ({ requireUser }));

import { uploadImage } from "./actions";

function form(file: File | string) {
  const data = new FormData();
  data.set("file", file);
  return data;
}

const png = () => new File([new Uint8Array(100)], "foto.png", { type: "image/png" });

describe("uploadImage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    requireUser.mockResolvedValue({ id: "u1" });
  });

  it("reenvía el fichero como multipart y devuelve el id", async () => {
    userApiFetch.mockResolvedValue({ ok: true, status: 201, data: { id: "a1", url: "/v1/media/a1" } });

    expect(await uploadImage(form(png()))).toEqual({ id: "a1" });
    const [path, options] = userApiFetch.mock.calls[0];
    expect(path).toBe("/media");
    expect(options.method).toBe("POST");
    expect((options.body as FormData).get("file")).toBeInstanceOf(File);
  });

  it("rechaza en el servidor de Next los ficheros grandes o de otro tipo", async () => {
    const big = new File([new Uint8Array(5 * 1024 * 1024 + 1)], "a.jpg", { type: "image/jpeg" });
    const pdf = new File(["%PDF"], "a.jpg", { type: "application/pdf" });

    expect(await uploadImage(form(big))).toEqual({ error: "La imagen supera 5 MB." });
    expect(await uploadImage(form(pdf))).toEqual({ error: "Formato no permitido. Usa JPEG, PNG o WebP." });
    expect(await uploadImage(form("texto"))).toEqual({ error: "Formato no permitido. Usa JPEG, PNG o WebP." });
    expect(userApiFetch).not.toHaveBeenCalled();
  });

  it.each([
    [413, "La imagen supera 5 MB."],
    [415, "Formato no permitido. Usa JPEG, PNG o WebP."],
    [0, "No se pudo subir la imagen. Inténtalo de nuevo."],
  ])("traduce el error %i de la API", async (status, error) => {
    userApiFetch.mockResolvedValue({ ok: false, error: { status, detail: null } });

    expect(await uploadImage(form(png()))).toEqual({ error });
  });
});
