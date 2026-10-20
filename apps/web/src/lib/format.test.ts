import { describe, expect, it } from "vitest";

import { formatPrice, formatPublishedAt } from "./format";

const nbsp = (text: string | null) => text?.replace(/ /g, " ");

describe("formatPrice", () => {
  it("formatea en euros al estilo español", () => {
    expect(nbsp(formatPrice(45.5, "EUR"))).toBe("45,50 €");
    expect(nbsp(formatPrice(1200, "EUR"))).toBe("1200,00 €");
    expect(formatPrice(null, null)).toBeNull();
  });
});

describe("formatPublishedAt", () => {
  const now = new Date("2026-10-20T10:00:00Z");

  it.each([
    ["2026-10-20T08:00:00Z", "hoy"],
    ["2026-10-19T08:00:00Z", "ayer"],
    ["2026-10-17T08:00:00Z", "hace 3 días"],
    ["2026-10-12T08:00:00Z", "12 oct"],
    ["2025-03-02T08:00:00Z", "2 mar 2025"],
  ])("%s → %s", (iso, expected) => {
    expect(formatPublishedAt(iso, now).replace(".", "")).toBe(expected);
  });

  it("usa el día de Madrid", () => {
    // 23:30 UTC del 19 es ya el día 20 en Madrid.
    expect(formatPublishedAt("2026-10-19T23:30:00Z", now)).toBe("hoy");
  });
});
