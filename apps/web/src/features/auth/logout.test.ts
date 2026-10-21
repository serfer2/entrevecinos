import { beforeEach, describe, expect, it, vi } from "vitest";

const { cookieDelete, redirect } = vi.hoisted(() => ({
  cookieDelete: vi.fn(),
  redirect: vi.fn((url: string) => {
    throw new Error(`NEXT_REDIRECT:${url}`);
  }),
}));

vi.mock("@/lib/api/server", () => ({ apiFetch: vi.fn() }));
vi.mock("next/headers", () => ({ cookies: async () => ({ delete: cookieDelete }) }));
vi.mock("next/navigation", () => ({ redirect }));

import { logout } from "./actions";

describe("logout", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("borra la cookie de sesión y redirige a la raíz", async () => {
    await expect(logout()).rejects.toThrow("NEXT_REDIRECT:/");

    expect(cookieDelete).toHaveBeenCalledWith({ name: "ev_session", path: "/" });
  });
});
