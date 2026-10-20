import { describe, expect, it } from "vitest";

import { safeNextPath } from "./redirect";

describe("safeNextPath", () => {
  it.each(["/inicio", "/comunidades/1/anuncios?page=2", "/perfil#datos"])("acepta %s", (value) => {
    expect(safeNextPath(value)).toBe(value);
  });

  it.each([
    "//evil.example",
    "https://evil.example",
    "/\\evil.example",
    "\\\\evil.example",
    "javascript:alert(1)",
    "/\tevil",
    "",
    "inicio",
    undefined,
    null,
    ["/inicio"],
  ])("rechaza %o", (value) => {
    expect(safeNextPath(value)).toBeNull();
  });
});
