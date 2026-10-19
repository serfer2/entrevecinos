import { describe, expect, it } from "vitest";

import { fieldErrorsOf, SIGNUP_MESSAGES, signupSchema } from "./schemas";

const valid = {
  full_name: "Alex Vecino",
  email: "vecino@example.com",
  password: "UnaClaveSegura123!",
  phone: "",
};

function errorsFor(input: Partial<typeof valid>) {
  const result = signupSchema.safeParse({ ...valid, ...input });
  return result.success ? {} : fieldErrorsOf(result.error);
}

describe("signupSchema", () => {
  it("acepta datos válidos, recorta el nombre y convierte el teléfono vacío en null", () => {
    const result = signupSchema.parse({ ...valid, full_name: "  Alex  " });

    expect(result.full_name).toBe("Alex");
    expect(result.phone).toBeNull();
  });

  it("conserva el teléfono informado", () => {
    expect(signupSchema.parse({ ...valid, phone: " +34600111222 " }).phone).toBe("+34600111222");
  });

  it.each([
    [{ full_name: "" }, "full_name", SIGNUP_MESSAGES.full_name],
    [{ full_name: "   " }, "full_name", SIGNUP_MESSAGES.full_name],
    [{ full_name: "x".repeat(121) }, "full_name", SIGNUP_MESSAGES.full_name_max],
    [{ email: "no-es-correo" }, "email", SIGNUP_MESSAGES.email],
    [{ email: `${"x".repeat(310)}@example.com` }, "email", SIGNUP_MESSAGES.email],
    [{ password: "corta" }, "password", SIGNUP_MESSAGES.password],
    [{ password: "x".repeat(129) }, "password", SIGNUP_MESSAGES.password_max],
    [{ phone: "1".repeat(33) }, "phone", SIGNUP_MESSAGES.phone],
  ])("rechaza %o", (input, field, message) => {
    expect(errorsFor(input)).toEqual({ [field]: message });
  });
});
