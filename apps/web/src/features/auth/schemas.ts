import { z } from "zod";

export const SIGNUP_MESSAGES = {
  full_name: "Introduce tu nombre.",
  full_name_max: "Máximo 120 caracteres.",
  email: "Introduce un correo electrónico válido.",
  password: "La contraseña debe tener al menos 12 caracteres.",
  password_max: "Máximo 128 caracteres.",
  phone: "Máximo 32 caracteres.",
} as const;

/** Mismas reglas que `RegisterRequest` en la API. */
export const signupSchema = z.object({
  full_name: z
    .string()
    .trim()
    .min(1, { error: SIGNUP_MESSAGES.full_name })
    .max(120, { error: SIGNUP_MESSAGES.full_name_max }),
  email: z
    .string()
    .trim()
    .max(320, { error: SIGNUP_MESSAGES.email })
    .pipe(z.email({ error: SIGNUP_MESSAGES.email })),
  password: z
    .string()
    .min(12, { error: SIGNUP_MESSAGES.password })
    .max(128, { error: SIGNUP_MESSAGES.password_max }),
  phone: z
    .string()
    .trim()
    .max(32, { error: SIGNUP_MESSAGES.phone })
    .transform((value) => value || null),
});

export type SignupField = keyof z.input<typeof signupSchema>;
export type SignupInput = z.output<typeof signupSchema>;

/** Mensaje mostrado cuando la API rechaza un campo con 422. */
export const SIGNUP_FIELD_MESSAGES: Record<SignupField, string> = {
  full_name: SIGNUP_MESSAGES.full_name,
  email: SIGNUP_MESSAGES.email,
  password: SIGNUP_MESSAGES.password,
  phone: SIGNUP_MESSAGES.phone,
};

/** Primer error de cada campo. */
export function fieldErrorsOf<F extends string>(error: z.ZodError): Partial<Record<F, string>> {
  const errors: Partial<Record<F, string>> = {};
  for (const issue of error.issues) {
    const field = issue.path[0] as F;
    errors[field] ??= issue.message;
  }
  return errors;
}
