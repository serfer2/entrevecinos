import { describe, expect, it } from "vitest";

import { formatLongDate } from "./dates";

describe("formatLongDate", () => {
  it("usa la fecha de Madrid", () => {
    expect(formatLongDate("2026-10-19T23:30:00Z")).toBe("20 de octubre de 2026");
  });
});
