import { describe, expect, it } from "vitest";

import { fieldErrorsOf } from "@/features/auth/schemas";

import { PROFILE_MESSAGES, profileSchema } from "./schemas";

function errorsFor(input: { full_name?: string; phone?: string }) {
  const result = profileSchema.safeParse({ full_name: "Alex", phone: "", ...input });
  return result.success ? {} : fieldErrorsOf(result.error);
}

describe("profileSchema", () => {
  it("recorta y convierte el teléfono vacío en null", () => {
    expect(profileSchema.parse({ full_name: "  Alex ", phone: "   " })).toEqual({
      full_name: "Alex",
      phone: null,
    });
  });

  it.each(["600111222", "+34 600 111 222", "(91) 555-12-34"])("acepta el teléfono %s", (phone) => {
    expect(profileSchema.parse({ full_name: "Alex", phone }).phone).toBe(phone);
  });

  it.each([
    [{ full_name: "" }, { full_name: PROFILE_MESSAGES.full_name }],
    [{ full_name: "   " }, { full_name: PROFILE_MESSAGES.full_name }],
    [{ full_name: "x".repeat(121) }, { full_name: PROFILE_MESSAGES.full_name_max }],
    [{ phone: "llámame" }, { phone: PROFILE_MESSAGES.phone }],
    [{ phone: "12345" }, { phone: PROFILE_MESSAGES.phone }],
    [{ phone: "1".repeat(33) }, { phone: PROFILE_MESSAGES.phone }],
  ])("rechaza %o", (input, expected) => {
    expect(errorsFor(input)).toEqual(expected);
  });
});
