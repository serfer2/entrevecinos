import { describe, expect, it } from "vitest";

import { conflictCode, membersPath, rowActions } from "./members";

const me = "u-admin";

describe("rowActions", () => {
  it.each([
    [{ status: "approved", role: "member", userId: "u1" }, ["bloquear", "expulsar"]],
    [{ status: "blocked", role: "member", userId: "u1" }, ["desbloquear", "expulsar"]],
    [{ status: "pending", role: "member", userId: "u1" }, "solicitud"],
    [{ status: "rejected", role: "member", userId: "u1" }, ["expulsar"]],
    [{ status: "approved", role: "community_admin", userId: "u2" }, []],
    [{ status: "approved", role: "member", userId: me }, []],
  ] as const)("%o → %o", (member, expected) => {
    expect(rowActions(member, me)).toEqual(expected);
  });
});

describe("conflictCode", () => {
  it.each([
    ["La comunidad debe tener al menos un administrador.", "ultimo-admin"],
    ["No se puede bloquear a un administrador de la comunidad.", "admin"],
    ["No puedes cambiar el estado de tu propia membresía.", "propio"],
    ["Cambio de estado no permitido.", "no-permitido"],
    [null, "error"],
  ])("%s → %s", (detail, code) => {
    expect(conflictCode(detail)).toBe(code);
  });
});

describe("membersPath", () => {
  it("construye la URL con parámetros", () => {
    expect(membersPath("c1")).toBe("/comunidades/c1/gestion/miembros");
    expect(membersPath("c1", { estado: "bloqueado", page: "2" })).toBe(
      "/comunidades/c1/gestion/miembros?estado=bloqueado&page=2",
    );
  });
});
