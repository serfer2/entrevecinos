import { describe, expect, it } from "vitest";

import { buildCsp, originOf } from "./csp";

const options = { nonce: "abc123", storageOrigin: "http://localhost:9000" };
const https = { nonce: "abc123", storageOrigin: "https://media.example.com" };

describe("buildCsp", () => {
  it("producción: nonce sin unsafe-* y con upgrade-insecure-requests", () => {
    const csp = buildCsp({ ...https, isDev: false });

    expect(csp).toContain("script-src 'self' 'nonce-abc123' 'strict-dynamic'");
    expect(csp).toContain("style-src 'self' 'nonce-abc123'");
    expect(csp).toContain("img-src 'self' data: https://media.example.com");
    expect(csp).toContain("connect-src 'self';");
    expect(csp).toContain("object-src 'none'");
    expect(csp).toContain("frame-ancestors 'none'");
    expect(csp).toContain("upgrade-insecure-requests");
    expect(csp).not.toContain("unsafe");
  });

  it("producción con almacenamiento http (prueba local): sin upgrade-insecure-requests", () => {
    const csp = buildCsp({ ...options, isDev: false });

    expect(csp).toContain("img-src 'self' data: http://localhost:9000");
    expect(csp).not.toContain("upgrade-insecure-requests");
  });

  it("desarrollo: unsafe-eval, estilos en línea y ws: para la recarga", () => {
    const csp = buildCsp({ ...options, isDev: true });

    expect(csp).toContain("'unsafe-eval'");
    expect(csp).toContain("style-src 'self' 'unsafe-inline'");
    expect(csp).toContain("connect-src 'self' ws:");
    expect(csp).not.toContain("upgrade-insecure-requests");
  });
});

describe("originOf", () => {
  it("se queda solo con el origen", () => {
    expect(originOf("https://cdn.example.com/bucket/path?x=1")).toBe("https://cdn.example.com");
    expect(originOf("http://localhost:9000")).toBe("http://localhost:9000");
  });

  it("falla si falta o no es una URL", () => {
    expect(() => originOf(undefined)).toThrow("STORAGE_PUBLIC_URL");
    expect(() => originOf("no es una url")).toThrow();
  });
});
