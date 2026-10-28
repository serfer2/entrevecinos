import { describe, expect, it } from "vitest";

import { canAccessCommunity, canManageCommunity } from "./access";

const user = { platform_role: "user" } as const;
const admin = { platform_role: "platform_admin" } as const;

describe("canAccessCommunity", () => {
  it("un vecino necesita la membresía aprobada", () => {
    expect(canAccessCommunity(user, { status: "approved", role: "member" })).toBe(true);
    expect(canAccessCommunity(user, { status: "pending", role: "member" })).toBe(false);
    expect(canAccessCommunity(user, undefined)).toBe(false);
  });

  it("un platform_admin entra sin membresía o con la solicitud pendiente", () => {
    expect(canAccessCommunity(admin, undefined)).toBe(true);
    expect(canAccessCommunity(admin, { status: "pending", role: "member" })).toBe(true);
  });
});

describe("canManageCommunity", () => {
  it("un vecino necesita ser community_admin aprobado", () => {
    expect(canManageCommunity(user, { status: "approved", role: "community_admin" })).toBe(true);
    expect(canManageCommunity(user, { status: "approved", role: "moderator" })).toBe(false);
    expect(canManageCommunity(user, { status: "pending", role: "community_admin" })).toBe(false);
  });

  it("un platform_admin gestiona cualquier comunidad", () => {
    expect(canManageCommunity(admin, undefined)).toBe(true);
  });
});
