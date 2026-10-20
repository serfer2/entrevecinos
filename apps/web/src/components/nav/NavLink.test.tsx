import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

const { usePathname } = vi.hoisted(() => ({ usePathname: vi.fn() }));
vi.mock("next/navigation", () => ({ usePathname }));

import { NavLink } from "./NavLink";

describe("NavLink", () => {
  beforeEach(() => usePathname.mockReset());

  it("marca la ruta actual con aria-current", () => {
    usePathname.mockReturnValue("/perfil");
    render(<NavLink href="/perfil">Mi perfil</NavLink>);

    expect(screen.getByRole("link", { name: "Mi perfil" }).getAttribute("aria-current")).toBe("page");
  });

  it("marca las subrutas de su sección", () => {
    usePathname.mockReturnValue("/comunidades/123");
    render(
      <NavLink href="/comunidades/nueva" section="/comunidades">
        Comunidades
      </NavLink>,
    );

    expect(screen.getByRole("link").getAttribute("aria-current")).toBe("page");
  });

  it("no marca otras rutas", () => {
    usePathname.mockReturnValue("/inicio");
    render(<NavLink href="/perfil">Mi perfil</NavLink>);

    expect(screen.getByRole("link").getAttribute("aria-current")).toBeNull();
  });
});
