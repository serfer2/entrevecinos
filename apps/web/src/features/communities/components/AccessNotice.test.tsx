import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("../actions", () => ({ requestAccess: vi.fn() }));

import type { ApiMyMembership, MembershipStatus } from "../types";
import { AccessNotice } from "./AccessNotice";

function membership(status: MembershipStatus): ApiMyMembership {
  return {
    community: {
      id: "c1",
      name: "Los Olivos",
      description: null,
      postal_code: null,
      city: null,
      is_active: true,
      created_at: "2026-11-09T10:00:00Z",
    } as ApiMyMembership["community"],
    role: "member",
    status,
    requested_at: "2026-11-09T10:00:00Z",
    joined_at: null,
  };
}

describe("AccessNotice", () => {
  it("con la solicitud pendiente explica que la administración la revisará y avisará por correo", () => {
    render(<AccessNotice communityId="c1" membership={membership("pending")} />);

    expect(screen.getByRole("status").textContent).toBe(
      "Hemos enviado tu solicitud a la administración de la comunidad, que la revisará. Te avisaremos por correo cuando la apruebe.",
    );
  });

  it.each(["rejected", "blocked"] as const)("con la membresía %s no da acceso", (status) => {
    render(<AccessNotice communityId="c1" membership={membership(status)} />);

    expect(screen.getByRole("status").textContent).toBe("No tienes acceso a esta comunidad.");
  });

  it("sin membresía ofrece solicitar el acceso", () => {
    render(<AccessNotice communityId="c1" membership={undefined} />);

    expect(screen.getByText("Solicita el acceso para ver y publicar anuncios.")).toBeTruthy();
  });
});
