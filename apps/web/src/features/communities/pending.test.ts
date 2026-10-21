import { describe, expect, it } from "vitest";

import { pendingCommunityOf } from "./pending";
import type { ApiMyMembership } from "./types";

function membership(id: string, createdBy: string, isActive: boolean): ApiMyMembership {
  return {
    community: {
      id,
      name: `Comunidad ${id}`,
      description: null,
      postal_code: null,
      city: null,
      created_by: createdBy,
      is_active: isActive,
      created_at: "2026-10-21T10:00:00Z",
    },
    role: "community_admin",
    status: "approved",
    requested_at: "2026-10-21T10:00:00Z",
    joined_at: "2026-10-21T10:00:00Z",
  };
}

describe("pendingCommunityOf", () => {
  it("no encuentra nada sin membresías", () => {
    expect(pendingCommunityOf([], "u1")).toBeUndefined();
  });

  it("encuentra la comunidad inactiva que creó el usuario", () => {
    const memberships = [membership("c1", "u1", true), membership("c2", "u1", false)];

    expect(pendingCommunityOf(memberships, "u1")?.id).toBe("c2");
  });

  it("ignora las comunidades activas y las inactivas de otros creadores", () => {
    const memberships = [membership("c1", "u1", true), membership("c2", "u2", false)];

    expect(pendingCommunityOf(memberships, "u1")).toBeUndefined();
  });
});
