import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("../actions", () => ({ requestAccess: vi.fn() }));

import { MembershipAction } from "./MembershipAction";

const id = "0b5c4a7e-1d2f-4c3b-9a8e-7f6d5c4b3a21";

describe("MembershipAction", () => {
  it("sin membresía: botón «Solicitar acceso» con el id", () => {
    const { container } = render(<MembershipAction communityId={id} status={undefined} />);

    expect(screen.getByRole("button", { name: "Solicitar acceso" })).toBeTruthy();
    expect(container.querySelector<HTMLInputElement>("input[name=community_id]")?.value).toBe(id);
  });

  it("pendiente", () => {
    render(<MembershipAction communityId={id} status="pending" />);

    expect(screen.getByText("Solicitud pendiente")).toBeTruthy();
    expect(screen.queryByRole("button")).toBeNull();
  });

  it("aprobada: enlace «Entrar»", () => {
    render(<MembershipAction communityId={id} status="approved" />);

    expect(screen.getByRole("link", { name: "Entrar" }).getAttribute("href")).toBe(`/comunidades/${id}`);
  });

  it.each([undefined, "pending", "rejected", "blocked"] as const)("platform_admin (%s): enlace «Entrar»", (status) => {
    render(<MembershipAction communityId={id} status={status} isPlatformAdmin />);

    expect(screen.getByRole("link", { name: "Entrar" }).getAttribute("href")).toBe(`/comunidades/${id}`);
    expect(screen.queryByRole("button")).toBeNull();
  });

  it.each(["rejected", "blocked"] as const)("%s: acceso no disponible", (status) => {
    render(<MembershipAction communityId={id} status={status} />);

    expect(screen.getByText("Acceso no disponible")).toBeTruthy();
  });
});
